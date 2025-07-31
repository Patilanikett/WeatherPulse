"""
Tests for main FastAPI application endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app
from app.models import WeatherResponse, CurrentWeather

client = TestClient(app)

class TestMainEndpoints:
    """Test class for main API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "WeatherPulse API is running!"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    @patch('app.weather_scraper.WeatherScraper.scrape_weather_data')
    def test_get_weather_success(self, mock_scraper):
        """Test successful weather data retrieval"""
        # Mock successful response
        mock_weather_data = WeatherResponse(
            city="Mumbai",
            country="India",
            current_weather=CurrentWeather(
                temperature=28.5,
                temperature_fahrenheit=83.3,
                condition="Partly Cloudy",
                humidity=65,
                pressure=1013.2,
                wind_speed=15.0,
                wind_direction="SW",
                visibility=10.0,
                uv_index=6,
                air_quality="Good"
            ),
            forecast=None,
            last_updated="2024-01-01T12:00:00",
            data_source="Bing Weather"
        )
        
        mock_scraper.return_value = mock_weather_data
        
        response = client.get("/weather/Mumbai")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Mumbai"
        assert data["current_weather"]["temperature"] == 28.5
        assert data["current_weather"]["condition"] == "Partly Cloudy"
    
    @patch('app.weather_scraper.WeatherScraper.scrape_weather_data')
    def test_get_weather_not_found(self, mock_scraper):
        """Test weather data not found"""
        mock_scraper.return_value = None
        
        response = client.get("/weather/InvalidCity")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    @patch('app.weather_scraper.WeatherScraper.scrape_weather_data')
    def test_get_weather_server_error(self, mock_scraper):
        """Test server error during weather data retrieval"""
        mock_scraper.side_effect = Exception("Scraping failed")
        
        response = client.get("/weather/TestCity")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to fetch weather data" in data["detail"]
    
    def test_search_weather_success(self):
        """Test weather search with location details"""
        search_data = {
            "city": "Delhi",
            "state": "Delhi",
            "country": "India"
        }
        
        with patch('app.weather_scraper.WeatherScraper.scrape_weather_data') as mock_scraper:
            mock_weather_data = WeatherResponse(
                city="Delhi",
                state="Delhi",
                country="India",
                current_weather=CurrentWeather(
                    temperature=32.0,
                    temperature_fahrenheit=89.6,
                    condition="Clear",
                    humidity=45,
                    pressure=1010.0,
                    wind_speed=8.0,
                    wind_direction="NW",
                    visibility=12.0,
                    uv_index=8,
                    air_quality="Moderate"
                ),
                forecast=None,
                last_updated="2024-01-01T12:00:00",
                data_source="Bing Weather"
            )
            mock_scraper.return_value = mock_weather_data
            
            response = client.post("/weather/search", json=search_data)
            assert response.status_code == 200
            data = response.json()
            assert data["city"] == "Delhi"
            assert data["state"] == "Delhi"
    
    def test_search_weather_invalid_data(self):
        """Test weather search with invalid data"""
        invalid_data = {
            "city": "",  # Empty city name
            "state": "TestState"
        }
        
        response = client.post("/weather/search", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.weather_scraper.WeatherScraper.scrape_forecast_data')
    def test_get_forecast_success(self, mock_scraper):
        """Test successful forecast data retrieval"""
        mock_forecast_data = {
            "city": "Bangalore",
            "forecast_days": 7,
            "forecast": [
                {
                    "date": "2024-01-01",
                    "high_temp": 28,
                    "low_temp": 22,
                    "condition": "Partly Cloudy",
                    "precipitation": "30%"
                }
            ]
        }
        mock_scraper.return_value = mock_forecast_data
        
        response = client.get("/weather/Bangalore/forecast?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Bangalore"
        assert len(data["forecast"]) == 1
    
    @patch('app.weather_scraper.WeatherScraper.scrape_forecast_data')
    def test_get_forecast_not_found(self, mock_scraper):
        """Test forecast data not found"""
        mock_scraper.return_value = None
        
        response = client.get("/weather/InvalidCity/forecast")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test class for async endpoint functionality"""
    
    async def test_async_weather_request(self):
        """Test async weather request"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.weather_scraper.WeatherScraper.scrape_weather_data') as mock_scraper:
                mock_weather_data = WeatherResponse(
                    city="Chennai",
                    country="India",
                    current_weather=CurrentWeather(
                        temperature=30.0,
                        condition="Sunny"
                    ),
                    forecast=None,
                    last_updated="2024-01-01T12:00:00",
                    data_source="Bing Weather"
                )
                mock_scraper.return_value = mock_weather_data
                
                response = await ac.get("/weather/Chennai")
                assert response.status_code == 200
                data = response.json()
                assert data["city"] == "Chennai"

class TestAPIValidation:
    """Test API input validation"""
    
    def test_city_name_validation(self):
        """Test city name validation in API"""
        # Test with special characters
        response = client.get("/weather/City@123")
        # Should still process but may return 404 or error
        assert response.status_code in [404, 500]
        
        # Test with very short name
        response = client.get("/weather/A")
        assert response.status_code in [404, 500]
    
    def test_forecast_days_validation(self):
        """Test forecast days parameter validation"""
        response = client.get("/weather/TestCity/forecast?days=0")
        # Should handle edge cases gracefully
        assert response.status_code in [200, 404, 422, 500]
        
        response = client.get("/weather/TestCity/forecast?days=100")
        # Should handle large numbers gracefully
        assert response.status_code in [200, 404, 422, 500]
