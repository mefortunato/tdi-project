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
#url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker={ticker}&date.gte={start_date}&date.lte={end_date}&api_key=PyewNKgseooV1caGxUtG'
url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker={ticker}&api_key=PyewNKgseooV1caGxUtG'

@app.route('/', methods=['GET', 'POST'])
def index():
    div = ''
    script = ''
    ticker = ''
    if request.method == 'POST':
        today = datetime.today()
        ticker = request.form.get('ticker')
        start_date = request.form.get('start-date', today.strftime('%Y-%m-%d'))
        end_date = request.form.get('end-date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
        resp = requests.get(url.format(ticker=ticker, start_date=start_date, end_date=end_date))
        res = json.loads(resp.text)['datatable']
        df = pd.DataFrame(columns=[c['name'] for c in res['columns']], data=res['data']).drop(columns='ticker')
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        x = df.index.values.astype(str)
        y = df['close']
        y_high = df['high']
        div = plotly.offline.plot(
            {
                'data': [
                    {'x': x, 'y': y, 'name': 'close'},
                ],
                'layout': {
                    'title': ticker,
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
            }, output_type='div', include_plotlyjs=False)
        #p = figure(x_axis_label='Date', y_axis_label='Closing Price', x_axis_type="datetime")
        #p.line(x, y, line_width=2)
        #script, div = components(p)
    return render_template('index.html', script=script, div=div, ticker=ticker)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=5000)
