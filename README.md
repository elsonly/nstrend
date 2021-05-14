# nstrend(Beta) - Google Trend on Taiwan Stock Market
nstrend will scrape google trend data of Taiwan Stock and
run server base on fastapi.

# How to Use it
```bash
uvicorn main:app --app-dir nstrend --reload
```

# API Methods
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

