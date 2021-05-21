from typing import List
from fastapi import Depends, APIRouter, Path
from sqlalchemy.orm import Session

from nstrend.dependency import get_db
from nstrend import crud, schemas

router = APIRouter()

#@router.get("/all/", response_model=List[schemas.Trend])
#async def get_trend(db: Session = Depends(get_db)):
#    trends = crud.get_trend(db)
#    return trends

@router.get("/code/{code}", response_model=List[schemas.Trend])
async def get_trend_by_codes(
        code:str = Path(..., 
                        title="Query Google Trend by stock codes",
                        description=""" Query Google Trend by stock codes.
                                        The API will return near 3 months Goolgle Trend data.
                                        If you want to request multiple stocks,
                                        just seperate stock codes seperated by ','.
                                        Ex: 2317,2330,3481
                                    """

                    ), 
        db: Session = Depends(get_db)
    ):
    code_ls = code.split(',')
    trends = crud.get_trend_by_codes(db, code_ls)
    return trends

@router.get("/date/{date}", response_model=List[schemas.Trend])
async def get_trend_by_date(
        date:str = Path(..., 
                        title="Query Google Trend by date",
                        description=""" Query Google Trend by date.
                                        The API will return Google Trend data of all 
                                        TSE stocks on specific date.
                                    """

                    ),  
        db: Session = Depends(get_db)
    ):
    trends = crud.get_trend_by_date(db, date)
    return trends
