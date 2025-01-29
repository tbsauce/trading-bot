import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np


from itertools import product

# Load environment variables
load_dotenv()

# Initialize Alpaca Headers
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": os.environ.get("KEY_ID"),
    "APCA-API-SECRET-KEY": os.environ.get("SECRET_KEY")
}

def get_bars_data(data_frame, symbol ,time_frame, start_date, feed):
    try:
    
        next_token = None
        
        # While to get all pages with data
        while True:
            # URL for the API request
            url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start_date}&limit=1000&adjustment=raw&feed={feed}&sort=asc"
            if next_token:
                url += f"&page_token={next_token}"
                
            # make request to API
            response = requests.get(url, headers=headers).json()
            df = pd.DataFrame(response["bars"]["TSLA"])
            data_frame = pd.concat([data_frame, df], ignore_index=True)
        

            # If there is no next_token leave loop
            next_token = response['next_page_token']
            if not next_token:
                break

    except:
        print("unexpected error getting bars from API")
    
    return data_frame.drop_duplicates()

def get_donchian_channel(data_frame, n_period, offset):

    data_frame['lower'] = data_frame['l'].rolling(window=n_period).min().shift(offset)
    data_frame['upper'] = data_frame['h'].rolling(window=n_period).max().shift(offset)
    data_frame['middle'] = ((data_frame['upper'] + data_frame['lower']) / 2).shift(offset)

    return data_frame

def get_volume(data_frame):

    data_frame['volume_bars'] = data_frame['v']
    data_frame.loc[data_frame['c'] < data_frame['c'].shift(1), 'volume_bars'] *= -1
    
    return data_frame

def get_volume_moving_average(data_frame, n_period):

    data_frame['volume_ma'] = data_frame['v'].rolling(window=n_period).mean()

    return data_frame

def get_williams_r(data_frame, n_period):
    highest = data_frame['h'].rolling(window=n_period).max()
    lowest = data_frame['l'].rolling(window=n_period).min()

    data_frame['WilliamsR'] = ((highest - data_frame['c']) / (highest - lowest)) * -100
    
    return data_frame

def strategy(data_frame, stop_loss_percent, stop_gain_percent):
    # Initialize variables
    trade_active = False
    entry_price = None
    stop_loss_price = None

    # Initialize all rows as 'HOLD'/0
    data_frame['Trade Action'] = 0.0

    for index, row in data_frame.iterrows():
        # Entry Condition
        if( not trade_active and row['c'] >= row['upper'] and row['WilliamsR'] >= -20 and row['v'] > row['volume_ma'] and row['volume_bars'] > 0):
            
            trade_active = True
            entry_price = row['c']
            stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
            stop_gain_price = entry_price * (1 + stop_gain_percent / 100)
            # Initialize row as 'BUY'/1
            data_frame.at[index, 'Trade Action'] = entry_price

        # Exit Condition and Initialize rows as 'SELL'/-1
        elif trade_active:
            if row['c'] <= stop_loss_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_loss_price

            elif row['c'] >= stop_gain_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_gain_price
    
            elif row['c'] < row['middle']:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * row['middle']


    return data_frame

def calculate_trade_stats(data_frame):
    total_profit_loss = 0
    profit_loss_values = []
    winning_trades = 0
    value_w = 0
    losing_trades = 0
    value_l = 0
    num_trades = 0

    buy_price = None

    # Iterate through the data_frame and identify BUY/SELL trades
    for index, row in data_frame.iterrows():
        trade_action = row['Trade Action']
        
        # buy action
        if trade_action > 0:
            buy_price = trade_action
        
        # sell action
        elif trade_action < 0:
            sell_price = trade_action * -1
            profit_or_loss = sell_price - buy_price
            

            # Update overall stats
            total_profit_loss += profit_or_loss
            profit_loss_values.append(total_profit_loss)
            if profit_or_loss < 0:  # It's a losing trade
                losing_trades += 1
                value_l += profit_or_loss
            else:  # It's a winning trade
                winning_trades += 1
                value_w += profit_or_loss
            num_trades += 1
            
            # Reset buy price
            buy_price = None

    winning_percentage = (winning_trades / num_trades) * 100 if num_trades > 0 else 0
    loosing_percentage = (losing_trades / num_trades) * 100 if num_trades > 0 else 0
    

    '''# Plot the profit/loss over time from the 'profit_loss_values' list
    plt.plot(profit_loss_values, label="Profit/Loss Over Time", color='green')
    plt.title('Profit and Loss Over Time')
    plt.xlabel('Trade Number')
    plt.ylabel('Profit/Loss')
    plt.grid(True)
    plt.legend()

    # Save the graph as an image file
    graph_filename = 'profit_loss_graph.png'
    plt.savefig(graph_filename)'''

    # Return the final trade statistics
    stats = {
        'total_profit_loss': total_profit_loss,
        'num_trades': num_trades,
        'winning_trades': winning_trades,
        'value_of_winning_trades': value_w,
        'losing_trades': losing_trades,
        'value_of_loosing_trades': value_l,
        'winning_percentage': round(winning_percentage, 2) if num_trades > 0 else 0,
        'loosing_percentage': round(loosing_percentage, 2) if num_trades > 0 else 0
    }
    
    return stats
    

def main_optimization():
    symbol = "TSLA"
    timeframe = "1H"
    feed = "iex"
    start_date = (datetime.now() - timedelta(days=300)).date()

    # Define parameter ranges
    donchian_period_range = range(5, 31, 5)  # Period from 5 to 30 with step 5
    donchian_offset_range = range(0, 10, 1)  # Offset from 0 to 9
    volume_ma_period_range = range(5, 101, 20)  # Volume MA period from 5 to 100 with step 20
    williams_period_range = range(5, 29, 5)  # Williams %R period from 5 to 28 with step 5

    best_stats = None
    best_parameters = None

    # Load data only once, this will be used for all parameter combinations
    stock_data = get_bars_data(pd.DataFrame(), symbol, timeframe, start_date, feed)
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




def main():

    symbol = "TSLA"
    timeframe = "1H"
    feed="iex"
    start_date = (datetime.now() - timedelta(days=300)).date()

    data_frame = pd.DataFrame()
    data_frame = get_bars_data(data_frame, symbol, timeframe, start_date, feed)
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

if __name__ == "__main__":
    main()
