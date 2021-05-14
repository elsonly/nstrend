import requests
import pandas as pd
from datetime import datetime
import os

from logger import Logger

class StockListScaper:
    def __init__(self):
        self.base_path = './nstrend/data/'
        logger = Logger()
        self.logger = logger.get_scrape_logger()

    def get_stk_list(self):
        filename = 'stock_list.csv'
        filedir = self.base_path + filename
        if not os.path.exists(filedir) or \
                (datetime.now() - datetime.fromtimestamp(os.path.getmtime(filedir))).days > 30 :
            df = self.request_stk_list()
            df.to_csv(filedir, index=False)

        else:
            return pd.read_csv(filedir)

        
    def request_stk_list(self):
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
            self.logger.info(f"Request {strMode_mapping[strMode]} stock list")

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
    
if __name__ == '__main__':
    sls = StockListScaper()
    df = sls.get_stk_list()