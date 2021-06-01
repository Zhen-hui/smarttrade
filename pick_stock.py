import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt
import dateutil.relativedelta
from tqdm import tqdm

from utils import get_ticker_record, compute_rsi, compute_macd, get_single_ticker_info

import warnings
warnings.filterwarnings('ignore')

nasdaq_screener = pd.read_csv('nasdaq_screener.csv')

ticker_lst = nasdaq_screener['Symbol'].tolist()

all_tickers = list()

for ticker in tqdm(ticker_lst[:50]):
    single_ticker_info = get_single_ticker_info(ticker)
    if single_ticker_info is not None:
        all_tickers.append(single_ticker_info)
        
columns = ['ticker', 'close t', 'volume t', 'RSI t', 'MACD t', 'signal t', 
           'close t-1', 'volume t-1', 'RSI t-1', 'MACD t-1', 'signal t-1']

df = pd.DataFrame(all_tickers, columns = columns)

# 1. close t > close t-1
df_close = df.loc[df['close t'] > df['close t-1']]
df_close.to_csv("df_close.csv")

# 2. RSI t-1 < 30 & RSI t > 30
df_rsi = df_close.loc[(df_close['RSI t-1'] < 30) & (df_close['RSI t'] > 30)]
df_rsi.to_csv("df_rsi.csv")

# 3. MACD t-1 < signal t-1 & MACD t > signal t
df_macd = df_rsi.loc[(df_rsi['MACD t-1'] < df_rsi['signal t-1']) & (df_rsi['MACD t'] > df_rsi['signal t'])]
df_macd.to_csv("df_macd.csv")