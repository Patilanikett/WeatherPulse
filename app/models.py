from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class LocationRequest(BaseModel):
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")

class CurrentWeather(BaseModel):
    temperature: float = Field(..., description="Current temperature in Celsius")
    temperature_fahrenheit: Optional[float] = Field(None, description="Current temperature in Fahrenheit")
    condition: str = Field(..., description="Weather condition")
    humidity: Optional[int] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    wind_speed: Optional[float] = Field(None, description="Wind speed")
    wind_direction: Optional[str] = Field(None, description="Wind direction")
    visibility: Optional[float] = Field(None, description="Visibility in km")
    uv_index: Optional[int] = Field(None, description="UV index")
    air_quality: Optional[str] = Field(None, description="Air quality status")

class DailyForecast(BaseModel):
    date: str = Field(..., description="Date of forecast")
    high_temp: float = Field(..., description="High temperature")
    low_temp: float = Field(..., description="Low temperature")
    condition: str = Field(..., description="Weather condition")
    precipitation_chance: Optional[int] = Field(None, description="Chance of precipitation")

class WeatherResponse(BaseModel):
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State/Province")
    country: str = Field(..., description="Country")
    current_weather: CurrentWeather
    forecast: Optional[List[DailyForecast]] = Field(None, description="Weather forecast")
    last_updated: datetime = Field(..., description="Last update timestamp")
    data_source: str = Field(..., description="Data source")
