import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from utils import get_single_ticker_info

import logging

if __name__ == '__main__':
    screen_dir = './picks/'
    record_dir = './records/'

    logname = record_dir + './log.txt'
    logging.basicConfig(filename=logname,
                                filemode='a',
                                format='%(asctime)s,%(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.INFO)

    date = datetime.today().strftime('%Y-%m-%d')

    if not os.path.exists(record_dir):
        os.mkdir(record_dir)

    # Iinitial fund if not portfolio exist
    if not os.path.isfile(record_dir + 'portfolio.csv'):
        portfolio = list()
        security = dict()
        security['name'] = 'USD'
        security['market value'] = 1000000
        security['current price'] = None
        security['quantity'] = None
        security['cost'] = None
        security['open_date'] = None
        portfolio.append(security)
        portfolio_df = pd.DataFrame(portfolio, columns=security.keys())
        portfolio_df.to_csv(record_dir + 'portfolio.csv', index=False)

    ## read profolio
    portfolio_df = pd.read_csv(record_dir + 'portfolio.csv')
    portfolio = portfolio_df.to_dict(orient='records')

    fund = float(portfolio_df.loc[portfolio_df['name']=='USD']['market value'])

    ## update existing positions
    portfolio_update = list()
    for security in portfolio:
        keep_position = False
        if security['name'] == 'USD':
            continue
        name = security['name']
        cost = security['cost']
        ticker_info = get_single_ticker_info(name)
        #columns = ['ticker', 'close t', 'volume t', 'RSI t', 'MACD t', 'signal t', 
        #          'close t-1', 'volume t-1', 'RSI t-1', 'MACD t-1', 'signal t-1']

        current_price = ticker_info[1]

        # conditions for selling
        # stop loss
        if current_price < cost:
            loss_ratio = (current_price - cost)/cost
            if loss_ratio > 0.1:
                print('sell {} at a loss: {}%'.format(name, loss_ratio*100))
                logging.info('sell {} at a loss: {}%'.format(name, loss_ratio*100))
                fund += current_pice * security['quantity']
            else: 
                keep_position = True
        # stop gain
        if current_price >= cost:
            gain_ratio = (current_price - cost)/cost
            if gain_ratio > 0.15:
                print('sell {} at a gain: {}%'.format(name, gain_ratio*100))
                logging.info('sell {} at a gain: {}%'.format(name, gain_ratio*100))
                fund += current_pice * security['quantity']
            else: 
                keep_position = True
        # rsi kill
        rsi = ticker_info[3]
        if rsi >= 60:
            change_ratio = (current_price - cost)/cost
            print('rsi indicates overbought, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            logging.info('rsi indicates overbought, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            fund += current_pice * security['quantity']
        else: 
            keep_position = True
        # price drop kill
        previous_price = ticker_info[6]
        price_change = (current_price - previous_price)/previous_price
        if price_change < - 0.05:
            change_ratio = (current_price - cost)/cost
            print('great price drop in one day, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            logging.info('great price drop in one day, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            fund += current_pice * security['quantity']
        else: 
            keep_position = True
        # inactive kill
        current_date = datetime.strptime(date, '%Y-%m-%d')
        open_date = datetime.strptime(security['open_date'], '%Y-%m-%d')
        days_past = current_date - open_date
        if int(days_past.days) > 5:
            change_ratio = (current_price - cost)/cost
            print('no change for a long period, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            logging.info('no change for a long period, sell {} at a gain/loss: {}%'.format(name, change_ratio*100))
            fund += current_pice * security['quantity']
        else: 
            keep_position = True
            
        # no update
        if keep_position:
            print('{} position no change'.format(name))
            security['current price'] = current_price
            security['market value'] = current_price * security['quantity']
            portfolio_update.append(security)

    ## open new positions
    # Today's picks
    picks_df = pd.read_csv(screen_dir + 'macd.csv')
    picks_df = picks_df.sort_values(by=['volume t'], ascending=False)
    picks = picks_df.to_dict(orient='records')

    #only keep the top 5 volumes
    if len(picks) > 5:
        picks = picks[:5]
    to_open = len(picks)

    if fund > 0:
        if len(picks) > 0:
            fund_each = fund/to_open
            # update fund
            security = dict()
            security['name'] = 'USD'
            security['market value'] = 0
            security['current price'] = None
            security['quantity'] = None
            security['cost'] = None
            security['open_date'] = None
            portfolio_update.append(security)
            # update securities
            for ticker in picks:
                name = ticker['ticker']
                price = ticker['close t']
                shares = fund_each/price
                
                security = dict()
                security['name'] = name
                security['market value'] = fund_each
                security['current price'] = price
                security['quantity'] = shares
                security['cost'] = price
                security['open_date'] = date
                portfolio_update.append(security)

                print('open position: {} shares of {} on {}'.format(shares, name, date))
        else:
            security = dict()
            security['name'] = 'USD'
            security['market value'] = fund
            security['current price'] = None
            security['quantity'] = None
            security['cost'] = None
            security['open_date'] = None
            portfolio_update.append(security)
            print('No new positions today, avaliable fund {}'.format(fund))
    else:
        security = dict()
        security['name'] = 'USD'
        security['market value'] = 0
        security['current price'] = None
        security['quantity'] = None
        security['cost'] = None
        security['open_date'] = None
        portfolio_update.append(security)
        print('Not enough fund to open new positions')
    portfolio_df = pd.DataFrame(portfolio_update, columns=portfolio[0].keys())
    total_value = sum(portfolio_df['market value'])
    print('Total market value on {}: {}'.format(date, total_value))
    with open (record_dir + 'total_value.txt', 'a') as f:
        f.write('{}:{}\n'.format(date, total_value))

    # write updated portfolio
    if os.path.isfile(record_dir + 'portfolio.csv'):
        os.remove(record_dir + 'portfolio.csv')
    portfolio_df.to_csv(record_dir + 'portfolio.csv'.format(date), index=False)
