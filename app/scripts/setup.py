#!/usr/bin/env python3
"""
Setup script for WeatherPulse project
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary project directories"""
    directories = [
        "logs",
        "data/cache",
        "data/exports",
        "tests",
        "docs",
        "app/utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Set up the development environment"""
    try:
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])
        print("✅ Dependencies installed successfully!")
        
        # Create .env file if it doesn't exist
        if not os.path.exists(".env"):
            with open(".env.example", "r") as example:
                with open(".env", "w") as env_file:
                    env_file.write(example.read())
            print("✅ Environment file created from template")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🌤️  WeatherPulse Project Setup")
    print("=" * 40)
    
    create_directories()
    setup_environment()
    
    print("\n🎉 Setup completed successfully!")
    print("Run 'python scripts/run.py' to start the application")
