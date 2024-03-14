import requests

def get_weather(api_key, city, country, date):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "cnt": 40,  # Number of forecast data to retrieve
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["cod"] != "200":
        print("Error:", data["message"])
        return

    for forecast in data["list"]:
        forecast_date = forecast["dt_txt"].split(" ")[0]
        if forecast_date == date:
            weather_desc = forecast["weather"][0]["description"]
            temp = forecast["main"]["temp"]
            temp_celsius = round(temp - 273.15, 2)
            print(f"On {date}, the weather in {city}, {country} is {weather_desc} with a temperature of {temp_celsius}°C.")
            return

    print(f"No forecast available for {date} in {city}, {country}.")

if __name__ == "__main__":
    api_key = "5fddc0d32e5e3f1e0a3ccfeefdb6154c"
    city = 'Guntur'
    country = 'IN'
    date = '2024-01-03'

    get_weather(api_key, city, country, date)
