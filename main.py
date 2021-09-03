import requests
import datetime as dt
import os
from twilio.rest import Client

STOCK = 'EDIT'
COMPANY_NAME = 'Editas Medicine'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH = os.environ.get('TWILIO_AUTH')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH)
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
NEWS_END_POINT = 'https://newsapi.org/v2/everything'
news_parameters = {
    'q': COMPANY_NAME,
    'apikey': NEWS_API_KEY,
    'sortBy': 'popularity',
}
AV_API_KEY = os.environ.get('AV_API_KEY')
AV_END_POINT = 'https://www.alphavantage.co/query'
av_parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': AV_API_KEY,
    'outputsize': 'compact',
}
sign: 'str'

today = dt.date.today()
yesterday = today - dt.timedelta(days=1)
before_yesterday = today - dt.timedelta(days=2)

av_response = requests.get(url=AV_END_POINT, params=av_parameters)
av_response.raise_for_status()

data = av_response.json()['Time Series (Daily)']

try:
    close1 = float(data[f'{today}']['4. close'])
except KeyError:
    close1 = float(data[f'{yesterday}']['4. close'])
    close2 = float(data[f'{before_yesterday}']['4. close'])
else:
    close2 = float(data[f'{yesterday}']['4. close'])

diff = ((close1 / close2) - 1) * 100

if abs(diff) > 5:
    news_response = requests.get(url=NEWS_END_POINT, params=news_parameters)
    news_response.raise_for_status()

    news_data = news_response.json()['articles'][:3]
    sign = '📈' if diff > 0 else '📉'

    for item in news_data:
        message = client.messages \
            .create(body=f'{STOCK}: {sign}{int(diff)}%\nHeadline: {item["title"]}\nBrief: {item["description"]}',
                    from_=os.environ.get('FROM_PHONE'),
                    to=os.environ.get('MY_PHONE')
                    )

        print(message.status)
