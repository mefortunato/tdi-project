import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly
from bokeh.plotting import figure, output_file, show, output_notebook
from bokeh.embed import components
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

symbols_url = 'https://api.iextrading.com/1.0/ref-data/symbols'
chart_url = 'https://api.iextrading.com/1.0/stock/{ticker}/chart/5y'
company_url = 'https://api.iextrading.com/1.0/stock/{ticker}/company'
logo_url = 'https://api.iextrading.com/1.0/stock/{ticker}/logo'
news_url = 'https://api.iextrading.com/1.0/stock/{ticker}/news/last/5'

@app.route('/', methods=['GET', 'POST'])
def index():
    div = ''
    script = ''
    ticker = ''
    company = ''
    logo = ''
    news = []
    
    if request.method == 'POST':
        today = datetime.today()
        ticker = request.form.get('ticker')
        start_date = request.form.get('start-date', today.strftime('%Y-%m-%d'))
        end_date = request.form.get('end-date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
        resp = requests.get(chart_url.format(ticker=ticker))
        if resp.status_code == 200:
          df = pd.DataFrame(data=json.loads(resp.text))
          df['date'] = pd.to_datetime(df['date'])
          df = df.set_index('date')
          x = df.index.values.astype(str)
          y = df['close']
          div = plotly.offline.plot(
              {
                  'data': [
                      {'x': x, 'y': y, 'name': 'close'},
                  ],
                  'layout': {
                      'margin': {
                        'l': 100,
                        'r': 100,
                        't': 10,
                        'b': 100,
                        'pad': 4
                      },
                      'xaxis': {
                          'title': 'Date',
                          'showgrid': False,
                          'showline': True,
                          'linecolor': 'black',
                          'linewidth': 2,
                          'mirror': True
                      },
                      'yaxis': {
                          'title': 'Closing Price',
                          'showgrid': False,
                          'showline': True,
                          'linecolor': 'black',
                          'linewidth': 2,
                          'mirror': True
                      },
                  }
              }, output_type='div', include_plotlyjs=False, config={'showLink': False})
          resp = requests.get(company_url.format(ticker=ticker))
          company = json.loads(resp.text).get('companyName', '')
          resp = requests.get(logo_url.format(ticker=ticker))
          logo = json.loads(resp.text).get('url', '')
          resp = requests.get(news_url.format(ticker=ticker))
          news = json.loads(resp.text)
        else:
          company = 'Error: Cannot query ticker symbol: {ticker}'.format(ticker=ticker)
    return render_template('index.html', div=div, ticker=ticker, company=company, logo=logo, news=news)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=5000)
