"""
Weather Dashboard - Fetches and displays weather data from OpenWeatherMap API
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class WeatherData:
    """Data class for weather information"""
    location: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    weather_main: str
    weather_description: str
    wind_speed: float
    wind_direction: int
    clouds: int
    sunrise: int
    sunset: int
    timezone: int
    timestamp: int


class WeatherDashboard:
    """Main weather dashboard class"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    
    # Weather condition icons
    WEATHER_ICONS = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Smoke': '💨',
        'Haze': '🌫️',
        'Dust': '🌪️',
        'Fog': '🌫️',
        'Sand': '🌪️',
        'Ash': '🌋',
        'Squall': '💨',
        'Tornado': '🌪️',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the weather dashboard
        
        Args:
            api_key: OpenWeatherMap API key (optional, loads from .env if not provided)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key not found. Set OPENWEATHER_API_KEY in .env file or pass it directly.")
        
        self.session = requests.Session()
        self.session.timeout = 10
    
    def get_weather_icon(self, condition: str) -> str:
        """Get emoji icon for weather condition"""
        return self.WEATHER_ICONS.get(condition, '🌤️')
    
    def get_current_weather(self, city: str, units: str = 'metric') -> Optional[WeatherData]:
        """
        Get current weather for a city
        
        Args:
            city: City name (e.g., "London", "New York")
            units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
            
        Returns:
            WeatherData object or None if request fails
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }
            
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather = WeatherData(
                location=f"{data['name']}, {data['sys']['country']}",
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                weather_main=data['weather'][0]['main'],
                weather_description=data['weather'][0]['description'],
                wind_speed=data['wind']['speed'],
                wind_direction=data['wind'].get('deg', 0),
                clouds=data['clouds']['all'],
                sunrise=data['sys']['sunrise'],
                sunset=data['sys']['sunset'],
                timezone=data['timezone'],
                timestamp=data['dt']
            )
            
            return weather
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data: {str(e)}")
            return None
        except KeyError as e:
            print(f"❌ Error parsing weather data: Missing key {str(e)}")
            return None
    
    def get_forecast(self, city: str, units: str = 'metric', days: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Get weather forecast for a city
        
        Args:
            city: City name
            units: Temperature units
            days: Number of days to forecast (1-5)
            
        Returns:
            List of forecast data or None if request fails
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'cnt': min(days * 8, 40)  # 5 day forecast has 40 entries (8 per day)
            }
            
            response = self.session.get(self.FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for forecast in data['list']:
                forecasts.append({
                    'timestamp': forecast['dt'],
                    'datetime': datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d %H:%M'),
                    'temperature': forecast['main']['temp'],
                    'feels_like': forecast['main']['feels_like'],
                    'humidity': forecast['main']['humidity'],
                    'weather': forecast['weather'][0]['main'],
                    'description': forecast['weather'][0]['description'],
                    'wind_speed': forecast['wind']['speed'],
                    'pressure': forecast['main']['pressure'],
                    'rain_chance': forecast.get('pop', 0) * 100
                })
            
            return forecasts
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching forecast data: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            print(f"❌ Error parsing forecast data: {str(e)}")
            return None
    
    def search_cities(self, query: str) -> Optional[List[Dict[str, str]]]:
        """
        Search for cities matching a query
        
        Args:
            query: City name or partial name
            
        Returns:
            List of matching cities or None
        """
        try:
            url = "https://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': query,
                'limit': 10,
                'appid': self.api_key
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            cities = []
            for result in data:
                cities.append({
                    'name': result['name'],
                    'country': result.get('country', 'N/A'),
                    'state': result.get('state', ''),
                    'lat': result['lat'],
                    'lon': result['lon']
                })
            
            return cities if cities else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching cities: {str(e)}")
            return None
    
    def get_weather_by_coordinates(self, latitude: float, longitude: float,
                                  units: str = 'metric') -> Optional[WeatherData]:
        """
        Get weather by geographic coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units
            
        Returns:
            WeatherData object or None if request fails
        """
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': units
            }
            
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather = WeatherData(
                location=f"{data['name']}, {data['sys']['country']}",
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                weather_main=data['weather'][0]['main'],
                weather_description=data['weather'][0]['description'],
                wind_speed=data['wind']['speed'],
                wind_direction=data['wind'].get('deg', 0),
                clouds=data['clouds']['all'],
                sunrise=data['sys']['sunrise'],
                sunset=data['sys']['sunset'],
                timezone=data['timezone'],
                timestamp=data['dt']
            )
            
            return weather
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data: {str(e)}")
            return None
    
    def save_weather_to_json(self, weather: WeatherData, filename: str = 'weather.json'):
        """
        Save weather data to JSON file
        
        Args:
            weather: WeatherData object
            filename: Output filename
        """
        try:
            data = {
                'location': weather.location,
                'temperature': weather.temperature,
                'feels_like': weather.feels_like,
                'humidity': weather.humidity,
                'pressure': weather.pressure,
                'weather_main': weather.weather_main,
                'weather_description': weather.weather_description,
                'wind_speed': weather.wind_speed,
                'wind_direction': weather.wind_direction,
                'clouds': weather.clouds,
                'sunrise': datetime.fromtimestamp(weather.sunrise).isoformat(),
                'sunset': datetime.fromtimestamp(weather.sunset).isoformat(),
                'timestamp': datetime.fromtimestamp(weather.timestamp).isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Weather data saved to {filename}")
            
        except IOError as e:
            print(f"✗ Error saving weather data: {str(e)}")
    
    def __del__(self):
        """Cleanup session"""
        try:
            self.session.close()
        except:
            pass
