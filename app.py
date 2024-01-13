from bot import Bot
import matplotlib.pyplot as plt
import numpy as np
bot = Bot()

symbol = "TSLA"
time_frame = "1Min"
start_date = "2022-05-12T09:00:00Z"
end_date = "2022-05-12T11:30:00Z"
feed = "sip"

data = bot.get_historical_data(symbol, time_frame, start_date, end_date, feed)

# Donchian Channel
data_donchian_channels = bot.get_donchian_channel(25, symbol, time_frame, start_date, end_date, feed)

# Volume Bars
data_volume = bot.get_volume(data)

# Williams %R
data_williams_r = bot.get_williams_r(14, symbol, time_frame, start_date, end_date, feed)

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

    if not buy and (sell_up <= closing or closing <= sell_down):
        signals.append(-1 * closing)
        buy = 1
    elif upper <= closing:
        buy_value = closing
        sell_down = closing - (closing * 0.001)
        #muda tbm? ou n?
        # sell_up = closing + (closing * 0.001)

        if buy:
            sell_up = closing + (closing * 0.001)
            signals.append(closing)
            buy = 0
        else:
            signals.append(0)
    else:
        signals.append(0)

    if sell_down < middle:
        sell_down = middle
        
    sell_down_values.append(sell_down)
    sell_up_values.append(sell_up)

# Convert the list to a NumPy array
signals = np.array(signals)

sell_signals = signals < 0
buy_signals = signals > 0


# Create a single figure with three subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 18))

# Plot Donchian Channel
axs[0].plot(data['t'], data['c'], linestyle='-')
axs[0].plot(data['t'], data_donchian_channels['upper_band'], label='Upper Band', linestyle='--', color='blue')
axs[0].plot(data['t'], data_donchian_channels['middle_band'], label='Middle Band', linestyle='--', color='blue')
axs[0].plot(data['t'], sell_up_values, linestyle='--', label='Sell Up', color='green')
axs[0].plot(data['t'], sell_down_values, linestyle='--', label='Sell Down', color='red')
axs[0].scatter(data['t'][buy_signals], data['c'][buy_signals], marker='^', color='green', label='Buy Signal')
axs[0].scatter(data['t'][sell_signals], data['c'][sell_signals], marker='v', color='red', label='Sell Signal')
axs[0].set_xlabel('Time')
axs[0].set_ylabel('Closing Price')
axs[0].set_xticks([])
axs[0].legend()

# Plot Volume Bars
temp_positive = data_volume['volume_adjusted'].abs()
axs[1].bar(data_volume['t'], temp_positive, color=['g' if x >= 0 else 'r' for x in data_volume['volume_adjusted']])
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Volume')
axs[1].set_xticks([])
axs[1].legend()

# Plot Williams %R
axs[2].plot(data_williams_r['t'], data_williams_r['WilliamsR'], linestyle='-')
axs[2].axhline(y=-20, color='r', linestyle='--', label='Over Bought')
axs[2].axhline(y=-80, color='r', linestyle='--', label='Over Sold')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Closing Price')
axs[2].legend()

# Adjust layout
plt.tight_layout()
plt.show()