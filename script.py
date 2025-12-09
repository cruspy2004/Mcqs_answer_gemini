from pynput import keyboard
import pyautogui
import base64
import requests
import time

API_KEY = "AIzaSyBuL5PZMjx1iHhCRo8fcqQy7AVIpqHlbQo"
MODEL = "gemini-2.0-flash"  

def screenshot_to_base64():
    image = pyautogui.screenshot()
    path = f"snap_{int(time.time())}.png"
    image.save(path)

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ask_gemini(image_b64):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    { "text": "Explain what is in this screenshot and what I should do."},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return response.text

def on_press(key):
    try:
        if key == keyboard.Key.f8:  # Change this to any key
            print("Taking screenshot...")
            img = screenshot_to_base64()

            print("Sending to Gemini...")
            answer = ask_gemini(img)
            print("\n💬 GEMINI RESPONSE:\n", answer)
    except Exception as e:
        print("Error:", e)

def main():
    print("Listening... Press F8 to screenshot and ask Gemini.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
