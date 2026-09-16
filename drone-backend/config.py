"""
Configuration settings for SKY SENTINEL Backend
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# YOLO Model Configuration
# ✅ CHANGED: Pointing to your newly trained drone detection model
YOLO_MODEL_PATH = MODELS_DIR / "sky_sentinel_drone_v1.pt"
YOLO_CONFIDENCE_THRESHOLD = 0.75
YOLO_IOU_THRESHOLD = 0.45

# Detection Classes (Custom Trained Model)
# ✅ CHANGED: Your model was trained with only 1 class (drone) at index 0
DETECTION_CLASSES = {
    0: 'drone',
}

# Thermal Imaging Settings
THERMAL_SWITCH_THRESHOLD = 0.3  # Confidence threshold to trigger thermal switch
GLARE_DETECTION_THRESHOLD = 200  # Pixel intensity threshold for glare detection
WHITEOUT_THRESHOLD = 240  # Pixel intensity threshold for whiteout detection

# Video Stream Settings
STREAM_FPS = 30
STREAM_QUALITY = 80  # JPEG quality for streaming
MAX_STREAM_RESOLUTION = (1280, 720)

# WebSocket Settings
WS_HOST = "0.0.0.0"
WS_PORT = 8000

# Alert Settings
ALERT_COOLDOWN = 5  # seconds between alerts for same detection