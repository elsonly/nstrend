from typing import List
from sqlalchemy.orm import Session
from nstrend.models import Trend
from datetime import datetime
#from nstrend import schemas -> for create

def get_trend_by_date(db: Session, tdate: str): 
    if '/' in tdate:
        format_ = '%Y/%m/%d'
    elif '-' in tdate:
        format_ = '%Y-%m-%d'
    else:
        format_ = '%Y%m%d'

    date = datetime.strptime(tdate, format_).date()
    return db.query(Trend).filter(Trend.tdate==date, Trend.active==True).all()

def get_trend_by_codes(db: Session, code_ls: List[str]):
    return db.query(Trend).filter(Trend.code.in_(code_ls), Trend.active==True).all()

def get_trend(db: Session):
    return db.query(Trend).filter(Trend.active==True).all()

