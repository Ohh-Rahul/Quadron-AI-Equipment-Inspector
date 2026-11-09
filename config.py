"""Centralized application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "Lab Equipment Condition Inspector"
APP_DESCRIPTION = (
    "Upload a photograph of laboratory equipment to prepare a visual condition "
    "assessment. This tool is not a certified safety inspection."
)

# These values are intentionally empty when no local .env values are configured.
AZURE_FOUNDRY_PROJECT_ENDPOINT = os.getenv("AZURE_FOUNDRY_PROJECT_ENDPOINT", "")
AZURE_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_MODEL_DEPLOYMENT_NAME", "")
AZURE_AUTHENTICATION_MODE = os.getenv("AZURE_AUTHENTICATION_MODE", "default")
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
