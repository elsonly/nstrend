import pandas as pd
import json
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Query, Path
from fastapi import status, HTTPException
from pydantic import BaseModel

from logger import Logger
from google_trend import TrendScraper
from taiex import StockListScaper

logger = Logger().get_main_logger()
# get google trend data
ts = TrendScraper()
trend_df = ts.get_trend_data()

# get tw stock list
sls = StockListScaper()
stock_df = sls.get_stk_list()
code_map_dict = {str(x):str(y) for (x,y) in zip(stock_df['code'], stock_df['name'].str.replace('-KY', ''))}

app = FastAPI()

@app.get("/trend/{code}")
async def get_stock_trend(
    code: str = Path(..., title="Stock Code", max_length=4, min_length=4),
    start_date: str = Query(..., title="Start Date"),
    end_date: str = Query(..., title="End Date"),
):
    if code in code_map_dict:
        stk_name = code_map_dict[code]
    else:
        raise HTTPException(status_code=404, detail="Code Not Found")
    
    if stk_name not in trend_df.columns:
        raise HTTPException(status_code=404, detail="Code(name) Not Found")

    df = trend_df.loc[start_date:end_date, stk_name]
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Date Range Need to be in near 3 months")

    return df.to_json(force_ascii=False, orient='split', index=False)

@app.get("/trend_all/")
async def get_all_stocks_trend(
    start_date: Optional[str] = Query(None, title="Start Date"),
    end_date: Optional[str] = Query(None, title="End Date"),
):
    df = trend_df.loc[start_date:end_date]
    if df.empty:
        raise HTTPException(status_code=404, detail="Date Range Need to be in near 3 months")

    return df.to_json(force_ascii=False, orient='split', index=False)
