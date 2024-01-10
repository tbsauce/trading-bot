import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_lwti_indicator(closing_values):
    period = 8
    atr_period = 8

    # Source of calculation ma
    source_ma = pd.Series(closing_values).diff(period)

    # Calculation ATR
    atr = pd.Series(closing_values).diff().abs().ewm(span=atr_period, min_periods=atr_period).mean()

    # LarryWilliams Calculation
    res_ma = (source_ma / atr * 50) + 50

    # Output
    no_value = res_ma.copy()
    bullish_value = res_ma.mask(res_ma <= 50)
    bearish_value = res_ma.mask(res_ma >= 50)

    # Repaint Calculation (The color is made based on < or > 50, it's just a coloration of the previous)
    bullish_value = bullish_value.where(res_ma > 50)
    bearish_value = bearish_value.where(res_ma < 50)

    # Create a DataFrame with the indicator values
    data = {
        'NoValue': no_value,
        'BullishValue': bullish_value,
        'BearishValue': bearish_value
    }
    df = pd.DataFrame(data)

    return df


url = "https://data.alpaca.markets/v2/stocks/bars?symbols=TSLA&timeframe=1Min&start=2024-01-04T0%3A00%3A00Z&end=2024-01-05T00%3A00%3A00Z&limit=1000&adjustment=raw&feed=sip&sort=asc"
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

df_lwti = analyze_lwti_indicator(df['c'])

# Filter data for the specified time range (9:30 AM to 10:00 AM)
# start_time = '10:00:00'
# end_time = '12:00:00'
# filtered_df = df.between_time(start_time, end_time)
# df_lwti = df_lwti.between_time(start_time, end_time)
filtered_df = df

# Initialize lists for buy/sell signals and stop-loss values
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
    if upper_band <= closing_cost and df_lwti['BullishValue'].iloc[i] > 50:
        
        buy_value = closing_cost
        #Sell values
        sell_down = closing_cost - (closing_cost * 0.001)
        sell_up = closing_cost + (closing_cost * 0.001)
        if buy == 1:
            buy_sell_signals.append(1)  # Buy signal
            buy -=1
        else: 
            buy_sell_signals.append(0)  # hold signal
    elif (sell_up <= closing_cost or closing_cost <= sell_down or df_lwti['BullishValue'].iloc[i] <= 50 or pd.isnull(df_lwti['BullishValue'].iloc[i])) and buy == 0:
        buy_sell_signals.append(-1)  # Sell signal
        buy_value = 0
        buy += 1
    else:
        buy_sell_signals.append(0)  # Hold signal
    if sell_down <= middle_band:
        sell_down = middle_band

    sell_down_values.append(sell_down)
    sell_up_values.append(sell_up)

# Convert the lists to NumPy arrays for further manipulation if needed
buy_sell_signals = np.array(buy_sell_signals)
sell_down_values = np.array(sell_down_values)
sell_up_values = np.array(sell_up_values)

# Generate buy and sell signals based on the filtered data
buy_signals = buy_sell_signals == 1
sell_signals = buy_sell_signals == -1

# Plotting TSLA stock price with buy/sell signals and stop-loss values
plt.figure(figsize=(15, 6))

# Plotting the TSLA stock price with upper band, buy/sell signals, and stop-loss values
plt.subplot(1, 2, 1)  # Subplot 1
plt.plot(filtered_df['c'], label='Closing Price', color='blue')
plt.plot(filtered_df['upper_band'], label='Upper Band', linestyle='--', color='blue')

# Plot buy signals (upper arrows)
plt.scatter(filtered_df.index[buy_signals], filtered_df['c'][buy_signals], marker='^', color='green', label='Buy Signal')

# Plot sell signals (lower flags)
plt.scatter(filtered_df.index[sell_signals], filtered_df['c'][sell_signals], marker='v', color='red', label='Sell Signal')

# Plot stop loss lines
plt.plot(filtered_df.index, sell_down_values, label='Sell Down', color='red', linestyle='--')
plt.plot(filtered_df.index, sell_up_values, label='Sell Up', color='green', linestyle='--')

plt.title('TSLA Stock Price with Buy/Sell Signals and Stop Loss (9:00 AM to 11:00 AM)')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)

# Plotting Larry Williams Large Trading Index (LWTI) indicator
plt.subplot(1, 2, 2)  # Subplot 2
plt.plot(df_lwti['NoValue'], label='No Value', color='gray')    
plt.plot(df_lwti['BullishValue'], label='LWTI Bullish Value', color='green')
plt.plot(df_lwti['BearishValue'], label='LWTI Bearish Value', color='red')

plt.title('Larry Williams Large Trading Index (LWTI) Indicator')
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()
plt.grid(True)

# Adjust layout and show plots
plt.tight_layout()
plt.show()
