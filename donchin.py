import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

url = "https://data.alpaca.markets/v2/stocks/bars?symbols=TSLA&timeframe=1Min&start=2024-01-04T00%3A00%3A00Z&end=2024-01-05T00%3A00%3A00Z&limit=1000&adjustment=raw&feed=sip&sort=asc"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKIPW6JUBW9OS2K4IHB2",
    "APCA-API-SECRET-KEY": "GIW5OQCpieNsYQpeEvF4FmCbnSbhUtoUbCkrKulZ"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Request failed with status code:", response.status_code)

# Extracting data
json_data = response.json()
aapl_data = json_data['bars']['TSLA']
df = pd.DataFrame(aapl_data)

# Convert 't' column to datetime
df['t'] = pd.to_datetime(df['t'])

# Setting the index of the DataFrame to 't' (time)
df.set_index('t', inplace=True)

# Calculate the Donchian Channel for the entire dataset
n_period = 10  # Donchian Channel period
df['upper_band'] = df['h'].rolling(window=n_period).max().shift(1)
df['lower_band'] = df['l'].rolling(window=n_period).min().shift(1)
df['middle_band'] = ((df['upper_band'] + df['lower_band']) / 2)

# Filter data for the specified time range (9:30 AM to 10:00 AM)
# start_time = '10:00:00'
# end_time = '12:00:00'
start_time = '9:00:00'
end_time = '11:00:00'
filtered_df = df.between_time(start_time, end_time)

# Initialize a list for buy/sell signals
buy_sell_signals = []

buy = 1
buy_value = 0
sell_down = sell_up = filtered_df['middle_band'][0]
sell_down_values = []
sell_up_values = []

for i in range(len(filtered_df['upper_band'])):
    closing_cost = filtered_df['c'].iloc[i]
    middle_band = filtered_df['middle_band'].iloc[i]
    upper_band = filtered_df['upper_band'].iloc[i]
    if upper_band <= closing_cost:
        
        buy_value = closing_cost
        #Sell values
        sell_down = closing_cost - (closing_cost * 0.001)
        sell_up = closing_cost + (closing_cost * 0.001)
        if buy == 1:
            buy_sell_signals.append(1)  # Buy signal
            buy -=1
        else: 
            buy_sell_signals.append(0)  # hold signal
    elif (sell_up <= closing_cost or closing_cost <= sell_down) and buy == 0:
        buy_sell_signals.append(-1)  # Sell signal
        buy_value = 0
        buy += 1
    else:
        buy_sell_signals.append(0)  # Hold signal
    if sell_down <= middle_band:
        sell_down = middle_band

    sell_down_values.append(sell_down)
    sell_up_values.append(sell_up)



# Convert the list to a NumPy array for further manipulation if needed
buy_sell_signals = np.array(buy_sell_signals)
sell_down_values = np.array(sell_down_values)
sell_up_values = np.array(sell_up_values)


# Generate buy and sell signals based on the filtered data
buy_signals = buy_sell_signals == 1
sell_signals = buy_sell_signals == -1

# Plotting for the specified time range
plt.figure(figsize=(10, 6))
plt.plot(filtered_df['c'], label='Closing Price', color='blue')
plt.plot(filtered_df['upper_band'], label='Upper Band', linestyle='--', color='blue')
# plt.plot(filtered_df['middle_band'], label='Middle Band', linestyle='--', color='blue')
# plt.plot(filtered_df['lower_band'], label='Lower Band', linestyle='--', color='orange')

# Plot buy signals (upper arrows)
plt.scatter(filtered_df.index[buy_signals], filtered_df['c'][buy_signals], marker='^', color='green', label='Buy Signal')

# Plot sell signals (lower flags)
plt.scatter(filtered_df.index[sell_signals], filtered_df['c'][sell_signals], marker='v', color='red', label='Sell Signal')

# Plot stop loss line
plt.plot(filtered_df.index, sell_down_values, label='Sell Down', color='red', linestyle='--')

# Plot stop loss line
plt.plot(filtered_df.index, sell_up_values, label='Sell Up', color='green', linestyle='--')

plt.title('TSLA Stock Price with Buy/Sell Signals and Stop Loss (9:30 AM to 10:00 AM)')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
