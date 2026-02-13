import os
from dotenv import load_dotenv

load_dotenv()

# --- API KEYS ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
API_KEY = os.getenv("GEMINI_API_KEY")  # Kept for compatibility

# --- PATHS ---
BASE_DIR = os.getcwd() 
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUT_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data", "logs")
GEN_BG_DIR = os.path.join(ASSETS_DIR, "backgrounds", "ai_generated")
SS_DIR = os.path.join(ASSETS_DIR, "screenshots")
MOCKUP_PATH = os.path.join(ASSETS_DIR, "mockups", "device_frame.png")

# --- MODEL CONFIG ---
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- CANVAS SETTINGS ---
# Canvas Dimensions
CANVAS_WIDTH, CANVAS_HEIGHT = 1290, 2796
SCALE_RATIO, RADIUS = 0.95, 120 
BATCH_LIMIT = 5

# Mockup Fit Settings (Percentage of Frame Dimensions)
MOCKUP_SCREEN_W_RATIO = 0.96
MOCKUP_SCREEN_H_RATIO = 0.975
MOCKUP_OFFSET_Y = 15

# Text Settings
TEXT_POS_Y_RATIO = 0.05
TEXT_FONT_SIZE = 120
TEXT_FONT_PATH_MACOS = "/System/Library/Fonts/SFNS.ttf"
TEXT_FONT_PATH_FALLBACK = "/Library/Fonts/Arial.ttf"
