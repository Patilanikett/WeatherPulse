from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from weather_scraper import WeatherScraper
from models import WeatherResponse, LocationRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WeatherPulse API",
    description="Comprehensive Weather Data Scraping Service",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize weather scraper
weather_scraper = WeatherScraper()

@app.get("/")
async def root():
    return {"message": "WeatherPulse API is running!", "version": "1.0.0"}

@app.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    """Get current weather data for a specific city"""
    try:
        weather_data = await weather_scraper.scrape_weather_data(city)
        if not weather_data:
            raise HTTPException(status_code=404, detail=f"Weather data not found for {city}")
        return weather_data
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@app.post("/weather/search", response_model=WeatherResponse)
async def search_weather(location: LocationRequest):
    """Search weather data using location details"""
    try:
        weather_data = await weather_scraper.scrape_weather_data(location.city, location.state, location.country)
        if not weather_data:
            raise HTTPException(status_code=404, detail="Weather data not found")
        return weather_data
    except Exception as e:
        logger.error(f"Error searching weather: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search weather data")

@app.get("/weather/{city}/forecast")
async def get_weather_forecast(city: str, days: int = 7):
    """Get weather forecast for specified number of days"""
    try:
        forecast_data = await weather_scraper.scrape_forecast_data(city, days)
        if not forecast_data:
            raise HTTPException(status_code=404, detail=f"Forecast data not found for {city}")
        return forecast_data
    except Exception as e:
        logger.error(f"Error fetching forecast for {city}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecast data")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": weather_scraper.get_current_timestamp()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
