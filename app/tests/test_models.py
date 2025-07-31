"""
Tests for Pydantic models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import (
    WeatherResponse, 
    CurrentWeather, 
    DailyForecast, 
    LocationRequest
)

class TestCurrentWeather:
    """Test CurrentWeather model"""
    
    def test_valid_current_weather(self):
        """Test creating valid CurrentWeather instance"""
        weather = CurrentWeather(
            temperature=25.5,
            temperature_fahrenheit=77.9,
            condition="Sunny",
            humidity=60,
            pressure=1013.2,
            wind_speed=10.5,
            wind_direction="NW",
            visibility=15.0,
            uv_index=6,
            air_quality="Good"
        )
        
        assert weather.temperature == 25.5
        assert weather.condition == "Sunny"
        assert weather.humidity == 60
        assert weather.uv_index == 6
    
    def test_required_fields_only(self):
        """Test CurrentWeather with only required fields"""
        weather = CurrentWeather(
            temperature=20.0,
            condition="Cloudy"
        )
        
        assert weather.temperature == 20.0
        assert weather.condition == "Cloudy"
        assert weather.temperature_fahrenheit is None
        assert weather.humidity is None
    
    def test_invalid_temperature(self):
        """Test CurrentWeather with invalid temperature"""
        # Pydantic doesn't validate temperature range by default
        # This would pass unless we add custom validators
        weather = CurrentWeather(
            temperature=-200.0,  # Extremely cold but valid float
            condition="Test"
        )
        assert weather.temperature == -200.0
    
    def test_invalid_condition_type(self):
        """Test CurrentWeather with invalid condition type"""
        with pytest.raises(ValidationError):
            CurrentWeather(
                temperature=25.0,
                condition=123  # Should be string
            )

class TestDailyForecast:
    """Test DailyForecast model"""
    
    def test_valid_daily_forecast(self):
        """Test creating valid DailyForecast instance"""
        forecast = DailyForecast(
            date="2024-01-01",
            high_temp=30.0,
            low_temp=20.0,
            condition="Partly Cloudy",
            precipitation_chance=40
        )
        
        assert forecast.date == "2024-01-01"
        assert forecast.high_temp == 30.0
        assert forecast.low_temp == 20.0
        assert forecast.precipitation_chance == 40
    
    def test_optional_precipitation(self):
        """Test DailyForecast without precipitation chance"""
        forecast = DailyForecast(
            date="2024-01-01",
            high_temp=25.0,
            low_temp=15.0,
            condition="Sunny"
        )
        
        assert forecast.precipitation_chance is None
    
    def test_invalid_date_format(self):
        """Test DailyForecast with various date formats"""
        # This will pass as Pydantic accepts any string for date field
        forecast = DailyForecast(
            date="invalid-date",
            high_temp=25.0,
            low_temp=15.0,
            condition="Test"
        )
        assert forecast.date == "invalid-date"

class TestLocationRequest:
    """Test LocationRequest model"""
    
    def test_valid_location_request(self):
        """Test creating valid LocationRequest instance"""
        location = LocationRequest(
            city="Mumbai",
            state="Maharashtra",
            country="India"
        )
        
        assert location.city == "Mumbai"
        assert location.state == "Maharashtra"
        assert location.country == "India"
    
    def test_required_city_only(self):
        """Test LocationRequest with only required city field"""
        location = LocationRequest(city="Delhi")
        
        assert location.city == "Delhi"
        assert location.state is None
        assert location.country is None
    
    def test_empty_city_validation(self):
        """Test LocationRequest with empty city"""
        with pytest.raises(ValidationError):
            LocationRequest(city="")
    
    def test_missing_city_validation(self):
        """Test LocationRequest without city"""
        with pytest.raises(ValidationError):
            LocationRequest(state="TestState")

class TestWeatherResponse:
    """Test WeatherResponse model"""
    
    def test_valid_weather_response(self):
        """Test creating valid WeatherResponse instance"""
        current_weather = CurrentWeather(
            temperature=25.0,
            condition="Sunny"
        )
        
        forecast = [
            DailyForecast(
                date="2024-01-01",
                high_temp=28.0,
                low_temp=22.0,
                condition="Partly Cloudy"
            )
        ]
        
        response = WeatherResponse(
            city="Pune",
            country="India",
            current_weather=current_weather,
            forecast=forecast,
            last_updated=datetime.now(),
            data_source="Test Source"
        )
        
        assert response.city == "Pune"
        assert response.country == "India"
        assert response.current_weather.temperature == 25.0
        assert len(response.forecast) == 1
        assert response.data_source == "Test Source"
    
    def test_weather_response_without_forecast(self):
        """Test WeatherResponse without forecast data"""
        current_weather = CurrentWeather(
            temperature=22.0,
            condition="Rainy"
        )
        
        response = WeatherResponse(
            city="Kolkata",
            country="India",
            current_weather=current_weather,
            last_updated=datetime.now(),
            data_source="Test Source"
        )
        
        assert response.forecast is None
        assert response.current_weather.condition == "Rainy"
    
    def test_weather_response_with_state(self):
        """Test WeatherResponse with state information"""
        current_weather = CurrentWeather(
            temperature=28.0,
            condition="Hot"
        )
        
        response = WeatherResponse(
            city="Jaipur",
            state="Rajasthan",
            country="India",
            current_weather=current_weather,
            last_updated=datetime.now(),
            data_source="Test Source"
        )
        
        assert response.state == "Rajasthan"
    
    def test_invalid_weather_response_structure(self):
        """Test WeatherResponse with invalid structure"""
        with pytest.raises(ValidationError):
            WeatherResponse(
                city="TestCity",
                # Missing required current_weather field
                last_updated=datetime.now(),
                data_source="Test"
            )

class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_weather_response_to_dict(self):
        """Test converting WeatherResponse to dictionary"""
        current_weather = CurrentWeather(
            temperature=26.0,
            condition="Clear",
            humidity=55
        )
        
        response = WeatherResponse(
            city="Bangalore",
            country="India",
            current_weather=current_weather,
            last_updated=datetime(2024, 1, 1, 12, 0, 0),
            data_source="Test API"
        )
        
        response_dict = response.model_dump()
        
        assert response_dict["city"] == "Bangalore"
        assert response_dict["current_weather"]["temperature"] == 26.0
        assert response_dict["current_weather"]["humidity"] == 55
    
    def test_weather_response_from_dict(self):
        """Test creating WeatherResponse from dictionary"""
        response_data = {
            "city": "Hyderabad",
            "country": "India",
            "current_weather": {
                "temperature": 29.0,
                "condition": "Partly Cloudy",
                "humidity": 70
            },
            "last_updated": "2024-01-01T12:00:00",
            "data_source": "Test API"
        }
        
        response = WeatherResponse(**response_data)
        
        assert response.city == "Hyderabad"
        assert response.current_weather.temperature == 29.0
        assert response.current_weather.humidity == 70

class TestFieldValidation:
    """Test specific field validation"""
    
    def test_temperature_types(self):
        """Test different temperature value types"""
        # Integer temperature
        weather1 = CurrentWeather(temperature=25, condition="Test")
        assert weather1.temperature == 25.0
        
        # Float temperature
        weather2 = CurrentWeather(temperature=25.5, condition="Test")
        assert weather2.temperature == 25.5
        
        # String temperature should fail
        with pytest.raises(ValidationError):
            CurrentWeather(temperature="25.5", condition="Test")
    
    def test_optional_field_handling(self):
        """Test handling of optional fields"""
        weather = CurrentWeather(
            temperature=20.0,
            condition="Test",
            humidity=None,  # Explicitly set to None
            pressure=1013.2  # Set to value
        )
        
        assert weather.humidity is None
        assert weather.pressure == 1013.2
        assert weather.wind_speed is None  # Not provided, defaults to None
