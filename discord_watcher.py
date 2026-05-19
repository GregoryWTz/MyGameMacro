"""
Discord Screen Watcher & Auto-Clicker
--------------------------------------
Watches a region of your screen for a keyword, then clicks a target
location the moment it's detected.

Requirements:
    pip install mss pillow pytesseract pyautogui
    Telegram is optional but recommended for instant notifications.
    If you want Telegram alerts, also install requests:
        pip install requests
    And don't forget to set up your Telegram bot and chat ID in the config below!

You also need Tesseract OCR installed on your system:
    Windows : https://github.com/UB-Mannheim/tesseract/wiki
    Linux   : sudo apt install tesseract-ocr
    macOS   : brew install tesseract
"""

import time
import pyautogui
import pytesseract
import mss
import mss.tools
from PIL import Image
import requests

# ─────────────────────────────────────────────
# CONFIGURATION — edit these values
# ─────────────────────────────────────────────

# Keywords to watch for (case-insensitive) — add as many as you want
KEYWORDS = [
    "glitch",
    "gli",
    "dream",
    "cyber",
    "space",
    "singularity",
    "singular",
    "sing",
    "jester",
    "jes"
]

# Screen region to watch (in pixels)
# Format: {"top": Y, "left": X, "width": W, "height": H}
# Tip: run get_position.py first to find your coordinates
WATCH_REGION = {
    "top": 830,
    "left": 450,
    "width": 1000,
    "height": 80,
}

# All coordinates to click when a keyword is found (clicked in order)
# Add more rows to cover more positions, e.g. if the link can appear at different heights
CLICK_TARGETS = [
    (980, 860),   # slightly above
    (980, 885),   # your main target
    (980, 910),   # slightly below
]

# Delay between each click in the list (in seconds)
CLICK_DELAY = 0.1  # 100ms between clicks

# How often to scan the screen (in seconds)
# Lower = faster reaction, higher = less CPU usage
SCAN_INTERVAL = 0.1  # 100ms — fast enough for most drops

# How long to wait (seconds) before scanning again after a click
# Prevents spam-clicking the same message
COOLDOWN_AFTER_CLICK = 10

# Optional: path to tesseract executable (Windows users usually need this)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TELEGRAM_TOKEN = "123" # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "123" # Replace with your Telegram chat ID

# ─────────────────────────────────────────────


def capture_region(region: dict) -> Image.Image:
    """Take a screenshot of the specified region."""
    with mss.MSS() as sct:
        raw = sct.grab(region)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def extract_text(image: Image.Image) -> str:
    """Run OCR on the image and return extracted text."""
    # Upscale for better OCR accuracy
    w, h = image.size
    image = image.resize((w * 2, h * 2), Image.LANCZOS)
    return pytesseract.image_to_string(image)

def send_telegram(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        print("  📱 Telegram notification sent!")
    except Exception as e:
        print(f"  ⚠️ Telegram failed: {e}")

send_telegram("🤖 Discord Watcher Bot is running!")

def main():
    print("=" * 50)
    print("  Discord Screen Watcher — Starting")
    print("=" * 50)
    print(f"  Keywords    : {KEYWORDS}")
    print(f"  Watch region: {WATCH_REGION}")
    print(f"  Click targets: {len(CLICK_TARGETS)} positions")
    print(f"  Scan rate   : every {SCAN_INTERVAL}s")
    print("  Press Ctrl+C to stop.\n")

    last_click_time = 0

    print(f"  👀 Watching for {KEYWORDS}...")

    while True:
        try:
            now = time.time()

            # Skip scan if still in cooldown
            if now - last_click_time < COOLDOWN_AFTER_CLICK:
                remaining = COOLDOWN_AFTER_CLICK - (now - last_click_time)
                print(f"\r  ⏳ Cooldown: {remaining:.1f}s remaining...   ", end="", flush=True)
                time.sleep(SCAN_INTERVAL)
                continue

            # Capture and read screen
            image = capture_region(WATCH_REGION)
            text = extract_text(image)

            # Check if ANY keyword is found in the screen text
            text_lower = text.lower()
            matched = next((kw for kw in KEYWORDS if kw.lower() in text_lower), None)

            if matched:
                send_telegram(f"✅ Keyword '{matched}' detected!")
                print(f"\n  ✅ Keyword '{matched}' detected! Clicking {len(CLICK_TARGETS)} positions...")
                for i, target in enumerate(CLICK_TARGETS):
                    pyautogui.click(target)
                    print(f"  🖱️  Click {i+1}/{len(CLICK_TARGETS)} at {target}")
                    if i < len(CLICK_TARGETS) - 1:
                        time.sleep(CLICK_DELAY)
                last_click_time = time.time()

            # Removed the else case to reduce console spam when no keywords are found

            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n  Stopped by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n  ⚠️  Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()