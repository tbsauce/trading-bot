import requests

url = "https://paper-api.alpaca.markets/v2/calendar?start=2022-01-03&end=2022-01-03"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKIPW6JUBW9OS2K4IHB2",
    "APCA-API-SECRET-KEY": "GIW5OQCpieNsYQpeEvF4FmCbnSbhUtoUbCkrKulZ"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Request failed with status code:", response.status_code)

json_data = response.json()

print(json_data[0]["open"])
print(json_data[0]["close"])
