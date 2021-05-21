from pydantic import BaseModel
from datetime import date

class Trend(BaseModel):
    code: str
    tdate: date
    timeframe: str
    trend: float

    class Config:
        orm_mode = True
