"""
Helper functions for WeatherPulse application
"""

import re
import math
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def format_temperature(temp: float, unit: str = 'C') -> str:
    """Format temperature with appropriate unit"""
    if unit.upper() == 'C':
        return f"{temp:.1f}°C"
    elif unit.upper() == 'F':
        return f"{temp:.1f}°F"
    else:
        return f"{temp:.1f}°"

def validate_city_name(city: str) -> bool:
    """Validate city name format"""
    if not city or len(city.strip()) < 2:
        return False
    
    # Allow letters, spaces, hyphens, apostrophes, and dots
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    return bool(re.match(pattern, city.strip()))

def get_formatted_timestamp(dt: Optional[datetime] = None) -> str:
    """Get formatted timestamp string"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def parse_weather_condition(condition_text: str) -> str:
    """Parse and normalize weather condition from text"""
    if not condition_text:
        return "Unknown"
    
    condition_mapping = {
        'clear': ['clear', 'sunny', 'bright'],
        'partly cloudy': ['partly cloudy', 'partly sunny', 'few clouds'],
        'mostly cloudy': ['mostly cloudy', 'broken clouds'],
        'cloudy': ['cloudy', 'overcast', 'gray'],
        'rain': ['rain', 'rainy', 'precipitation'],
        'drizzle': ['drizzle', 'light rain', 'sprinkle'],
        'thunderstorm': ['thunderstorm', 'thunder', 'storm'],
        'snow': ['snow', 'snowy', 'snowfall'],
        'fog': ['fog', 'foggy', 'mist', 'misty'],
        'wind': ['windy', 'breezy', 'gusty']
    }
    
    condition_lower = condition_text.lower()
    
    for normalized, keywords in condition_mapping.items():
        for keyword in keywords:
            if keyword in condition_lower:
                return normalized.title()
    
    return condition_text.title()

def calculate_heat_index(temp_f: float, humidity: float) -> float:
    """Calculate heat index (feels like temperature) in Fahrenheit"""
    if temp_f < 80 or humidity < 40:
        return temp_f
    
    # Rothfusz regression equation
    hi = (-42.379 + 
          2.04901523 * temp_f + 
          10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 
          6.83783e-3 * temp_f * temp_f - 
          5.481717e-2 * humidity * humidity + 
          1.22874e-3 * temp_f * temp_f * humidity + 
          8.5282e-4 * temp_f * humidity * humidity - 
          1.99e-6 * temp_f * temp_f * humidity * humidity)
    
    return round(hi, 1)

def convert_pressure_units(pressure: float, from_unit: str, to_unit: str) -> float:
    """Convert pressure between different units"""
    # Convert to hPa first (base unit)
    if from_unit.lower() == 'inhg':
        pressure_hpa = pressure * 33.8639
    elif from_unit.lower() == 'mmhg':
        pressure_hpa = pressure * 1.33322
    elif from_unit.lower() == 'psi':
        pressure_hpa = pressure * 68.9476
    else:  # Already in hPa
        pressure_hpa = pressure
    
    # Convert from hPa to target unit
    if to_unit.lower() == 'inhg':
        return round(pressure_hpa / 33.8639, 2)
    elif to_unit.lower() == 'mmhg':
        return round(pressure_hpa / 1.33322, 1)
    elif to_unit.lower() == 'psi':
        return round(pressure_hpa / 68.9476, 2)
    else:  # Return in hPa
        return round(pressure_hpa, 1)

def format_wind_direction(degrees: Optional[float]) -> str:
    """Convert wind direction degrees to compass direction"""
    if degrees is None:
        return "Variable"
    
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    index = round(degrees / 22.5) % 16
    return directions[index]

def extract_numeric_value(text: str, pattern: str) -> Optional[float]:
    """Extract numeric value from text using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            return None
    return None

def sanitize_html_text(html_text: str) -> str:
    """Clean HTML text for processing"""
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', html_text.strip())
    # Remove common HTML entities
    cleaned = cleaned.replace('&nbsp;', ' ').replace('&amp;', '&')
    return cleaned

def categorize_temperature(temp_c: float) -> str:
    """Categorize temperature into descriptive ranges"""
    if temp_c < 0:
        return "Freezing"
    elif temp_c < 10:
        return "Very Cold"
    elif temp_c < 20:
        return "Cold"
    elif temp_c < 25:
        return "Mild"
    elif temp_c < 30:
        return "Warm"
    elif temp_c < 35:
        return "Hot"
    else:
        return "Very Hot"

def calculate_dew_point(temp_c: float, humidity: float) -> float:
    """Calculate dew point temperature"""
    a = 17.27
    b = 237.7
    
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    
    return round(dew_point, 1)

def format_forecast_date(date_str: str) -> str:
    """Format forecast date for display"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%a, %b %d")
    except ValueError:
        return date_str

def validate_api_response(response_data: Dict[str, Any]) -> List[str]:
    """Validate API response data and return list of errors"""
    errors = []
    
    required_fields = ['city', 'current_weather']
    for field in required_fields:
        if field not in response_data:
            errors.append(f"Missing required field: {field}")
    
    if 'current_weather' in response_data:
        current = response_data['current_weather']
        if 'temperature' not in current:
            errors.append("Missing temperature in current weather")
        elif not isinstance(current['temperature'], (int, float)):
            errors.append("Invalid temperature format")
    
    return errors

def get_weather_emoji(condition: str) -> str:
    """Get emoji representation of weather condition"""
    emoji_map = {
        'clear': '☀️',
        'sunny': '☀️',
        'partly cloudy': '⛅',
        'mostly cloudy': '☁️',
        'cloudy': '☁️',
        'overcast': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'fog': '🌫️',
        'mist': '🌫️',
        'wind': '💨'
    }
    
    return emoji_map.get(condition.lower(), '🌤️')

def calculate_comfort_index(temp_c: float, humidity: float, wind_speed: float = 0) -> str:
    """Calculate comfort index based on temperature, humidity, and wind"""
    # Convert to heat index in Fahrenheit
    temp_f = (temp_c * 9/5) + 32
    heat_index = calculate_heat_index(temp_f, humidity)
    
    # Adjust for wind chill effect
    if temp_c < 10 and wind_speed > 5:
        # Simple wind chill adjustment
        feels_like = temp_c - (wind_speed * 0.5)
    else:
        feels_like = (heat_index - 32) * 5/9  # Convert back to Celsius
    
    if feels_like < 0:
        return "Extremely Cold"
    elif feels_like < 10:
        return "Very Cold"
    elif feels_like < 18:
        return "Cool"
    elif feels_like < 24:
        return "Comfortable"
    elif feels_like < 27:
        return "Warm"
    elif feels_like < 32:
        return "Hot"
    else:
        return "Extremely Hot"
