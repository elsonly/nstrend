import pandas as pd
import numpy as np
import os
import time
from pytrends.request import TrendReq
from datetime import datetime

from nstrend.database import SessionLocal
from nstrend.models import Trend, Stock
from nstrend.logger import get_logger
from nstrend.crawl.taiex import StockListCrawler
logger = get_logger('crawler')

class TrendCrawler:
    def __init__(self, controller:str, n_topics:int=5, timeframe_ls:list=[],
            stockType:int=1, proxy_ls:list=[]):
        """
        parameters
        ______________
        @controller:str, Used to be sent to google trend api
                        as one of topics in each request.
        @n_topics:int, number of topics in each request, n_topics should be 
                        beween 2 and 5
        @timeframe_ls:list, available timeframe: 
                            'today 1-m', 'today 3-m', 'today 12-m',
                            'now 1-d', 'now 7-d',
                            'now 1-H', 'now 4-H'
        @stockType:int, 1:上市, 2:上櫃, 3:興櫃一般板, 0:上市, 上櫃, 興櫃一般板
        @proxy_ls:list
        """
        if n_topics>5 or n_topics<2:
            raise ValueError("n_topics should be betweend 2 and 5")

        self.controller = controller
        self.n_topics = n_topics
        self.proxy_ls = proxy_ls
        self.timeframe_ls = timeframe_ls
        self.stockType = stockType

    def _request(self, kw_list:list, timeframe:str='today 3-m') -> pd.DataFrame:
        """
        Google Trend is not static data, which means data is 
        inconsistent through timeframe and (topic?).
        @timeframe start_date + ' ' + end_date, today 3-m , now 4-H
        """
        logger.debug(f"Crawling: {kw_list}")
        
        params_pytrend = {
            'hl':'zh-TW',
            'tz':-480,
        }
        if self.proxy_ls:
            params_pytrend['requests_args'] = {'verify':False},
            params_pytrend['proxies'] = self.proxy_ls
            params_pytrend['timeout'] = (5, 10)
            params_pytrend['retries'] = 2
            params_pytrend['backoff_factor'] = 0.1

        params_payload = {
            'kw_list':kw_list,
            'cat':784, #Business News
            'timeframe':timeframe, 
            'geo':'TW',
            'gprop':'',
        }
        while True:
            try:
                pytrends = TrendReq(**params_pytrend)
                pytrends.build_payload(**params_payload)
                results = pytrends.interest_over_time()

                return results
            except:
                logger.debug('Crawling: Error, Wait 60 secs')
                time.sleep(60)
    
    def request(self, kw_list:list, timeframe:str ='today 3-m') -> list:
        logger.info("Start to Request Data from Goole Trend")
        
        trend_ls = []
        if self.proxy_ls:
            batch_size = len(self.proxy_ls) * self.n_topics
        else:
            batch_size = self.n_topics

        n_stocks = len(kw_list)
        for k in range(0, n_stocks, batch_size-1):
            logger.info(f"Crawling {k}/{n_stocks}")
            stocks_ls = kw_list[k:k+batch_size-1]
            #controller check
            if self.controller in stocks_ls:
                stocks_ls.remove(self.controller)
            stocks_ls.append(self.controller)

            result = self._request(stocks_ls, timeframe)

            if not self.proxy_ls:
                time.sleep(5)
                
            if type(result) == pd.DataFrame:
                logger.debug(f"Results: {result.columns[:-1].tolist()}")
            else:
                logger.debug(f"Results: {result}")
            trend_ls.append(result)

        return trend_ls
  
    def generate_comparable_data(self, raw_trend_ls:list):
        """
        Function will scrape all elements in stk_list from Google Trend API, 
        concatenate each request and make them comparible.

        Since Google Trend API only allow "5" topics per each request, which means
        we cannot get comparible data in one request. And still, Google Trend API
        scales data between 0 and 100 in each request. In other words, we will get 
        different numbers if we compare one topic to the other 2 sets of topics.
        Here, the function will overlap one element in each requests and adjust main 
        dataframe to make it comparible.
        """
        trend_ls = [x.iloc[:, :-1].copy() for x in raw_trend_ls]
        for i in range(1, len(trend_ls)):
            df_prv = trend_ls[i-1]
            df = trend_ls[i]
            
            #Adjusted Factor
            if df.iloc[:, -1].max() * df_prv.iloc[:, -1].max() > 0:
                adjFactor = df_prv.iloc[:, -1].max() / df.iloc[:, -1].max()
                df *= adjFactor
            
        #Concat DataFrame
        concat_ls = [x.iloc[:, :-1] for x in trend_ls[:-1]]
        concat_ls.append(trend_ls[-1])
        df = pd.concat(concat_ls, axis=1)
        df /= df.max().max()
        df *= 100
        
        return df

    def loadStocks(self, stockType:int)->pd.DataFrame:
        """
        @stockType:int, 0:上市, 上櫃, 1:上市, 2:上櫃, 3:興櫃一般板
        """
        query_ls = []

        stockCols = []
        if stockType in [0, 1]:
            query_ls.append('上市')
        if stockType in [0, 2]:
            query_ls.append('上櫃')
        if stockType in [0, 3]:
            query_ls.append('興櫃一般板')

        
        s = SessionLocal()
        df_ls = []
        for ipo_type in query_ls:
            df = pd.read_sql(s.query(Stock).filter(Stock.ipo_type==ipo_type).statement, s.bind)
            df_ls.append(df)
        s.close()

        df = pd.concat(df_ls, axis=0).reset_index(drop=True)
        return df

    def df2db(self, trend_df:pd.DataFrame, 
            stock_df:pd.DataFrame, 
            timeframe:str='today 3-m', 
            table:str='google_trend'
            ):
        logger.info('Insert Google Trend Data to DB')

        s = SessionLocal()
        if table == 'google_trend':
            code_mapping = {row['name']:str(row['code']) for _, row in stock_df.iterrows()}
            s.query(Trend).filter(Trend.active == True).update({Trend.active:False}, synchronize_session=True)
            s.commit()
            for col in trend_df.columns:
                code = code_mapping[col]
                try:
                    data_ls = [Trend(code=code, 
                                    tdate=idx, 
                                    timeframe=timeframe,
                                    trend=val,
                                    active=True
                                    ) 
                                for idx, val in trend_df[col].iteritems()
                            ]
                    s.add_all(data_ls)
                    s.commit()
                except:
                    s.rollback()
                    up_date = s.query(Trend).order_by(Trend.up_date.desc()).first().up_date
                    for idx, val in trend_df[col].iteritems():
                        data = Trend(code=code, tdate=idx, timeframe=timeframe,
                                    trend=val,active=True) 
                        s.query(Trend).filter(
                                Trend.code==code, 
                                Trend.tdate==idx, 
                                Trend.timeframe==timeframe,
                                Trend.up_date==up_date
                                ).delete()
                        s.add(data)
                    s.commit()

        else:
            raise ValueError("Invalid table")
    
        s.close()

    def run(self, stockType:int, timeframe:str='today 3-m'):
        self._stock_df = self.loadStocks(stockType=1)
        self._trend_ls = self.request(
                                kw_list=self._stock_df['name'].tolist(),
                                timeframe=timeframe,
                            )

        self._trend_df = self.generate_comparable_data(self._trend_ls)
        self.df2db(self._trend_df, self._stock_df)

    def autocheck(self):
        s = SessionLocal()
        stock_data = s.query(Stock).first()
        trend_data = s.query(Trend).order_by(Trend.up_date.desc()).first()
        s.close()
        
        if not stock_data or \
                (datetime.now().date() - stock_data.up_date).days > 30:
            logger.info("Update Stock List")
            slc = StockListCrawler()
            slc.run()

        if not trend_data or \
                (datetime.now().date() - trend_data.up_date).days > 0:
            logger.info("Update Google Trend Data")
            for timeframe in self.timeframe_ls:
                self.run(stockType=self.stockType, timeframe=timeframe)

if __name__ == '__main__':
    timeframe_ls=['today 3-m']
    tc = TrendCrawler(controller='台積電', n_topics=5, timeframe_ls=timeframe_ls, stockType=1)
    #tc.loadStocks(stockType=1)
    for timeframe in timeframe_ls:
        tc.run(stockType=1, timeframe=timeframe)
    