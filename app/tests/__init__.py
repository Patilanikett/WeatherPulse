"""
Test package for WeatherPulse application
"""

import sys
from pathlib import Path

# Add the app directory to Python path for testing
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

__version__ = "1.0.0"
