# smarttrade
This is a personal project: writing python functions to pick stocks based on defined selection criteria on a daily basis. Then run a simulation to trade the selected stocks and see whether or not the strategy work.

In order to run the program, we need to go to https://www.nasdaq.com/market-activity/stocks/screener and download the list of stocks listed in NASDAQ first.

Current selection criteria are:    
  1. Volume > 50000.     
  2. close t > close t-1.  
  3. RSI t-1 < 30 & RSI t > 30.  
  4. MACD t-1 < signal t-1 & MACD t > signal t.  
