# smarttrade
In this project, we are writing python functions to pick stocks based on defined selection criteria on a daily basis. Then run a simulation to trade the selected stocks and see whether or not the strategy work.


**Current selection criteria inlclude:**    
  1. Volume > 50000.     
  2. close t > close t-1.  
  3. RSI t-1 < 30 & RSI t > 30.  
  4. MACD t-1 < signal t-1 & MACD t > signal t.  


**Prerequisites to run the program:**
1. Download a list of NASDAQ stock symbols from https://www.nasdaq.com/market-activity/stocks/screener as 'nasdaq_screener.csv' to the project folder. To visualize data in the downloaded sccreener, I also built this interactive Tableau dashboard: https://public.tableau.com/app/profile/zhenhui.trinh/viz/NASDAQStockScreenerAnalysis/IPOTrend_1
2. Make sure all the required packages are installed by simply running the below command in your terminal.

  ``` 
  pip3 install -r requirements.txt --user
  ```

