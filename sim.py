import os
import pandas as pd
import yfinance as yf
from datetime import datetime

if __name__ == '__main__':
    screen_dir = './picks/'
    record_dir = './records/'

    date = datetime.today().strftime('%Y-%m-%d')

    if not os.path.exists(record_dir):
        os.mkdir(record_dir)

    if not os.path.isfile(record_dir + 'portfolio.csv'):
        # create initial prorfolio
        portfolio = list()
        security = dict()
        security['name'] = 'USD'
        security['value'] = 100000.0
        security['quantity'] = None
        security['cost'] = None
        security['open_date'] = None
        portfolio.append(security)
        portfolio_df = pd.DataFrame(portfolio, columns=security.keys())
        portfolio_df.to_csv(record_dir + 'portfolio.csv', index=False)

    # read profolio
    portfolio_df = pd.read_csv(record_dir + 'portfolio.csv')
    portfolio = portfolio_df.to_dict(orient='records')

    # TODO :update and close positions
    for security in portfolio:
        if security['name'] != 'USD':
            ticker = security['name']

    # open positions
    # Today's picks
    picks_df = pd.read_csv(screen_dir + 'macd.csv')
    picks_df = picks_df.sort_values(by=['volume t'], ascending=False)
    picks = picks_df.to_dict(orient='records')

    #only keep the top 5 volumes
    if len(picks) > 5:
        picks = picks[:5]
    to_open = len(picks)
    fund = float(portfolio_df.loc[portfolio_df['name']=='USD']['value'])

    print(portfolio)
    portfolio = list()
    if fund > 0 and len(picks) > 0:
        fund_each = fund/to_open

        # update fund
        security = dict()
        security['name'] = 'USD'
        security['value'] = 0
        security['quantity'] = None
        security['cost'] = None
        security['open_date'] = None
        portfolio.append(security)
        # update securities
        for pick in picks:
            ticker = yf.Ticker(pick['ticker']).info
            price = ticker['regularMarketPrice']
            shares = fund_each/price
            
            security = dict()
            security['name'] = pick['ticker']
            security['value'] = fund_each
            security['quantity'] = shares
            security['cost'] = price
            security['open_date'] = date
            portfolio.append(security)

            print('open position: {} shares of {} on {}'.format(shares, pick['ticker'], date))
    portfolio_df = pd.DataFrame(portfolio, columns=portfolio[0].keys())
    portfolio_df.to_csv(record_dir + 'portfolio_{}.csv'.format(date), index=False)
