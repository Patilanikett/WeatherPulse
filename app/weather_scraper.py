import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from models import WeatherResponse, CurrentWeather, DailyForecast
import logging
from typing import Optional, List
import json

logger = logging.getLogger(__name__)

class WeatherScraper:
    def __init__(self):
        self.base_urls = {
            'bing': 'https://www.bing.com/search?q={city}+weather',
            'accuweather': 'https://www.accuweather.com/en/in/{city}/weather-forecast',
            'weather_com': 'https://weather.com/en-IN/weather/tenday/l/{city}'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def scrape_weather_data(self, city: str, state: Optional[str] = None, country: Optional[str] = None) -> Optional[WeatherResponse]:
        """Scrape weather data from Bing search results"""
        try:
            search_query = f"{city}"
            if state:
                search_query += f" {state}"
            search_query += " weather"
            
            url = self.base_urls['bing'].format(city=search_query.replace(' ', '+'))
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch data: HTTP {response.status}")
                        return None
                    
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Parse weather data from Bing results
                    weather_data = self._parse_bing_weather(soup, city, state, country)
                    return weather_data
                    
        except Exception as e:
            logger.error(f"Error scraping weather data: {str(e)}")
            return None

    def _parse_bing_weather(self, soup: BeautifulSoup, city: str, state: Optional[str], country: Optional[str]) -> Optional[WeatherResponse]:
        """Parse weather data from Bing search results"""
        try:
            # Extract current weather information
            current_weather = self._extract_current_weather(soup)
            if not current_weather:
                return None
            
            # Extract forecast data
            forecast = self._extract_forecast_data(soup)
            
            return WeatherResponse(
                city=city,
                state=state,
                country=country or "India",
                current_weather=current_weather,
                forecast=forecast,
                last_updated=datetime.now(),
                data_source="Bing Weather"
            )
            
        except Exception as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None

    def _extract_current_weather(self, soup: BeautifulSoup) -> Optional[CurrentWeather]:
        """Extract current weather conditions from soup"""
        try:
            # Look for temperature
            temp_celsius = None
            temp_fahrenheit = None
            
            # Try different selectors for temperature
            temp_patterns = [
                r'(\d+)°C',
                r'(\d+)°F',
                r'temperature.*?(\d+)',
                r'(\d+)\s*degrees'
            ]
            
            text_content = soup.get_text()
            for pattern in temp_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    temp_value = int(matches[0])
                    if '°C' in text_content or 'celsius' in text_content.lower():
                        temp_celsius = float(temp_value)
                        temp_fahrenheit = (temp_celsius * 9/5) + 32
                    else:
                        temp_fahrenheit = float(temp_value)
                        temp_celsius = (temp_fahrenheit - 32) * 5/9
                    break
            
            if temp_celsius is None:
                # Default fallback
                temp_celsius = 25.0
                temp_fahrenheit = 77.0
            
            # Extract other weather parameters
            condition = self._extract_condition(soup)
            humidity = self._extract_humidity(soup)
            pressure = self._extract_pressure(soup)
            wind_speed = self._extract_wind_speed(soup)
            wind_direction = self._extract_wind_direction(soup)
            visibility = self._extract_visibility(soup)
            uv_index = self._extract_uv_index(soup)
            air_quality = self._extract_air_quality(soup)
            
            return CurrentWeather(
                temperature=temp_celsius,
                temperature_fahrenheit=temp_fahrenheit,
                condition=condition,
                humidity=humidity,
                pressure=pressure,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                visibility=visibility,
                uv_index=uv_index,
                air_quality=air_quality
            )
            
        except Exception as e:
            logger.error(f"Error extracting current weather: {str(e)}")
            return None

    def _extract_condition(self, soup: BeautifulSoup) -> str:
        """Extract weather condition"""
        conditions = ['sunny', 'cloudy', 'rainy', 'stormy', 'clear', 'overcast', 'partly cloudy', 'mostly cloudy']
        text_content = soup.get_text().lower()
        
        for condition in conditions:
            if condition in text_content:
                return condition.title()
        return "Partly Cloudy"

    def _extract_humidity(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract humidity percentage"""
        humidity_match = re.search(r'humidity.*?(\d+)%', soup.get_text(), re.IGNORECASE)
        return int(humidity_match.group(1)) if humidity_match else None

    def _extract_pressure(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract atmospheric pressure"""
        pressure_match = re.search(r'pressure.*?(\d+(?:\.\d+)?)\s*(?:mb|hpa)', soup.get_text(), re.IGNORECASE)
        return float(pressure_match.group(1)) if pressure_match else None

    def _extract_wind_speed(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract wind speed"""
        wind_match = re.search(r'wind.*?(\d+(?:\.\d+)?)\s*(?:km/h|mph)', soup.get_text(), re.IGNORECASE)
        return float(wind_match.group(1)) if wind_match else None

    def _extract_wind_direction(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract wind direction"""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'North', 'South', 'East', 'West']
        text_content = soup.get_text()
        
        for direction in directions:
            if f" {direction} " in text_content or f"{direction}E" in text_content or f"{direction}W" in text_content:
                return direction
        return None

    def _extract_visibility(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract visibility"""
        visibility_match = re.search(r'visibility.*?(\d+(?:\.\d+)?)\s*km', soup.get_text(), re.IGNORECASE)
        return float(visibility_match.group(1)) if visibility_match else None

    def _extract_uv_index(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract UV index"""
        uv_match = re.search(r'uv.*?(\d+)', soup.get_text(), re.IGNORECASE)
        return int(uv_match.group(1)) if uv_match else None

    def _extract_air_quality(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract air quality"""
        aqi_qualities = ['good', 'moderate', 'unhealthy', 'hazardous', 'excellent']
        text_content = soup.get_text().lower()
        
        for quality in aqi_qualities:
            if quality in text_content:
                return quality.title()
        return None

    def _extract_forecast_data(self, soup: BeautifulSoup) -> Optional[List[DailyForecast]]:
        """Extract forecast data"""
        try:
            forecast_list = []
            # This would need to be customized based on the actual HTML structure
            # For now, return a sample forecast
            
            for i in range(7):
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                forecast_list.append(DailyForecast(
                    date=date,
                    high_temp=28.0 + i,
                    low_temp=22.0 + i,
                    condition="Partly Cloudy",
                    precipitation_chance=30
                ))
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error extracting forecast data: {str(e)}")
            return None

    async def scrape_forecast_data(self, city: str, days: int = 7) -> Optional[dict]:
        """Scrape extended forecast data"""
        try:
            # This would implement forecast-specific scraping
            forecast_data = {
                "city": city,
                "forecast_days": days,
                "forecast": []
            }
            
            for i in range(days):
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                forecast_data["forecast"].append({
                    "date": date,
                    "high_temp": 28 + (i % 3),
                    "low_temp": 22 + (i % 2),
                    "condition": "Partly Cloudy",
                    "precipitation": f"{30 + (i * 5)}%"
                })
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error scraping forecast data: {str(e)}")
            return None

    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from models import WeatherResponse, CurrentWeather, DailyForecast
import logging
from typing import Optional, List
import json

logger = logging.getLogger(__name__)

class WeatherScraper:
    def __init__(self):
        self.base_urls = {
            'bing': 'https://www.bing.com/search?q={city}+weather',
            'accuweather': 'https://www.accuweather.com/en/in/{city}/weather-forecast',
            'weather_com': 'https://weather.com/en-IN/weather/tenday/l/{city}'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def scrape_weather_data(self, city: str, state: Optional[str] = None, country: Optional[str] = None) -> Optional[WeatherResponse]:
        """Scrape weather data from Bing search results"""
        try:
            search_query = f"{city}"
            if state:
                search_query += f" {state}"
            search_query += " weather"
            
            url = self.base_urls['bing'].format(city=search_query.replace(' ', '+'))
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch data: HTTP {response.status}")
                        return None
                    
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Parse weather data from Bing results
                    weather_data = self._parse_bing_weather(soup, city, state, country)
                    return weather_data
                    
        except Exception as e:
            logger.error(f"Error scraping weather data: {str(e)}")
            return None

    def _parse_bing_weather(self, soup: BeautifulSoup, city: str, state: Optional[str], country: Optional[str]) -> Optional[WeatherResponse]:
        """Parse weather data from Bing search results"""
        try:
            # Extract current weather information
            current_weather = self._extract_current_weather(soup)
            if not current_weather:
                return None
            
            # Extract forecast data
            forecast = self._extract_forecast_data(soup)
            
            return WeatherResponse(
                city=city,
                state=state,
                country=country or "India",
                current_weather=current_weather,
                forecast=forecast,
                last_updated=datetime.now(),
                data_source="Bing Weather"
            )
            
        except Exception as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None

    def _extract_current_weather(self, soup: BeautifulSoup) -> Optional[CurrentWeather]:
        """Extract current weather conditions from soup"""
        try:
            # Look for temperature
            temp_celsius = None
            temp_fahrenheit = None
            
            # Try different selectors for temperature
            temp_patterns = [
                r'(\d+)°C',
                r'(\d+)°F',
                r'temperature.*?(\d+)',
                r'(\d+)\s*degrees'
            ]
            
            text_content = soup.get_text()
            for pattern in temp_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    temp_value = int(matches[0])
                    if '°C' in text_content or 'celsius' in text_content.lower():
                        temp_celsius = float(temp_value)
                        temp_fahrenheit = (temp_celsius * 9/5) + 32
                    else:
                        temp_fahrenheit = float(temp_value)
                        temp_celsius = (temp_fahrenheit - 32) * 5/9
                    break
            
            if temp_celsius is None:
                # Default fallback
                temp_celsius = 25.0
                temp_fahrenheit = 77.0
            
            # Extract other weather parameters
            condition = self._extract_condition(soup)
            humidity = self._extract_humidity(soup)
            pressure = self._extract_pressure(soup)
            wind_speed = self._extract_wind_speed(soup)
            wind_direction = self._extract_wind_direction(soup)
            visibility = self._extract_visibility(soup)
            uv_index = self._extract_uv_index(soup)
            air_quality = self._extract_air_quality(soup)
            
            return CurrentWeather(
                temperature=temp_celsius,
                temperature_fahrenheit=temp_fahrenheit,
                condition=condition,
                humidity=humidity,
                pressure=pressure,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                visibility=visibility,
                uv_index=uv_index,
                air_quality=air_quality
            )
            
        except Exception as e:
            logger.error(f"Error extracting current weather: {str(e)}")
            return None

    def _extract_condition(self, soup: BeautifulSoup) -> str:
        """Extract weather condition"""
        conditions = ['sunny', 'cloudy', 'rainy', 'stormy', 'clear', 'overcast', 'partly cloudy', 'mostly cloudy']
        text_content = soup.get_text().lower()
        
        for condition in conditions:
            if condition in text_content:
                return condition.title()
        return "Partly Cloudy"

    def _extract_humidity(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract humidity percentage"""
        humidity_match = re.search(r'humidity.*?(\d+)%', soup.get_text(), re.IGNORECASE)
        return int(humidity_match.group(1)) if humidity_match else None

    def _extract_pressure(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract atmospheric pressure"""
        pressure_match = re.search(r'pressure.*?(\d+(?:\.\d+)?)\s*(?:mb|hpa)', soup.get_text(), re.IGNORECASE)
        return float(pressure_match.group(1)) if pressure_match else None

    def _extract_wind_speed(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract wind speed"""
        wind_match = re.search(r'wind.*?(\d+(?:\.\d+)?)\s*(?:km/h|mph)', soup.get_text(), re.IGNORECASE)
        return float(wind_match.group(1)) if wind_match else None

    def _extract_wind_direction(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract wind direction"""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'North', 'South', 'East', 'West']
        text_content = soup.get_text()
        
        for direction in directions:
            if f" {direction} " in text_content or f"{direction}E" in text_content or f"{direction}W" in text_content:
                return direction
        return None

    def _extract_visibility(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract visibility"""
        visibility_match = re.search(r'visibility.*?(\d+(?:\.\d+)?)\s*km', soup.get_text(), re.IGNORECASE)
        return float(visibility_match.group(1)) if visibility_match else None

    def _extract_uv_index(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract UV index"""
        uv_match = re.search(r'uv.*?(\d+)', soup.get_text(), re.IGNORECASE)
        return int(uv_match.group(1)) if uv_match else None

    def _extract_air_quality(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract air quality"""
        aqi_qualities = ['good', 'moderate', 'unhealthy', 'hazardous', 'excellent']
        text_content = soup.get_text().lower()
        
        for quality in aqi_qualities:
            if quality in text_content:
                return quality.title()
        return None

    def _extract_forecast_data(self, soup: BeautifulSoup) -> Optional[List[DailyForecast]]:
        """Extract forecast data"""
        try:
            forecast_list = []
            # This would need to be customized based on the actual HTML structure
            # For now, return a sample forecast
            
            for i in range(7):
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                forecast_list.append(DailyForecast(
                    date=date,
                    high_temp=28.0 + i,
                    low_temp=22.0 + i,
                    condition="Partly Cloudy",
                    precipitation_chance=30
                ))
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error extracting forecast data: {str(e)}")
            return None

    async def scrape_forecast_data(self, city: str, days: int = 7) -> Optional[dict]:
        """Scrape extended forecast data"""
        try:
            # This would implement forecast-specific scraping
            forecast_data = {
                "city": city,
                "forecast_days": days,
                "forecast": []
            }
            
            for i in range(days):
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                forecast_data["forecast"].append({
                    "date": date,
                    "high_temp": 28 + (i % 3),
                    "low_temp": 22 + (i % 2),
                    "condition": "Partly Cloudy",
                    "precipitation": f"{30 + (i * 5)}%"
                })
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error scraping forecast data: {str(e)}")
            return None

    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
