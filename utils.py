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
    """
    This function returns a dataframe containing the 3-month history of a specific ticker using the yfinance package
    """    
    #today = dt.datetime.today().strftime('%Y-%m-%d') the data 
    today = (dt.datetime.today() + dt.timedelta(days=1)).strftime('%Y-%m-%d') 
    previous_date = dt.datetime.today() - dateutil.relativedelta.relativedelta(months=3)
    previous_date = previous_date.strftime('%Y-%m-%d')

    df = yf.Ticker(ticker).history(start=previous_date, end=today)
    return df


def compute_rsi(ticker_record):
    """
    This function calculates the Relative Strength Index (RSI) of a ticker.
    RSI is a momentum indicator that evaluates overbought or oversold conditions based on changes in stock price. 
    RSI ranges between 0 and 100. Generally an RSI of 70 or more is considered as overbought/overvalued, and an RSI value of 30 or less is considered as oversold/undervalued.
    
    Formula:
    RSI = 100 - 100/(1+RS)
        * RS = average gain/average loss (2 steps in calculating average here)
            * First average gain and average loss are simple 14-day averages
                First Average Gain = Sum of Gains over the past 14 periods / 14
                First Average Loss = Sum of Losses over the past 14 periods / 14
            * The second, and subsequent, calculations are based on the prior averages and the current gain loss:
                Average Gain = (previous Average Gain x 13 + current Gain) / 14
                Average Loss = (previous Average Loss x 13 + current Loss) / 14
    """    

    # Initialize a dataframe to store the values
    df = ticker_record
    if not 'Adj Close' in df:
        df['Adj Close'] = df['Close']
    df['Daily Gain'] = np.nan 
    df['Daily Loss'] = np.nan
    df['Average Gain'] = np.nan 
    df['Average Loss'] = np.nan
    df['RS'] = np.nan  # Relative Strength
    df['RSI'] = np.nan # Relative Strength Index
   
    ## Calculate Daily Gain & Daily Loss
    for x in range(1, len(df)):
        df['Daily Gain'][x] = 0
        df['Daily Loss'][x] = 0
        
        # If close price of date x is higher than that of date (x-1), then it's a gain, calculate the difference
        if df['Adj Close'][x] > df['Adj Close'][x-1]:
            df['Daily Gain'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]
        # If close price of date x is lower than that of date (x-1), then it's a loss, calculate the absolute difference
        if df['Adj Close'][x] < df['Adj Close'][x-1]:
            df['Daily Loss'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  


    ## Calculate initial Average Gain & Average Loss, RS, and RSI
    df['Average Gain'][14] = df['Daily Gain'][1:15].mean()
    df['Average Loss'][14] = df['Daily Loss'][1:15].mean()
    df['RS'][14] = df['Average Gain'][14] / df['Average Loss'][14]
    df['RSI'][14] = 100 - (100/(1+df['RS'][14]))


    ## Calculate rest of Average Gain, Average Loss, RS, and RSI
    ## "Average Gain" and "Average Loss" values are smoothed after the first calculation
    for x in range(15, len(df)):
        df['Average Gain'][x] = (df['Average Gain'][x-1]*13+df['Daily Gain'][x])/14
        df['Average Loss'][x] = (df['Average Loss'][x-1]*13+df['Daily Loss'][x])/14
        df['RS'][x] = df['Average Gain'][x] / df['Average Loss'][x]
        df['RSI'][x] = 100 - (100/(1+df['RS'][x]))


    return df


def compute_macd(ticker_record):
    """
    This function calculates the following:
        - Moving Average Convergence Divergence (MACD): the difference between 26-day and 12-day exponential moving averages (EMA)
        - Signal: a 9-day EMA. A buy signal is triggered when MACD is above the signal, while a sell signal is triggered when MACD is below the signal.
    """

    df = ticker_record

    ## Calculate the Long Term Exponential Moving Average (12-day EMA)
    ShortEMA = df.Close.ewm(span=12, adjust=False).mean() 

    ## Calculate the Long Term Exponential Moving Average (26-day EMA)
    LongEMA = df.Close.ewm(span=26, adjust=False).mean() 

    ## Calculate the Moving Average Convergence/Divergence (MACD)
    MACD = ShortEMA - LongEMA

    ## Calcualte the signal line (9-day EMA)
    signal = MACD.ewm(span=9, adjust=False).mean()
    
    df['MACD'] = MACD
    df['signal'] = signal
    
    return df


def get_single_ticker_info(ticker, filter_volume=True):
    """
    This function returns current and previous days' close price, volume, RSI, MACD, and signal for a select ticker 
    """
    try:
        ticker_record = get_ticker_record(ticker)

        # If the colume of the ticker in both days is lower than our threshold, move to the next ticker without calculating any of the values
        if filter_volume  and ticker_record['Volume'][-1] < MIN_VOLUME:
            return None

        ticker_record = compute_rsi(ticker_record)
        ticker_record = compute_macd(ticker_record)
        ticker_record

        single_ticker_info = list()
        # ticker name
        single_ticker_info.append(ticker)
        # today's close price
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


# Try on one ticker
if __name__ == '__main__':
    ticker = 'RENT'

    ticker_info = get_ticker_record(ticker)
    print(ticker_info)

    ticker_info = get_single_ticker_info(ticker)
    print(ticker_info)
