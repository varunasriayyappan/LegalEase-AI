import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()

API_HOST = "127.0.0.1"
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}"

STREAMLIT_PORT = 8501

IMAGE_DIR = BASE_DIR / "Image"
LOGO_PATH = IMAGE_DIR / "Logo.png"

FOOTER_TEXT = "LegalEase Inc. | contact@legalease.com | All Rights Reserved."


def ensure_logo() -> None:
    """Create a simple logo with Pillow if Image/Logo.png does not exist.
    To use your own logo, just replace Image/Logo.png."""
    if LOGO_PATH.exists():
        return
    from PIL import Image, ImageDraw, ImageFont

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (600, 180), "white")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 30, 140, 150), radius=24, fill=(30, 58, 138))
    try:
        big = ImageFont.load_default(size=64)
        icon = ImageFont.load_default(size=80)
    except TypeError:  # very old Pillow
        big = icon = ImageFont.load_default()
    draw.text((52, 40), "L", fill="white", font=icon)
    draw.text((165, 52), "LegalEase", fill=(30, 58, 138), font=big)
    img.save(LOGO_PATH)