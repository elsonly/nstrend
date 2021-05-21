import requests
import pandas as pd
from datetime import datetime
import os

from nstrend.database import SessionLocal
from nstrend.models import Stock
from nstrend.logger import get_logger
logger = get_logger('crawler')

class StockListCrawler:

    def request(self) -> pd.DataFrame:
        df_list = []
        header = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Connection':'keep-alive',
            'Host':'isin.twse.com.tw',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        }
        strMode_mapping = {2:'上市', 4:'上櫃', 5:'興櫃'}
        for strMode in [2, 4, 5]:
            logger.info(f"Request {strMode_mapping[strMode]} stock list")

            url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={strMode}"
            res = requests.get(url, headers=header)
            df = pd.read_html(res.text)[0]
            df.columns = df.iloc[0, :].tolist()
            df = df.loc[df.iloc[:, -2] == 'ESVUFR']
            df_tmp = df.iloc[:, 0].str.replace('\u3000', ' ').str.split(' ', expand=True)
            df = pd.concat((df_tmp, df.iloc[:, 2:-2]), axis=1)
            df.columns = ['code', 'name', 'ipo_date', 'type', 'ind']
            df_list.append(df)                

        return pd.concat(df_list).reset_index(drop=True)

    def preprocessing(self, df):
        #Exclude keywords -KY
        df['name'] = df['name'].str.replace('-KY', '')
        df.drop_duplicates(['name'], inplace=True)

    def df2db(self, df:pd.DataFrame, table:str='stock_basic'):
        s = SessionLocal()
        if table == 'stock_basic':
            for _, row in df.iterrows():
                s.query(Stock).filter(Stock.code==row['code']).delete()
                data = Stock(code=str(row['code']), 
                                name=str(row['name']), 
                                ipo_date=pd.to_datetime(row['ipo_date']),
                                ipo_type=str(row['type']),
                                industry=str(row['ind'])
                                ) 
                s.add(data)
            s.commit()
            s.close()
        else:
            raise ValueError("Invalid table")
        s.close()

    def run(self):
        df = self.request()
        self.preprocessing(df)
        self.df2db(df)
    
if __name__ == '__main__':
    slc = StockListCrawler()
    slc.run()
