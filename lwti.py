import requests
import pandas as pd
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

    # Iterating through indicator values to identify bullish states
    for index, row in df.iterrows():
        if row['BullishValue'] > 50:
            print(f"At {index}, the Larry Williams Large Trading Index is in a bullish state.")

    # Plotting the indicator values
    plt.figure(figsize=(12, 6))

    # Plot NoValue
    plt.plot(df['NoValue'], label='No Value', color='gray')

    # Plot BullishValue and BearishValue
    plt.plot(df['BullishValue'], label='Bullish Value', color='green')
    plt.plot(df['BearishValue'], label='Bearish Value', color='red')

    # Plotting middle line
    plt.axhline(y=50, color='black', linestyle='--', label='Middle')

    plt.title('Larry Williams Large Trading Index')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()

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

# Extracting closing values
closing_values = [data_point['c'] for data_point in tsla_data]

# Call the function to analyze the Larry Williams Large Trading Index indicator
analyze_lwti_indicator(closing_values)
