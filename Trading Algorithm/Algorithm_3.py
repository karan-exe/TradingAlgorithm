transactions = 0

import pandas as pd
import numpy as np
import talib
from datetime import date
from nsepy import get_history


# important variables for indicators
START_DATE = date(2018, 3, 15)
END_DATE = date.today()
STOCH_INTERVAL_DAYS = 14
STOCH_LOWER_BAND = 40
STOCH_HIGHER_BAND = 70

# date list to traverse through the dictionary
date_list = []
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
ticker_list = ['SBIN']#pd.read_csv("nifty50_csv.csv")['Symbol'].to_list() # top100 NSE_csv.csv

# portfolio Variables
portfolio = {ticker: {"quantity": 0, "average_trading_price": 0, "highest_traded_closing_price_after_buy": 0, "PNL": [], "buy_trigger": False, "Profit_fulfillment_bool_trigger": False} for ticker in ticker_list}


INITIAL_AMOUNT = 200000
demat_fund = 200000
lowest_demat_price = 200000
invested_amount = 0
PROFITABILITY_EXPECTANCY_RATE = 1.14
risk_ema50 = 5
risk_ema200 = 5
TRAILING_SL = 2.5


# raw data for each ticker
raw_data_nse100 = {}
try:
    for ticker in ticker_list:
        ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
        ticker_date_list = []
        try:
            ticker_date_list = [str(date) for date in ticker_dataframe.index]
        except AttributeError:
            print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
            try:
                ticker_date_list = [str(date) for date in ticker_dataframe.index]
            except AttributeError:
                print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError3 while fetching data for ticker_date_list, wait a while...")
        ticker_dataframe["date_list"] = ticker_date_list
        ticker_dataframe.set_index("date_list", inplace=True)
        raw_data_nse100[ticker] = ticker_dataframe
        
except AttributeError:
    print("AttributeError1 while fetching data for raw_data_nse100, wait a while...")
    try:
        for ticker in ticker_list:
            ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
            ticker_date_list = []
            try:
                ticker_date_list = [str(date) for date in ticker_dataframe.index]
            except AttributeError:
                print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                    try:
                        ticker_date_list = [str(date) for date in ticker_dataframe.index]
                    except AttributeError:
                        print("AttributeError3 while fetching data for ticker_date_list, wait a while...")
            ticker_dataframe["date_list"] = ticker_date_list
            ticker_dataframe.set_index("date_list", inplace=True)
            raw_data_nse100[ticker] = ticker_dataframe
            
    except AttributeError:
        print("AttributeError2 while fetching data for raw_data_nse100, wait a while...")
        try:
            for ticker in ticker_list:
                ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
                ticker_date_list = []
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
                    try:
                        ticker_date_list = [str(date) for date in ticker_dataframe.index]
                    except AttributeError:
                        print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                        try:
                            ticker_date_list = [str(date) for date in ticker_dataframe.index]
                        except AttributeError:
                            print("AttributeError3 while fetching data for ticker_date_list, wait a while...")
                ticker_dataframe["date_list"] = ticker_date_list
                ticker_dataframe.set_index("date_list", inplace=True)
                raw_data_nse100[ticker] = ticker_dataframe
        except AttributeError:
            print("AttributeError3 while fetching data for raw_data_nse100, wait a while...")

# indicators
#ema50 for every ticker
ema50_nse100 = {}
for ticker in ticker_list:
    try:
        ema50_nse100[ticker] = talib.EMA(raw_data_nse100[ticker]['Close'], 50)
    except:
        print('Error EMA 50, fetching data for', ticker)

#ema200 for every ticker
ema200_nse100 = {}
for ticker in ticker_list:
    try:
        ema200_nse100[ticker] = talib.EMA(raw_data_nse100[ticker]['Close'], 200)
    except:
        print('Error EMA 200, fetching data for', ticker)

#stochastic for every ticker
stoch14_nse100 = {}
for ticker in ticker_list:
    try:
        stoch14_nse100[ticker] = talib.STOCH(raw_data_nse100[ticker]['High'], raw_data_nse100[ticker]['Low'], raw_data_nse100[ticker]['Close'], 14)
    except:
        print('Error STOCH 14, fetching data for', ticker)



