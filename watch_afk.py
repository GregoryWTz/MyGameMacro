"""
Screen Keyword Watcher — Telegram Notifier
-------------------------------------------
Watches a region of your screen for keywords,
then sends a Telegram notification when detected.

Requirements:
    pip install mss pillow pytesseract requests
    setup a telegram bot and get your chat ID to receive notifications
"""

import time
import pytesseract
import mss
from PIL import Image, ImageFilter, ImageOps
import requests

# ─────────────────────────────────────────────
# CONFIGURATION — edit these values
# ─────────────────────────────────────────────

KEYWORDS = [
    # MERCHANTS
    "jester",
    "mari",
    "rin",
    # BIOMES
    "starfall",
    "corrupt",
    "heaven",
    "dreamspace",
    "manager",
    "cyber",
    "singularity",
    "sing"
]

WATCH_REGION = {
    "top": 150,
    "left": 10,
    "width": 565,
    "height": 240,
}

SCAN_INTERVAL = 0.1       # How often to scan (seconds)
COOLDOWN_AFTER_ALERT = 20 # Prevent duplicate alerts (seconds)

TELEGRAM_TOKEN = "123" # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "123" # Replace with your Telegram chat ID

# ─────────────────────────────────────────────


def send_telegram(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        print("  📱 Telegram notification sent!")
    except Exception as e:
        print(f"  ⚠️ Telegram failed: {e}")

send_telegram("🤖 Merchant Bot is running!")

def capture_region(region: dict) -> Image.Image:
    with mss.MSS() as sct:
        raw = sct.grab(region)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def extract_text(image: Image.Image) -> str:
    w, h = image.size
    image = image.resize((w * 2, h * 2), Image.LANCZOS)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image)


def main():
    print("=" * 50)
    print("  Screen Watcher — Telegram Notifier")
    print("=" * 50)
    print(f"  Keywords    : {KEYWORDS}")
    print(f"  Watch region: {WATCH_REGION}")
    print(f"  Scan rate   : every {SCAN_INTERVAL}s")
    print("  Press Ctrl+C to stop.\n")
    print(f"  👀 Watching for {KEYWORDS}...")

    last_alert_time = 0

    while True:
        try:
            now = time.time()

            # Skip if still in cooldown
            if now - last_alert_time < COOLDOWN_AFTER_ALERT:
                remaining = COOLDOWN_AFTER_ALERT - (now - last_alert_time)
                print(f"\r  ⏳ Cooldown: {remaining:.1f}s remaining...   ", end="", flush=True)
                time.sleep(SCAN_INTERVAL)
                continue

            # Capture and scan
            image = capture_region(WATCH_REGION)
            text = extract_text(image)
            text_lower = text.lower()
            matched = next((kw for kw in KEYWORDS if kw.lower() in text_lower), None)

            alert_msg = None
            if matched:
                if matched.lower() == "jester" or matched.lower() == "mari" or matched.lower() == "rin":
                    alert_msg = f"🔍 Merchant detected: '{matched}'\n🕐 Time: {time.strftime('%H:%M:%S')}"
                else:
                    alert_msg = f"🔍 Biome detected: '{matched}'\n🕐 Time: {time.strftime('%H:%M:%S')}"
                send_telegram(alert_msg)
                last_alert_time = time.time()

            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n  Stopped by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n  ⚠️ Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()