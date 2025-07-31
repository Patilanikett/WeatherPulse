"""
Data validation utilities for WeatherPulse
"""

import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator, Field
import logging

logger = logging.getLogger(__name__)

class CityValidator:
    """Validator for city names and locations"""
    
    @staticmethod
    def validate_city_name(city: str) -> bool:
        """Validate city name format"""
        if not city or len(city.strip()) < 2:
            return False
        
        # Allow letters, spaces, hyphens, and apostrophes
        pattern = r"^[a-zA-Z\s\-'\.]+$"
        return bool(re.match(pattern, city.strip()))
    
    @staticmethod
    def sanitize_city_name(city: str) -> str:
        """Sanitize and format city name"""
        if not city:
            return ""
        
        # Remove extra spaces and capitalize properly
        sanitized = " ".join(city.strip().split())
        return sanitized.title()
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude coordinates"""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180

class TemperatureValidator:
    """Validator for temperature values"""
    
    @staticmethod
    def validate_celsius(temp: float) -> bool:
        """Validate Celsius temperature (reasonable range)"""
        return -100 <= temp <= 60  # Extreme but possible range
    
    @staticmethod
    def validate_fahrenheit(temp: float) -> bool:
        """Validate Fahrenheit temperature (reasonable range)"""
        return -148 <= temp <= 140  # Extreme but possible range
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return (celsius * 9/5) + 32
    
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius"""
        return (fahrenheit - 32) * 5/9

class WeatherDataValidator:
    """Validator for weather data completeness and accuracy"""
    
    @staticmethod
    def validate_humidity(humidity: Optional[int]) -> bool:
        """Validate humidity percentage"""
        if humidity is None:
            return True
        return 0 <= humidity <= 100
    
    @staticmethod
    def validate_pressure(pressure: Optional[float]) -> bool:
        """Validate atmospheric pressure (hPa/mb)"""
        if pressure is None:
            return True
        return 800 <= pressure <= 1200  # Reasonable atmospheric pressure range
    
    @staticmethod
    def validate_wind_speed(wind_speed: Optional[float]) -> bool:
        """Validate wind speed (km/h)"""
        if wind_speed is None:
            return True
        return 0 <= wind_speed <= 500  # Extreme but possible wind speeds
    
    @staticmethod
    def validate_visibility(visibility: Optional[float]) -> bool:
        """Validate visibility (km)"""
        if visibility is None:
            return True
        return 0 <= visibility <= 50  # Reasonable visibility range
    
    @staticmethod
    def validate_uv_index(uv_index: Optional[int]) -> bool:
        """Validate UV index"""
        if uv_index is None:
            return True
        return 0 <= uv_index <= 15  # Standard UV index range

class LocationValidator(BaseModel):
    """Pydantic validator for location data"""
    
    city: str = Field(..., min_length=2, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    @validator('city')
    def validate_city(cls, v):
        if not CityValidator.validate_city_name(v):
            raise ValueError('Invalid city name format')
        return CityValidator.sanitize_city_name(v)
    
    @validator('state')
    def validate_state(cls, v):
        if v and not CityValidator.validate_city_name(v):
            raise ValueError('Invalid state name format')
        return CityValidator.sanitize_city_name(v) if v else v
    
    @validator('country')
    def validate_country(cls, v):
        if v and not CityValidator.validate_city_name(v):
            raise ValueError('Invalid country name format')
        return CityValidator.sanitize_city_name(v) if v else v

class WeatherConditionValidator:
    """Validator for weather conditions"""
    
    VALID_CONDITIONS = {
        'clear', 'sunny', 'partly cloudy', 'mostly cloudy', 'cloudy', 'overcast',
        'light rain', 'rain', 'heavy rain', 'drizzle', 'showers',
        'thunderstorm', 'snow', 'light snow', 'heavy snow', 'sleet',
        'fog', 'mist', 'haze', 'windy', 'calm'
    }
    
    @staticmethod
    def validate_condition(condition: str) -> bool:
        """Validate weather condition"""
        if not condition:
            return False
        return condition.lower().strip() in WeatherConditionValidator.VALID_CONDITIONS
    
    @staticmethod
    def normalize_condition(condition: str) -> str:
        """Normalize weather condition format"""
        if not condition:
            return "Unknown"
        
        normalized = condition.lower().strip()
        if normalized in WeatherConditionValidator.VALID_CONDITIONS:
            return normalized.title()
        
        # Try to match partial conditions
        for valid_condition in WeatherConditionValidator.VALID_CONDITIONS:
            if valid_condition in normalized or normalized in valid_condition:
                return valid_condition.title()
        
        return condition.title()

def validate_weather_response(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate complete weather response data"""
    errors = {}
    
    # Validate required fields
    if 'city' not in data or not data['city']:
        errors['city'] = 'City is required'
    elif not CityValidator.validate_city_name(data['city']):
        errors['city'] = 'Invalid city name format'
    
    # Validate current weather
    if 'current_weather' in data:
        current = data['current_weather']
        
        if 'temperature' in current:
            if not TemperatureValidator.validate_celsius(current['temperature']):
                errors['temperature'] = 'Invalid temperature value'
        
        if 'humidity' in current:
            if not WeatherDataValidator.validate_humidity(current['humidity']):
                errors['humidity'] = 'Invalid humidity value'
        
        if 'pressure' in current:
            if not WeatherDataValidator.validate_pressure(current['pressure']):
                errors['pressure'] = 'Invalid pressure value'
        
        if 'wind_speed' in current:
            if not WeatherDataValidator.validate_wind_speed(current['wind_speed']):
                errors['wind_speed'] = 'Invalid wind speed value'
    
    return errors
