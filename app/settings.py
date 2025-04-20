"""Configuration settings for the Spot2 real estate assistant application."""
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "spot2_assistant"
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.0-flash-live-001")
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
