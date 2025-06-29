import sys
import time
from utils import * 

import requests
import configparser
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.historical.corporate_actions import CorporateActionsClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.stream import TradingStream
from alpaca.data.live.stock import StockDataStream

from alpaca.data.requests import * 
from alpaca.trading.requests import * 
from alpaca.trading.enums import *

# Load from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["keys"]["api_key"]
secret_key = config["keys"]["api_secret"]
paper=True

stock_historical_data_client = StockHistoricalDataClient(api_key, secret_key)
trade_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)

symbol = "TSLA"
timeframe = TimeFrame(amount = 1, unit = TimeFrameUnit.Hour)
feed="iex"
days = 300

data_request = StockBarsRequest(
    symbol_or_symbols = [symbol],
    timeframe=TimeFrame(amount = 1, unit = TimeFrameUnit.Hour), 
    start = (datetime.now() - timedelta(days=days)).date(),  
    feed=feed,
)

#Main live trader
def live_trading():

    while True:
        data_frame = stock_historical_data_client.get_stock_bars(data_request).df
        data_frame = get_donchian_channel(data_frame, 5, 4)
        data_frame = get_volume(data_frame)
        data_frame = get_volume_moving_average(data_frame, 45)
        data_frame = get_williams_r(data_frame, 20)

        data_frame = live_strategy(data_frame, 20, 40)

        time.sleep(60)

def live_strategy(data_frame, stop_price_percent, limit_price_percent):
    
    # Process only last line 
    row = data_frame.iloc[-1]
    
    # Entry Condition
    if( not trade_active and row['close'] >= row['upper'] and row['WilliamsR'] >= -20 and row['volume'] > row['volume_ma'] and row['volume_bars'] > 0):
        
        entry_price = row['close']
        stop_price = entry_price * (1 - stop_price_percent / 100)
        limit_price = entry_price * (1 + limit_price_percent / 100)
        # Initialize row as 'BUY'/1

        qty = math.floor((entry_price / trade_client.get_account()["cash"]) * 10) / 10

        req = MarketOrderRequest(
                    symbol = symbol,
                    qty = qty,
                    side = OrderSide.BUY,
                    time_in_force = TimeInForce.DAY,
                    order_class = OrderClass.BRACKET,
                    take_profit = TakeProfitRequest(limit_price=limit_price),
                    stop_loss = StopLossRequest(stop_price=stop_price)
        )
        res = trade_client.submit_order(req)

    return data_frame

# Function to test strategy with historical data
def backtesting():

    data_frame = stock_historical_data_client.get_stock_bars(data_request).df
    data_frame = get_donchian_channel(data_frame, 5, 4)
    data_frame = get_volume(data_frame)
    data_frame = get_volume_moving_average(data_frame, 45)
    data_frame = get_williams_r(data_frame, 20)
    data_frame = strategy(data_frame, 20, 40)
    stats = calculate_trade_stats(data_frame)
    
    print("Total Profit/Loss:", stats['total_profit_loss'])
    print("Number of Trades:", stats['num_trades'])
    print("Winning Trades:", stats['winning_trades'])
    print("Value of Winning Trades:", stats['value_of_winning_trades'])
    print("Losing Trades:", stats['losing_trades'])
    print("Value of Losing Trades:", stats['value_of_loosing_trades'])
    print("Winning Percentage:", stats['winning_percentage'], "%")
    print("Loosing Percentage:", stats['loosing_percentage'], "%")

