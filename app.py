from bot import Bot
import matplotlib.pyplot as plt
import numpy as np
bot = Bot()

symbol = "TSLA"
time_frame = "5Min"
#bearsih market
start_date = "2021-11-01T09:00:00Z"
end_date = "2023-11-30T11:30:00Z"

feed = "sip"

data = bot.get_historical_data(symbol, time_frame, start_date, end_date, feed)

# Donchian Channel
data_donchian_channels = bot.get_donchian_channel(96, symbol, time_frame, start_date, end_date, feed)

# Volume Bars
data_volume = bot.get_volume(data)

# Volume MA
data_vma = bot.get_volume_moving_average(30, symbol, time_frame, start_date, end_date, feed)

# Williams %R 
data_williams_r = bot.get_williams_r(200, symbol, time_frame, start_date, end_date, feed)

# Strategy
signals = []

buy = 1
buy_value = 0
sell_down = sell_up = data_donchian_channels['middle_band'].iloc[0]
sell_down_values = []
sell_up_values = []

for i in range(len(data['c'])):
    closing = data['c'].iloc[i]
    upper = data_donchian_channels['upper_band'].iloc[i]
    middle = data_donchian_channels['middle_band'].iloc[i]

    
    good_to_buy = (upper <= closing and 
        data_volume['volume_bars'].iloc[i] > 0 and data_volume['volume_bars'].iloc[i -1] > 0 and
        data_vma['volume_ma'].iloc[i] < data_volume['volume_bars'].iloc[i] and
        data_vma['volume_ma'].iloc[i-1] < data_volume['volume_bars'].iloc[i-1] and
        data_volume['volume_bars'].iloc[i] > data_volume['volume_bars'].iloc[i-1] and 
        data_williams_r['WilliamsR'].iloc[i] >= -20)


    if buy and good_to_buy:
        sell_up = closing + (closing * 0.05)
        sell_down = middle
        signals.append(closing)
        buy = 0
    elif not buy and sell_up <= closing:
        signals.append(-1 * sell_up)
        buy = 1
    elif not buy and closing <= sell_down:
        signals.append(-1 * sell_down)
        buy = 1
    else: 
        signals.append(0)

    if sell_down < middle:
        sell_down = middle
        

    
    sell_down_values.append(sell_down)
    sell_up_values.append(sell_up)


# Statistics
trade_stats = bot.calculate_trade_stats(signals)
print("Total Profit/Loss:", trade_stats['total_profit_loss'])
print("Total Trades:", trade_stats['num_trades'])
print("Winning Trades:", trade_stats['winning_trades'])
print("Winning Trades value:", trade_stats['value_of_winning_trades'])
print("Losing Trades:", trade_stats['losing_trades'])
print("Losing Trades value:", trade_stats['value_of_loosing_trades'])
print("Winning Percentage:", trade_stats['winning_percentage'], "%")

exit(1)
# Graph

plt.figure(figsize=(10, 6))

# Plot Donchian Channel
plt.plot(data['t'], data['c'], linestyle='-')
plt.plot(data['t'], data_donchian_channels['upper_band'], label='Upper Band', linestyle='--', color='blue')
plt.plot(data['t'], data_donchian_channels['middle_band'], label='Middle Band', linestyle='--', color='blue')
plt.plot(data['t'], sell_up_values, linestyle='--', label='Sell Up', color='green')
plt.plot(data['t'], sell_down_values, linestyle='--', label='Sell Down', color='red')
signals = np.array(signals)
sell_signals = signals < 0
buy_signals = signals > 0
plt.scatter(data['t'][buy_signals], data['c'][buy_signals], marker='^', color='green', label='Buy Signal')
plt.scatter(data['t'][sell_signals], data['c'][sell_signals], marker='v', color='red', label='Sell Signal')

plt.legend()
plt.show()
