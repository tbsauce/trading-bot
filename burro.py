from bot import Bot
import matplotlib.pyplot as plt
import numpy as np
import talib

bot = Bot()

symbol = "TSLA"
time_frame = "5Min"

start_date = "2022-01-03T09:00:00Z"
end_date = "2022-11-04T11:30:00Z"
feed = "sip"

data = bot.get_historical_data(symbol, time_frame, start_date, end_date, feed)

# Donchian Channel
upper_band, middle_band, lower_band = talib.BBANDS(data['c'], timeperiod=96)
data_donchian_channels = {'upper_band': upper_band, 'middle_band': middle_band, 'lower_band': lower_band}

# Volume Bars
data_volume = bot.get_volume(data)

# Volume MA
data_vma = talib.SMA(data_volume['v'], timeperiod=30)

# Williams %R
data_williams_r = talib.WILLR(data['h'], data['l'], data['c'], timeperiod=30)

# Strategy
signals = []

buy = 1
buy_value = 0
sell_down = sell_up = data_donchian_channels['middle_band'][0]
sell_down_values = []
sell_up_values = []

for i in range(len(data['c'])):
    closing = data['c'][i]
    upper = data_donchian_channels['upper_band'][i]
    middle = data_donchian_channels['middle_band'][i]

    if not buy and (sell_up <= closing or closing <= sell_down):
        signals.append(-1 * closing)
        buy = 1
    elif (buy and upper <= closing and
          data_volume['volume_bars'][i] > 0 and data_volume['volume_bars'][i - 1] > 0 and
          data_vma[i] < data_volume['volume_bars'][i] and
          data_vma[i - 1] < data_volume['volume_bars'][i - 1] and
          data_volume['volume_bars'][i] > data_volume['volume_bars'][i - 1] and
          data_williams_r[i] >= -20):
        buy_value = closing
        sell_down = closing - (closing * 0.001)
        sell_up = closing + (closing * 0.001)
        signals.append(closing)
        buy = 0
    else:
        signals.append(0)

    tmp = closing - (closing * 0.001)

    if sell_down < middle:
        sell_down = middle
    if not buy and sell_down < tmp:
        sell_down = tmp

    sell_down_values.append(sell_down)
    sell_up_values.append(sell_up)

# Statistics
trade_stats = bot.calculate_trade_stats(signals)
print("Total Profit/Loss:", trade_stats['total_profit_loss'])
print("Total Trades:", trade_stats['num_trades'])
print("Winning Trades:", trade_stats['winning_trades'])
print("Losing Trades:", trade_stats['losing_trades'])
print("Winning Percentage:", trade_stats['winning_percentage'], "%")

exit(1)
# Graph
fig, axs = plt.subplots(3, 1, figsize=(10, 18))

# Plot Donchian Channel
axs[0].plot(data['t'], data['c'], linestyle='-')
axs[0].plot(data['t'], data_donchian_channels['upper_band'], label='Upper Band', linestyle='--', color='blue')
axs[0].plot(data['t'], data_donchian_channels['middle_band'], label='Middle Band', linestyle='--', color='blue')
axs[0].plot(data['t'], sell_up_values, linestyle='--', label='Sell Up', color='green')
axs[0].plot(data['t'], sell_down_values, linestyle='--', label='Sell Down', color='red')
signals = np.array(signals)
sell_signals = signals < 0
buy_signals = signals > 0
axs[0].scatter(data['t'][buy_signals], data['c'][buy_signals], marker='^', color='green', label='Buy Signal')
axs[0].scatter(data['t'][sell_signals], data['c'][sell_signals], marker='v', color='red', label='Sell Signal')
axs[0].set_xlabel('Time')
axs[0].set_ylabel('Closing Price')
axs[0].set_xticks([])
axs[0].legend()

# Plot Volume Bars
temp_positive = data_volume['volume_bars'].abs()
axs[1].bar(data_volume['t'], temp_positive, color=['g' if x >= 0 else 'r' for x in data_volume['volume_bars']])
axs[1].plot(data['t'], data_vma, linestyle='--', label='ma', color='blue')
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Volume')
axs[1].set_xticks([])
axs[1].legend()

# Plot Williams %R
axs[2].plot(data['t'], data_williams_r, linestyle='-')
axs[2].axhline(y=-20, color='r', linestyle='--', label='Over Bought')
axs[2].axhline(y=-80, color='r', linestyle='--', label='Over Sold')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Closing Price')
axs[2].legend()

# Adjust layout
plt.tight_layout()
plt.show()
