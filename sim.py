import os
import pandas as pd

if __name__ = '__main__':
    screen_dir = './picks/'
    record_dir = './records/'

    # Today's picks
    picks = pd.read_csv(screen_dir + 'macd.csv')

    if not os.path.is_file(record_dir + 'portfolio.csv'):
        # create initial prorfolio
        portfolio = dict()
        portfolio['cash'] = 100000

    # read profolio
    protfolio = pd.read_csv(record_dir + 'portfolio.csv')

    # close positions
    for security in protfolio:
        if profolio is not 'cash':
            ticker = security

    # open positions
    if (picks is not None) and (protfolio['cash']) > 0:
        for pick in picks:
            ticker = pick['ticker']
                
        
        
