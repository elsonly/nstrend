import pandas as pd
import os
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from concurrent.futures import ThreadPoolExecutor, as_completed

from taiex import StockListScaper
from logger import Logger

class TrendScraper:
    def __init__(self):
        logger = Logger()
        self.logger = logger.get_scrape_logger()
        self.filedir = './nstrend/data/trend.csv'
        self.check_update()

    def scrape_trend_batch(self, stk_list:list, start_date:str, end_date:str):
        """
        Google Trend is not static data, which means data is 
        inconsistent through timeframe and (topic?).
        """
        pytrends = TrendReq(hl='zh-TW', tz=-480, proxies=[])
        pytrends.build_payload(
            stk_list
            , cat=784 #Business News
            , timeframe='today 3-m' #start_date + ' ' + end_date #'today 3-m'#'now 4-H'#
            , geo='TW'
            , gprop=''
        )
        
        return pytrends.interest_over_time()

    def scrape_trend(self, stk_list:list, start_date:str, end_date:str, n_batch=5):
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
        n_stock = len(stk_list)
        _stk_list = stk_list[:n_batch]
        
        #Initialize
        self.logger.info("Start to scrape Goole Trend")
        self.logger.info("Scraper hasn't been optimized, it takes about 10 min to scrape data.")
        df = self.scrape_trend_batch(_stk_list, start_date, end_date).iloc[:, :-1]
        for k in range(n_batch+1, n_stock, n_batch-1):
            self.logger.debug(f"scraping {k} - {k+n_batch-1} elements")
            _stk_list = [df.columns[-1]]
            _stk_list.extend(stk_list[k:k+n_batch-1])
            
            df_tmp = self.scrape_trend_batch(_stk_list, start_date, end_date).iloc[:, :-1]
            if df_tmp.empty: #無資料
                self.logger.debug(f"empty data in {k} - {k+n_batch-1} elements")
                continue
            
            #Adjusted Factor
            div = df[_stk_list[0]].max() if df[_stk_list[0]].max() > 0 else 1
            adjFactor = df_tmp[_stk_list[0]].max() / div if df_tmp[_stk_list[0]].max() > 0 else 1
            df *= adjFactor
            
            #Concat DataFrame
            df = pd.concat((df.iloc[:, :-1], df_tmp), axis=1)

        df /= df.max().max()*100
        df.to_csv(self.filedir)
        self.logger.debug("Successfully scrape Goole Trend")
        
    def check_update(self):
        self.logger.info('Check Google Trend data updated')
        if not os.path.exists(self.filedir) or \
                (datetime.now() - datetime.fromtimestamp(os.path.getmtime(self.filedir))).days > 0 :
            self.logger.info('Update Google Trend data...')
            #Get Stock List
            slc = StockListScaper()
            df_stk_list = slc.get_stk_list()
            #Only include '上市', '上櫃'
            df_stk_list = df_stk_list.loc[df_stk_list['type'].isin(['上市', '上櫃'])]
            #Exclude keywords -KY
            df_stk_list['name'] = df_stk_list['name'].str.replace('-KY', '')
            df_stk_list.drop_duplicates(['name'], inplace=True)

            stk_list = df_stk_list['name'].tolist()

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(months=3)).strftime('%Y-%m-%d')
            df = self.scrape_trend(stk_list, start_date, end_date)
        
        else:
            self.logger.info('Google Trend data is the latest')

    def get_trend_data(self):        
        df = pd.read_csv(self.filedir)
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
        #convert to numeric
        for col in df.columns:
            df.loc[:, col] = df.loc[:, col].astype(float)

        return df

if __name__ == '__main__':
    ts = TrendScraper()
    df = ts.get_trend_data()