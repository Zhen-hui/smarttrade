import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt
import dateutil.relativedelta

import warnings
warnings.filterwarnings('ignore')

MIN_VOLUME = 50000

def get_ticker_record(ticker):
    today = dt.datetime.today().strftime('%Y-%m-%d')
    previous_date = dt.datetime.today() - dateutil.relativedelta.relativedelta(months=3)
    previous_date = previous_date.strftime('%Y-%m-%d')

    """
    df = pdr.get_data_yahoo(ticker, previous_date, today)
    """
    df = yf.Ticker(ticker).history(start=previous_date, end=today)
    return df


def compute_rsi(ticker_record):
    df = ticker_record
    if not 'Adj Close' in df:
        df['Adj Close'] = df['Close']
    ## Compute 14_Day RSI
    df['Up Move'] = np.nan
    df['Down Move'] = np.nan
    df['Average Up'] = np.nan
    df['Average Down'] = np.nan
    # Relative Strength
    df['RS'] = np.nan
    # Relative Strength Index
    df['RSI'] = np.nan
    ## Calculate Up Move & Down Move
    for x in range(1, len(df)):
        df['Up Move'][x] = 0
        df['Down Move'][x] = 0

        if df['Adj Close'][x] > df['Adj Close'][x-1]:
            df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]

        if df['Adj Close'][x] < df['Adj Close'][x-1]:
            df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  

    ## Calculate initial Average Up & Down, RS and RSI
    df['Average Up'][14] = df['Up Move'][1:15].mean()
    df['Average Down'][14] = df['Down Move'][1:15].mean()
    df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
    df['RSI'][14] = 100 - (100/(1+df['RS'][14]))
    ## Calculate rest of Average Up, Average Down, RS, RSI
    for x in range(15, len(df)):
        df['Average Up'][x] = (df['Average Up'][x-1]*13+df['Up Move'][x])/14
        df['Average Down'][x] = (df['Average Down'][x-1]*13+df['Down Move'][x])/14
        df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
        df['RSI'][x] = 100 - (100/(1+df['RS'][x]))
    return df


def compute_macd(ticker_record):
    ## Calculate the MACD and Signal Line indicators
    ## Calculate the Short Term Exponential Moving Average

    df = ticker_record

    ShortEMA = df.Close.ewm(span=12, adjust=False).mean() 

    ## Calculate the Long Term Exponential Moving Average

    LongEMA = df.Close.ewm(span=26, adjust=False).mean() 

    ## Calculate the Moving Average Convergence/Divergence (MACD)

    MACD = ShortEMA - LongEMA

    ## Calcualte the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()
    
    df['MACD'] = MACD
    df['signal'] = signal
    
    return df

def get_single_ticker_info(ticker, filter_volume=True):
    
    try:
        ticker_record = get_ticker_record(ticker)
        if filter_volume  and ticker_record['Volume'][-1] < MIN_VOLUME:
            return None
        ticker_record = compute_rsi(ticker_record)
        ticker_record = compute_macd(ticker_record)
        ticker_record

        single_ticker_info = list()
        # ticker name
        single_ticker_info.append(ticker)
        # today's close
        single_ticker_info.append(ticker_record['Close'][-1])
        # today's volume
        single_ticker_info.append(ticker_record['Volume'][-1])
        # today's rsi
        single_ticker_info.append(ticker_record['RSI'][-1])
        # today's macd
        single_ticker_info.append(ticker_record['MACD'][-1])
        # today's macd signal
        single_ticker_info.append(ticker_record['signal'][-1])

        # yestoday's close
        single_ticker_info.append(ticker_record['Close'][-2])
        # yestoday's volume
        single_ticker_info.append(ticker_record['Volume'][-2])
        # yestoday's rsi
        single_ticker_info.append(ticker_record['RSI'][-2])
        # yestoday's macd
        single_ticker_info.append(ticker_record['MACD'][-2])
        # yestoday's macd signal
        single_ticker_info.append(ticker_record['signal'][-2])

        return single_ticker_info
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    ticker = 'BB'

    ticker_info = get_single_ticker_info(ticker)
    #ticker_info = get_ticker_record(ticker)
    #ticker_info = yf.Ticker(ticker).history(period='3mo')

    print(ticker_info)