# Funcion to get the best parameters for the strategy
def backtesting_optimization():

    # Define parameter ranges
    donchian_period_range = range(5, 31, 5)  # Period from 5 to 30 with step 5
    donchian_offset_range = range(0, 10, 1)  # Offset from 0 to 9
    volume_ma_period_range = range(5, 101, 20)  # Volume MA period from 5 to 100 with step 20
    williams_period_range = range(5, 29, 5)  # Williams %R period from 5 to 28 with step 5
    total_iterations = len(donchian_period_range) * len(donchian_offset_range) * len(volume_ma_period_range) * len(williams_period_range)
    print("Total Interations: {total_iterations}")

    best_stats = None
    best_parameters = None

    # Load data only once, this will be used for all parameter combinations
    stock_data = stock_historical_data_client.get_stock_bars(data_request).df
    stock_data = get_volume(stock_data)

    # Now loop through the combinations of parameters
    for donchian_period, volume_ma_period, williams_period, donchian_offset in product(
        donchian_period_range, volume_ma_period_range, williams_period_range, donchian_offset_range
    ):
        try:
            # Copy the pre-loaded stock data for each iteration
            data_frame = stock_data.copy()

            # Apply the specific indicators for the current parameters
            data_frame = get_donchian_channel(data_frame, donchian_period, donchian_offset)
            data_frame = get_volume_moving_average(data_frame, volume_ma_period)
            data_frame = get_williams_r(data_frame, williams_period)

            # Apply the strategy and calculate trade stats
            data_frame = strategy(data_frame, 20, 40)
            stats = calculate_trade_stats(data_frame)

            # Update the best performing parameters
            if best_stats is None or stats['total_profit_loss'] > best_stats['total_profit_loss']:
                best_stats = stats
                best_parameters = (donchian_period, volume_ma_period, williams_period, donchian_offset)

        except Exception as e:
            print(f"Error during optimization with {donchian_period=}, {volume_ma_period=}, {williams_period=}, {donchian_offset=}: {e}")
            continue

    # Output the best parameters and performance stats after the loop
    print("\nBest Parameters:")
    print(f"  Donchian Period: {best_parameters[0]}")
    print(f"  Donchian Offset: {best_parameters[3]}")
    print(f"  Volume MA Period: {best_parameters[1]}")
    print(f"  Williams %R Period: {best_parameters[2]}")

    print("\nTrade Stats for Best Parameters:")
    print(f"  Total Profit/Loss: {best_stats['total_profit_loss']}")
    print(f"  Number of Trades: {best_stats['num_trades']}")
    print(f"  Winning Trades: {best_stats['winning_trades']}")
    print(f"  Value of Winning Trades: {best_stats['value_of_winning_trades']}")
    print(f"  Losing Trades: {best_stats['losing_trades']}")
    print(f"  Value of Losing Trades: {best_stats['value_of_loosing_trades']}")
    print(f"  Winning Percentage: {best_stats['winning_percentage']}%")
    print(f"  Losing Percentage: {best_stats['losing_percentage']}%")

def strategy(data_frame, stop_loss_percent, stop_gain_percent):

    # Initialize variables
    trade_active = False
    stop_loss_price = None

    # Initialize all rows as 'HOLD'/0
    data_frame['Trade Action'] = 0.0

    for index, row in data_frame.iterrows():
        # Entry Condition
        if( not trade_active and row['close'] >= row['upper'] and row['WilliamsR'] >= -20 and row['volume'] > row['volume_ma'] and row['volume_bars'] > 0):
            
            trade_active = True
            entry_price = row['close']
            stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
            stop_gain_price = entry_price * (1 + stop_gain_percent / 100)
            # Initialize row as 'BUY'/1
            data_frame.at[index, 'Trade Action'] = entry_price

        # Exit Condition and Initialize rows as 'SELL'/-1
        elif trade_active:
            if row['close'] <= stop_loss_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_loss_price

            elif row['close'] >= stop_gain_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_gain_price
    
            elif row['close'] < row['middle']:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * row['middle']


    return data_frame

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py [live|backtest|optimize]")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "live":
        live_trading()
    elif mode == "backtest":
        backtesting()
    elif mode == "optimize":
        backtesting_optimization()
    else:
        print("Invalid mode. Use: live, backtest, or optimize")

if __name__ == "__main__":
    main()
