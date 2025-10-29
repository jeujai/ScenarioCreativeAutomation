import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "input"
OUTPUTS_DIR = BASE_DIR / "outputs"
EXAMPLES_DIR = BASE_DIR / "examples"

ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
    "9:16": (1080, 1920)
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

# Azure Blob Storage (SAS URL for secure, scoped access)
AZURE_STORAGE_SAS_URL = os.getenv("AZURE_STORAGE_SAS_URL", "")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "campaign-assets")
AZURE_UPLOAD_ENABLED = os.getenv("AZURE_UPLOAD_ENABLED", "true").lower() == "true"

DEFAULT_FONT_SIZE = 72
TEXT_COLOR = (255, 255, 255)
TEXT_SHADOW_COLOR = (0, 0, 0)
TEXT_PADDING = 50
