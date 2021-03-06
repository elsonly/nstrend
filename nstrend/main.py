from fastapi import FastAPI, APIRouter

from nstrend import models
from nstrend.database import engine
from nstrend.crawl.google_trend import TrendCrawler
from nstrend.routers import trend

#Initialize
##database
models.Base.metadata.create_all(bind=engine)
tc = TrendCrawler(controller='台積電', timeframe_ls=['today 3-m'], stockType=1)
tc.autocheck()

##api server
app = FastAPI()

app.include_router(
    trend.router,
    prefix="/trend",
)