# 22.9, -10, 10, 65, 25
first_buy = True
first_buy_str = []
transactions = 0

import talib
from nsepy import get_history
from datetime import date
import pandas as pd
import numpy as np


# important variables for indicators
START_DATE = date(2020, 3, 1)
END_DATE = date.today()
STOCH_INTERVAL_DAYS = 14
STOCH_LOWER_BAND = 40
STOCH_HIGHER_BAND = 70

# date list to traverse through the dictionary
try:
    date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
except AttributeError:
    print("AttributeError1 while fetching data for date_list, wait a while...")
    try:
        date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
    except AttributeError:
        print("AttributeError2 while fetching data for date_list, wait a while...")
        try:
            date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
        except AttributeError:
            print("AttributeError3 while fetching data for date_list, wait a while...")
# gathering NSE top100 ticker's list
ticker_list = pd.read_csv("nifty50_csv.csv")['Symbol'].to_list()  # ['SAIL', 'RELIANCE', 'SUNPHARMA', 'SBIN', 'ITC', 'TATAMOTORS']

# Portfolio Variables
PORTFOLIO = {ticker: 0 for ticker in ticker_list}
INITIAL_AMOUNT = 10000
DEMAT_FUND = 10000
INVESTED_AMOUNT = 0
risk_ema50 = 5


# raw data for each ticker
raw_data_nse100 = {ticker: get_history(ticker, START_DATE, END_DATE) for ticker in ticker_list}

# indicators
#ema50 for every ticker
ema50_nse100 = {}
for ticker in ticker_list:
    try:
        ema50_nse100[ticker] = talib.EMA(raw_data_nse100[ticker]['Close'], 50)
    except:
        print('Error, fetching data for', ticker)

#ema200 for every ticker
ema200_nse100 = {}
for ticker in ticker_list:
    try:
        ema200_nse100[ticker] = talib.EMA(raw_data_nse100[ticker]['Close'], 200)
    except:
        print('Error, fetching data for', ticker)

#stochastic for every ticker
stoch14_nse100 = {}
for ticker in ticker_list:
    try:
        stoch14_nse100[ticker] = talib.STOCH(raw_data_nse100[ticker]['High'], raw_data_nse100[ticker]['Low'], raw_data_nse100[ticker]['Close'], 14)
    except:
        print('Error, fetching data for', ticker)



# strategy excecution
for date_index in range(0, len(date_list)-1):
    for ticker in ticker_list:
        try:
            current_ticker_price = np.round(raw_data_nse100[ticker]["Close"][date_index], 2)
            current_ticker_ema200 = np.round(ema200_nse100[ticker][date_index], 2)
            current_ticker_ema50 = np.round(ema50_nse100[ticker][date_index], 2)
            current_ticker_stoch_K = np.round(stoch14_nse100[ticker][0][date_index], 2)
            current_ticker_stoch_D = np.round(stoch14_nse100[ticker][1][date_index], 2)

            #buy rules syntax
            if (current_ticker_price > current_ticker_ema200) and (current_ticker_price > (current_ticker_ema50 * (1-(risk_ema50/100)))) and((current_ticker_stoch_K > current_ticker_stoch_D) and (current_ticker_stoch_K >= STOCH_LOWER_BAND) and (current_ticker_stoch_D < STOCH_LOWER_BAND)) and (DEMAT_FUND >= current_ticker_price): 
                
                #first buy
                if first_buy:
                    first_buy = False
                    first_buy_str = [date_list[date_index]," BUY -- ", ticker, " Price: ",current_ticker_price, "ema200: ", current_ticker_ema200, "ema50: ",current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ", DEMAT_FUND, "    current ", ticker, "quantity: ", PORTFOLIO[ticker]] 
                
                
                DEMAT_FUND -= current_ticker_price
                PORTFOLIO[ticker] += 1

                print(date_list[date_index]," BUY -- ", ticker, " Price: ",current_ticker_price, " ema200: ",current_ticker_ema200, " ema50: ",current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ", DEMAT_FUND, "    current ", ticker, "quantity: ", PORTFOLIO[ticker])
                
                transactions += 1


            #sell rules syntax
            if PORTFOLIO[ticker] > 0:
                if current_ticker_price < (current_ticker_ema50 * (1-(risk_ema50/100))):

                    DEMAT_FUND += current_ticker_price * PORTFOLIO[ticker]
                    PORTFOLIO[ticker] = 0

                    print(date_list[date_index]," SELL ", ticker, " Price: ",current_ticker_price, " ema200: ",current_ticker_ema200, " ema50: ",current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ", DEMAT_FUND, "    current ", ticker, "quantity: ", PORTFOLIO[ticker], "REASON: Hit below EMA-200")
                    
                    transactions += 1


                if (current_ticker_stoch_K < STOCH_HIGHER_BAND) and (current_ticker_stoch_K < current_ticker_stoch_D) and (current_ticker_stoch_D >= STOCH_HIGHER_BAND):

                    DEMAT_FUND += current_ticker_price * PORTFOLIO[ticker]
                    PORTFOLIO[ticker] = 0

                    print(date_list[date_index]," SELL ", ticker, " Price: ",current_ticker_price, " ema200: ",current_ticker_ema200, " ema50: ",current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ", DEMAT_FUND, "    current ", ticker, "quantity: ", PORTFOLIO[ticker], "REASON: Selling by Stochastic indication")
                    
                    transactions += 1

        except IndexError:    # 'IndexError' is likely to happen, so to avoid that exception handling is used
            print("IndexError in ", ticker)
        except KeyError:
            print("KeyError in ", ticker)
            
print(first_buy_str)


for ticker in PORTFOLIO:    # Counting total invested amount by multiplying the current portfolio ticker quantity with the current respective price
    try:    # 'IndexError' exception handling
        current_ticker_price = get_history(symbol=ticker, start=START_DATE, end=END_DATE)['Close'][-3]
        INVESTED_AMOUNT += current_ticker_price * PORTFOLIO[ticker]

    except IndexError:
        print("Portfolio counting IndexError in",ticker)

    except KeyError:
        print("Portfolio counting KeyError in  ",ticker)

print("Demat Fund: ", DEMAT_FUND, "\n",
      "Invested Fund's Current Value: ", INVESTED_AMOUNT, "\n",
      "Total Profit: ", np.round((INVESTED_AMOUNT+DEMAT_FUND-INITIAL_AMOUNT) * 100 / INITIAL_AMOUNT, 2), "%")

print(PORTFOLIO)