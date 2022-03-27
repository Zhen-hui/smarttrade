import pandas as pd
import multiprocessing as mp
import os
import time
from tqdm import tqdm

from utils import get_ticker_record, compute_rsi, compute_macd, get_single_ticker_info

import warnings

MULTI_PROCESS = False
DELAY = 1.6

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    out_dir = 'picks/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    file_lst = os.listdir(out_dir)
    if len(file_lst) != 0:
        for old_file in file_lst:
            os.remove(out_dir + old_file)

    nasdaq_screener = pd.read_csv('nasdaq_screener.csv')

    ticker_lst = nasdaq_screener['Symbol'].tolist()

    all_tickers = list()


    if MULTI_PROCESS:
        pool = mp.Pool(mp.cpu_count())

        all_tickers = tqdm(pool.imap(get_single_ticker_info, ticker_lst))
        all_tickers = list(filter(None, all_tickers))

    else:
        for ticker in tqdm(ticker_lst):
            start = time.process_time()
            single_ticker_info = get_single_ticker_info(ticker)
            if single_ticker_info is not None:
                all_tickers.append(single_ticker_info)
            end = time.process_time()
            if (end-start) < DELAY:
                time.sleep(DELAY-(end-start))
            
    columns = ['ticker', 'close t', 'volume t', 'RSI t', 'MACD t', 'signal t', 
               'close t-1', 'volume t-1', 'RSI t-1', 'MACD t-1', 'signal t-1']

    df = pd.DataFrame(all_tickers, columns = columns)

    # 0. filter by volume
    df_vol = df.loc[df['volume t'] > 50000]
    #df_vol = df # volume has been filtered in screener
    df_vol.to_csv(out_dir + "volume.csv", index=False)

    # 1. close t > close t-1
    df_close = df_vol.loc[df['close t'] > df['close t-1']]
    df_close.to_csv(out_dir + "close.csv", index=False)

    # 2. RSI t-1 < 30 & RSI t > 30
    df_rsi = df_close.loc[(df_close['RSI t-1'] < 30) & (df_close['RSI t'] > 30)]
    df_rsi.to_csv(out_dir + "rsi.csv", index=False)

    # 3. MACD t-1 < signal t-1 & MACD t > signal t
    df_macd = df_rsi.loc[(df_rsi['MACD t-1'] < df_rsi['signal t-1']) & (df_rsi['MACD t'] > df_rsi['signal t'])]
    df_macd.to_csv(out_dir + "macd.csv", index=False)
