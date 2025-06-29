import pandas as pd

def get_donchian_channel(data_frame, n_period, offset):

    data_frame['lower'] = data_frame['low'].rolling(window=n_period).min().shift(offset)
    data_frame['upper'] = data_frame['high'].rolling(window=n_period).max().shift(offset)
    data_frame['middle'] = ((data_frame['upper'] + data_frame['lower']) / 2).shift(offset)

    return data_frame

def get_volume(data_frame):

    data_frame['volume_bars'] = data_frame['volume']
    data_frame.loc[data_frame['close'] < data_frame['close'].shift(1), 'volume_bars'] *= -1
    
    return data_frame

def get_volume_moving_average(data_frame, n_period):

    data_frame['volume_ma'] = data_frame['volume'].rolling(window=n_period).mean()

    return data_frame

def get_williams_r(data_frame, n_period):

    highest = data_frame['high'].rolling(window=n_period).max()
    lowest = data_frame['low'].rolling(window=n_period).min()

    data_frame['WilliamsR'] = ((highest - data_frame['close']) / (highest - lowest)) * -100
    
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
    

    # # Plot the profit/loss over time from the 'profit_loss_values' list
    # plt.plot(profit_loss_values, label="Profit/Loss Over Time", color='green')
    # plt.title('Profit and Loss Over Time')
    # plt.xlabel('Trade Number')
    # plt.ylabel('Profit/Loss')
    # plt.grid(True)
    # plt.legend()
    #
    # # Save the graph as an image file
    # graph_filename = 'profit_loss_graph.png'
    # plt.savefig(graph_filename)

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
