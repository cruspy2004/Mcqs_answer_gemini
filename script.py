from pynput import keyboard
import pyautogui
import base64
import requests
import time
import threading
from win10toast import ToastNotifier

API_KEY = "AIzaSyBuL5PZMjx1iHhCRo8fcqQy7AVIpqHlbQo"
MODEL = "gemini-2.0-flash"

# Global state
listener_active = False
hotkey_triggered = False

def screenshot_to_base64():
    """Capture screenshot and convert to base64"""
    try:
        image = pyautogui.screenshot()
        path = f"snap_{int(time.time())}.png"
        image.save(path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Screenshot error: {e}", flush=True)
        return None

def ask_gemini(image_b64):
    """Send screenshot to Gemini API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
        prompt = """Identify the correct answer for this MCQ.
Response format ONLY:
Option X: "answer"

Example: Option D: "The powerhouse of the cell"
NO explanation needed."""

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": image_b64}}
                ]
            }]
        }

        response = requests.post(url, json=payload, timeout=30)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

def show_notification(title, message):
    """Display Windows notification"""
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10)
    except:
        pass

def process_screenshot_async():
    """Process screenshot in background"""
    def worker():
        try:
            print("📸 Capturing screenshot...", flush=True)
            show_notification("MCQ Solver", "📸 Capturing...")
            time.sleep(0.5)
            
            img = screenshot_to_base64()
            if not img:
                show_notification("Error", "Failed to capture")
                return

            print("🔄 Sending to Gemini...", flush=True)
            show_notification("MCQ Solver", "🔄 Analyzing...")
            
            answer = ask_gemini(img)
            print(f"✅ Answer: {answer}", flush=True)
            show_notification("MCQ Answer", answer)
            
        except Exception as e:
            show_notification("Error", str(e))
    
    threading.Thread(target=worker, daemon=False).start()

def on_activate():
    """Called when Alt+S is pressed"""
    global hotkey_triggered
    print("\n🎯 ALT+S DETECTED!", flush=True)
    hotkey_triggered = True
    process_screenshot_async()

# Use system hotkey listener
def listen_with_hotkey():
    """Listen using keyboard hotkey combination"""
    try:
        from pynput.keyboard import Controller, Listener, Key
        
        def on_press(key):
            try:
                # Direct check for Alt+S
                if hasattr(key, 'vk') and key.vk == 18:  # Alt key
                    pass
            except:
                pass
        
        def on_release(key):
            pass
        
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        print(f"Listener error: {e}", flush=True)

def main():
    print("\n" + "="*60, flush=True)
    print("🚀 MCQ ANSWER SOLVER ACTIVE", flush=True)
    print("="*60, flush=True)
    print("📋 Press ALT + S to analyze MCQ on screen", flush=True)
    print("📧 Answer appears in notification", flush=True)
    print("❌ Press Ctrl+C to exit\n", flush=True)
    
    # For testing, let's use a simpler approach
    try:
        from pynput.keyboard import Listener, Key
        
        pressed_keys = set()
        
        def on_press(key):
            try:
                pressed_keys.add(key)
                
                # Check for Alt+S
                has_alt = any(k in [Key.alt, Key.alt_l, Key.alt_r] for k in pressed_keys)
                has_s = any(hasattr(k, 'char') and k.char and k.char.lower() == 's' for k in pressed_keys)
                
                if has_alt and has_s:
                    pressed_keys.clear()
                    on_activate()
                    
            except Exception as e:
                print(f"Error: {e}", flush=True)
        
        def on_release(key):
            pressed_keys.discard(key)
        
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
            
    except KeyboardInterrupt:
        print("\n👋 Exiting...", flush=True)
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
