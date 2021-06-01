import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt
import dateutil.relativedelta
import multiprocessing as mp
import os
from tqdm import tqdm

from utils import get_ticker_record, compute_rsi, compute_macd, get_single_ticker_info

import warnings


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    out_dir = './picks/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    nasdaq_screener = pd.read_csv('nasdaq_screener.csv')

    ticker_lst = nasdaq_screener['Symbol'].tolist()

    all_tickers = list()

    pool = mp.Pool(mp.cpu_count())

    all_tickers = tqdm(pool.imap(get_single_ticker_info, ticker_lst))
    all_tickers = list(filter(None, all_tickers))

    """
    for ticker in tqdm(ticker_lst):
        single_ticker_info = get_single_ticker_info(ticker)
        if single_ticker_info is not None:
            all_tickers.append(single_ticker_info)
    """
            
    columns = ['ticker', 'close t', 'volume t', 'RSI t', 'MACD t', 'signal t', 
               'close t-1', 'volume t-1', 'RSI t-1', 'MACD t-1', 'signal t-1']

    df = pd.DataFrame(all_tickers, columns = columns)

    # 1. close t > close t-1
    df_close = df.loc[df['close t'] > df['close t-1']]
    df_close.to_csv(out_dir + "df_close.csv")

    # 2. RSI t-1 < 30 & RSI t > 30
    df_rsi = df_close.loc[(df_close['RSI t-1'] < 30) & (df_close['RSI t'] > 30)]
    df_rsi.to_csv(out_dir + "df_rsi.csv")

    # 3. MACD t-1 < signal t-1 & MACD t > signal t
    df_macd = df_rsi.loc[(df_rsi['MACD t-1'] < df_rsi['signal t-1']) & (df_rsi['MACD t'] > df_rsi['signal t'])]
    df_macd.to_csv(out_dir + "df_macd.csv")
