# nstrend(Beta) - Google Trend on Taiwan Stock Market
nstrend will scrape google trend data of Taiwan Stock and 
run server base on fastapi.
Note that there serveral limits due to Google Trend API constraint.
1. It takes abouts 10 minutes to scrape trend data since there is 
a rate limit. It cannot be solved by using proxies.
2. Date range only availible near 3 months. 
Google Trend is not static data, which means data is inconsistent 
with timeframe and (topic?). Data with different date range from google api 
is not comparible. Note that if data is incosistent with topic, this module
will become useless(Check).
3. nstrend data may not be the same as Google Trend.
Since Google Trend API only allow "5" topics per each request, which means
we cannot get comparible data in one request. And still, Google Trend API
scales data between 0 and 100 in each request. In other words, we will get 
different numbers if we compare one topic to the other 2 sets of topics.
Here, nstrend will overlap one element in each requests and adjust main 
dataframe to make it comparible.

## How to Use it
Run api server
```bash
uvicorn main:app --reload
```

## API Methods
* Get stock Google Trend Data
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/trend/2330?start_date=2021-03-05&end_date=2021-05-13' \
  -H 'accept: application/json'
```

* Get TW market Google Trend Data
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/trend_all/?start_date=2021-03-14&end_date=2021-05-13' \
  -H 'accept: application/json'
```

