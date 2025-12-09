import keyboard
import pyautogui
import base64
import requests
import time
import threading
import os
from win10toast import ToastNotifier

API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set")
    print("Set it with: set GEMINI_API_KEY=your_api_key_here")
    exit(1)

MODEL = "gemini-2.0-flash"

def screenshot_to_base64():
    """Capture screenshot and convert to base64"""
    try:
        image = pyautogui.screenshot()
        path = f"snap_{int(time.time())}.png"
        image.save(path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None

def ask_gemini(image_b64):
    """Send screenshot to Gemini API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
        prompt = (
            "Identify the correct answer for this MCQ.\n"
            "Response format ONLY:\n"
            "Option X: \"answer\"\n\n"
            "Example: Option D: \"The powerhouse of the cell\"\n"
            "NO explanation needed."
        )

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": image_b64}}
                ]
            }]
        }

        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

def show_notification(title, message):
    """Display Windows notification"""
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10, threaded=True)
    except:
        print(f"[{title}] {message}")

def on_hotkey():
    """Called when Alt+S is pressed"""
    print("\n>>> ALT+S pressed! Taking screenshot...")
    
    def worker():
        try:
            show_notification("MCQ Solver", "Taking screenshot...")
            time.sleep(0.3)
            
            img = screenshot_to_base64()
            if not img:
                show_notification("Error", "Failed to capture screenshot")
                return
            
            print(">>> Sending to Gemini...")
            show_notification("MCQ Solver", "Analyzing...")
            
            answer = ask_gemini(img)
            print(f">>> ANSWER: {answer}")
            show_notification("MCQ Answer", answer)
            
        except Exception as e:
            print(f"Error: {e}")
            show_notification("Error", str(e))
    
    threading.Thread(target=worker, daemon=True).start()

def main():
    print("=" * 50)
    print("  MCQ ANSWER SOLVER - RUNNING")
    print("=" * 50)
    print("  Hotkey: ALT + S")
    print("  Press Ctrl+C to exit")
    print("=" * 50)
    
    # Register the hotkey
    keyboard.add_hotkey('alt+s', on_hotkey)
    
    print("\nListening for ALT+S...")
    
    # Keep the program running
    try:
        keyboard.wait()  # Blocks forever until Ctrl+C
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