# strategy excecution
for date_index in date_list:
    for ticker in ticker_list:
        try:
            current_ticker_price = np.round(raw_data_nse100[ticker]["Close"][date_index], 2)
            current_ticker_ema200 = np.round(ema200_nse100[ticker][date_index], 2)
            current_ticker_ema50 = np.round(ema50_nse100[ticker][date_index], 2)
            current_ticker_stoch_K = np.round(stoch14_nse100[ticker][0][date_index], 2)
            current_ticker_stoch_D = np.round(stoch14_nse100[ticker][1][date_index], 2)
            
            if demat_fund < lowest_demat_price:
                lowest_demat_price = demat_fund
                
            # for the trailing stop-loss
            if portfolio[ticker]["quantity"] > 0:
                if current_ticker_price > portfolio[ticker]["highest_traded_closing_price_after_buy"]:
                    portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price
            
            #buying signals
            if demat_fund >= current_ticker_price:
                
                if (current_ticker_stoch_K > current_ticker_stoch_D) and (current_ticker_stoch_K >= STOCH_LOWER_BAND) and (current_ticker_stoch_D <= STOCH_LOWER_BAND):
                    portfolio[ticker]["buy_trigger"] = True
    
                if (portfolio[ticker]["buy_trigger"] == True) and ((current_ticker_ema50 >= current_ticker_ema200) and (current_ticker_price > (current_ticker_ema50 * (1-(risk_ema50/100))))):
    
                    demat_fund -= current_ticker_price      # modifying demat fund
                    portfolio[ticker]["average_trading_price"] = (((portfolio[ticker]["average_trading_price"] * portfolio[ticker][
                        "quantity"]) + current_ticker_price) / (portfolio[ticker]["quantity"] + 1))     # modifying average trading price
                    portfolio[ticker]["quantity"] = portfolio[ticker]["quantity"] + 1       # modifying quantity of the ticker in the portfolio
                    
                    # for the trailing stop-loss
                    if current_ticker_price > portfolio[ticker]["highest_traded_closing_price_after_buy"]:
                        portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price
                    
                    portfolio[ticker]["PNL"].append((date_index, "BOUGHT for", current_ticker_price,
                                                     portfolio[ticker]["average_trading_price"], portfolio[ticker]["quantity"], "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))    # taking record of the buy/sell mini statement for the excel sheet
    
                    if current_ticker_price > portfolio[ticker]["highest_traded_closing_price_after_buy"]:      # for the trailing stop-loss
                        portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price
    
                    portfolio[ticker]["buy_trigger"] = False    # for the next buying opportunity, turning the boolean value False
    
                    print(date_index, " BUY -- ", ticker, " Price: ", current_ticker_price, " ema200: ", current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"])       # message statement
    
                    transactions += 1
                    
            elif demat_fund < current_ticker_price:
                portfolio[ticker]["PNL"].append((date_index, "BUYING CHANCE!", current_ticker_price,
portfolio[ticker]["average_trading_price"], portfolio[ticker]["quantity"]))
                

            #selling signals
            if portfolio[ticker]["quantity"] > 0:

                if current_ticker_price >= (portfolio[ticker]["average_trading_price"] * PROFITABILITY_EXPECTANCY_RATE):

                    portfolio[ticker]["Profit_fulfillment_bool_trigger"] = True
                    print(date_index, " SELL ", ticker, " Price: ", current_ticker_price, " ema200: ",
                          current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ",
                          current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ",
                          portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"],
                          "REASON: Target Achieved!")

                if (current_ticker_stoch_K < STOCH_HIGHER_BAND) and (current_ticker_stoch_K < current_ticker_stoch_D) and (current_ticker_stoch_D >= STOCH_HIGHER_BAND) and (portfolio[ticker]["Profit_fulfillment_bool_trigger"] == True):     # According to stochastics

                    demat_fund += current_ticker_price * portfolio[ticker]["quantity"]
                    portfolio[ticker]["PNL"].append(
                        (date_index, "SOLD for", current_ticker_price, portfolio[ticker]["average_trading_price"], "PNL: ",
                         ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker][
                             "average_trading_price"],
                          "REASON: Selling by Stochastic indication", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))
                    portfolio[ticker]["quantity"] = 0
                    portfolio[ticker]["average_trading_price"] = 0
                    portfolio[ticker]["Profit_fulfillment_bool_trigger"] = False

                    print(date_index, " SELL ", ticker, " Price: ", current_ticker_price, " ema200: ", current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"],
                          "REASON: Selling by Stochastic indication")

                    transactions += 1
                    portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                if current_ticker_ema50 < (current_ticker_ema200 * (1 - (risk_ema200 / 100))):
                    # According to EMA50 below EMA200
                    demat_fund += current_ticker_price * portfolio[ticker]["quantity"]
                    portfolio[ticker]["PNL"].append(
                        (date_index, "SOLD for", current_ticker_price, portfolio[ticker]["average_trading_price"], "PNL: ",
                         np.round(
                             ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker][
                                 "average_trading_price"], 2), "REASON: Hit below EMA-200", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))
                    portfolio[ticker]["quantity"] = 0
                    portfolio[ticker]["average_trading_price"] = 0

                    print(date_index, " SELL -- ", ticker, " Price: ", current_ticker_price, " ema200: ", current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"], "REASON: Hit below EMA-200")

                    transactions += 1
                    portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                if current_ticker_price < (current_ticker_ema50 * (1 - (risk_ema50 / 100))):
                    # according to current price below EMA50
                    demat_fund += current_ticker_price * portfolio[ticker]["quantity"]
                    portfolio[ticker]["PNL"].append(
                        (date_index, "SOLD for", current_ticker_price, portfolio[ticker]["average_trading_price"], "PNL: ",
                         np.round(
                             ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker][
                                 "average_trading_price"], 2), "REASON: Hit below EMA-50", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))
                    portfolio[ticker]["quantity"] = 0
                    portfolio[ticker]["average_trading_price"] = 0

                    print(date_index, " SELL -- ", ticker, " Price: ", current_ticker_price, " ema200: ", current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"], "REASON: Hit below EMA-50")

                    transactions += 1
                    portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                if current_ticker_price < (portfolio[ticker]["highest_traded_closing_price_after_buy"] * (1 - (TRAILING_SL / 100))):
                    # according to trailing stop-loss
                    demat_fund += current_ticker_price * portfolio[ticker]["quantity"]
                    portfolio[ticker]["PNL"].append(
                        (date_index, "SOLD for", current_ticker_price, portfolio[ticker]["average_trading_price"], "PNL: ",
                         np.round(
                             ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker][
                                 "average_trading_price"], 2), "REASON: Hit below Trailing Stop-loss", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))
                    portfolio[ticker]["quantity"] = 0
                    portfolio[ticker]["average_trading_price"] = 0

                    print(date_index, " SELL -- ", ticker, " Price: ", current_ticker_price, " ema200: ", current_ticker_ema200,
                          " ema50: ", current_ticker_ema50, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D,
                          "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                          " average price: ", portfolio[ticker]["average_trading_price"], "REASON: Hit below Trailing Stop-loss")

                    transactions += 1
                    portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0


        except IndexError:    # 'IndexError', 'KeyError' and 'ValueErrors' are likely to happen, so to avoid that exception handling is used
            print("IndexError in ", ticker)
        except KeyError:
            print("KeyError in ", ticker)
        except ValueError:
            print("ValueError: in ", ticker)

for ticker in portfolio.keys():  # Counting total invested amount by multiplying the current portfolio ticker quantity with the current respective price
    try:  # 'IndexError' exception handling
        current_ticker_price = get_history(symbol=ticker, start=START_DATE, end=END_DATE)['Close'][-3]
        invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
    except AttributeError:
        print("portfolio counting AttributeError1 in", ticker)
        try:  # 'IndexError' exception handling
            current_ticker_price = get_history(symbol=ticker, start=START_DATE, end=END_DATE)['Close'][-3]
            invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
        except AttributeError:
            print("portfolio counting AttributeError2 in", ticker)
            try:  # 'IndexError' exception handling
                current_ticker_price = get_history(symbol=ticker, start=START_DATE, end=END_DATE)['Close'][-3]
                invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
            except AttributeError:
                print("portfolio counting AttributeError3 in", ticker)

    except IndexError:
        print("portfolio counting IndexError in", ticker)

    except KeyError:
        print("portfolio counting KeyError in  ", ticker)

print("Demat Fund: ", demat_fund, "\n",
      "Invested Fund's Current Value: ", invested_amount, "\n",
      "Total Profit: ", np.round((invested_amount + demat_fund - INITIAL_AMOUNT) * 100 / INITIAL_AMOUNT, 2), "%")

dfportfolio = pd.DataFrame(portfolio).transpose().to_csv("Report_Algorithm-3.csv")

print("lowest demat amount", lowest_demat_price)