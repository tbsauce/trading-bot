import requests
import matplotlib.pyplot as plt

url = "https://data.alpaca.markets/v2/stocks/bars?symbols=TSLA&timeframe=1Min&start=2024-01-04T09%3A30%3A00Z&end=2024-01-04T10%3A00%3A00Z&limit=1000&adjustment=raw&feed=sip&sort=asc"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKIPW6JUBW9OS2K4IHB2",
    "APCA-API-SECRET-KEY": "GIW5OQCpieNsYQpeEvF4FmCbnSbhUtoUbCkrKulZ"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Request failed with status code:", response.status_code)

json_data = response.json()

# Assuming you have already obtained the AAPL stock data
aapl_data = json_data['bars']['TSLA']

# Extracting closing times and values
closing_times = [data_point['t'] for data_point in aapl_data]
closing_values = [data_point['c'] for data_point in aapl_data]

# Initialize variables to keep track of high and low prices
high = closing_values[0]
low = closing_values[0]

Bullish = 0
Bearish = 0
Consolidation = 0
# Access individual data points (vertices) using an index-based approach
for i in range(len(closing_values)):
    price = closing_values[i]

    if price > high:
        high = price
        low = closing_values[i-1]
        Bullish += 1
    elif price < low:
        low = price
        high= closing_values[i-1]
        Bearish += 1
    else:
        Consolidation += 1



print(f'Bullish: {Bullish}, Bearish: {Bearish}, Consolidation: {Consolidation}')

if Bullish > Bearish:
    print("Probably Bullish")
else:
    print("Probably Bearish")

# Plotting the closing values over time
plt.figure(figsize=(10, 6))
plt.plot(closing_times, closing_values, marker='o', linestyle='-')
plt.title('TSLA Closing Prices on Jan 3rd, 2022')
plt.xlabel('Time')
plt.ylabel('Closing Price ($)')
plt.xticks(rotation=45)
plt.tight_layout()

# Display the plot
plt.show()




    
