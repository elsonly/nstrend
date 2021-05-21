# nstrend(Beta) - Google Trend on Taiwan Stock Market
nstrend crawls [Google Trend](https://trends.google.com/trends/) data of Taiwan Stock and run server base on fastapi - SQLAlchemy.


Note that there serveral limits due to Google Trend constraint.
1. It takes abouts 10 minutes to crawl Google Trend data of all TSE stocks since there is a rate limit. It can be accelerated by using high quality proxies.
2. Google Trend data is not static, since only a sample of Google searches are used in Google Trends.

>While only a sample of Google searches are used in Google Trends, this is sufficient because we handle billions of searches per day. Providing access to the entire data set would be too large to process quickly. By sampling data, we can look at a dataset representative of all Google searches, while finding insights that can be processed within minutes of an event happening in the real world.

3. nstrend data may not be the same as Google Trend.
Since Google Trend only allow *5* topics per each request. And still, Google Trend normalizes data between 0 and 100 in each request. In other words, we will get different values in each request although one of the topic is fixed in each request.
However, we still can make it comparable by using the values from fixed topic.

## How to Use it
Run api server
```bash
uvicorn nstrend.main:app --reload
```

## API Methods
* Get Google Trend by stock codes  
The API will return near 3 months Goolgle Trend data.
If you want to request multiple stocks,
just seperate stock codes seperated by ' , '.
Ex: 2317,2330,3481

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/trend/code/2317%2C%202330%2C%3481' \
  -H 'accept: application/json'
```

* Get Google Trend by date  
The API will return Google Trend data of all 
TSE stocks on specific date.
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/trend/date/20210517' \
  -H 'accept: application/json'
```
