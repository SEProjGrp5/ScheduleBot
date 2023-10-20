import datetime as dt
import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

f = open("src/apifile.txt", "r")

API_KEY = f.read() 
CITY = 'Raleigh'


url = BASE_URL + "appid="+ API_KEY #+ "&q=" + CITY


def getWeatherData(latlng):

    url = f'{BASE_URL}lat={latlng[0]}&lon={latlng[1]}&appid={API_KEY}'

    response = requests.get(url).json()

    print(response)

    temp_kelvin = response['main']['temp']
    temp_celsius = temp_kelvin - 273.15
    temp_fahrenheit = temp_celsius * (9/5) + 32
    feels_like = (response['main']['feels_like'] - 273.15) * (9/5) + 32
    desc = response['weather'][0]['description']
    humidity = response['main']['humidity']

    return humidity, temp_celsius, temp_fahrenheit, feels_like, desc


