from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float
from nstrend.database import Base
from datetime import datetime

class Stock(Base):
    __tablename__ = "stock_basic"
    #__table_args__ = {'extend_existing':True}
    
    code = Column(String, primary_key=True, index=True)
    name = Column(String)
    ipo_date = Column(Date)
    ipo_type = Column(String)
    industry = Column(String)
    up_date = Column(Date, default=datetime.now())

class Trend(Base):
    __tablename__ = "google_trend"
    __table_args__ = {'extend_existing':True}

    code = Column(String, ForeignKey('stock_basic.code'), primary_key=True, index=True)
    tdate = Column(Date, index=True, primary_key=True)
    timeframe = Column(String, index=True, primary_key=True)
    trend = Column(Float)
    up_date = Column(Date, default=datetime.now(), primary_key=True)
    active = Column(Boolean, default=False)



if __name__ == '__main__':
    from nstrend.database import engine
    Base.metadata.create_all(bind=engine)
