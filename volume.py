import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fetching data from Alpaca API
url = "https://data.alpaca.markets/v2/stocks/bars?symbols=TSLA&timeframe=1Min&start=2024-01-04T09%3A00%3A00Z&end=2024-01-05T00%3A00%3A00Z&limit=1000&adjustment=raw&feed=sip&sort=asc"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKIPW6JUBW9OS2K4IHB2",
    "APCA-API-SECRET-KEY": "GIW5OQCpieNsYQpeEvF4FmCbnSbhUtoUbCkrKulZ"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Request failed with status code:", response.status_code)

json_data = response.json()

# Assuming you have already obtained the TSLA stock data
tsla_data = json_data['bars']['TSLA']

# Create DataFrame from the retrieved data
df = pd.DataFrame(tsla_data)

# Convert 't' column to datetime and set it as the index
df['t'] = pd.to_datetime(df['t'])

# Calculate Volume Moving Average (VMA)
n = 10  # Number of periods for VMA calculation
df['VolumeMA'] = df['v'].rolling(window=n).mean()

# Plotting Volume and VMA
plt.figure(figsize=(12, 6))

# Plot Volume bars
plt.bar(df.index, df['v'], color='blue', alpha=0.5, label='Volume')

# Plot Volume Moving Average (VMA)
plt.plot(df.index, df['VolumeMA'], color='red', label='Volume Moving Average (VMA)')

plt.title('Volume and Volume Moving Average (VMA)')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.legend()
plt.grid(True)
plt.show()