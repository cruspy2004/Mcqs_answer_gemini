# gemini_mcq_helper_small_overlay.py
# HARD-CODED to model "models/gemini-2.5-flash"
# WARNING: Embedded API key below. Rotate key if this file is shared.

import os
import base64
import threading
import traceback
import time
import re
from io import BytesIO
from PIL import Image, ImageGrab
import tkinter as tk
import keyboard

# Optional OCR fallback (install pytesseract and Tesseract binary separately)
try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# ----------------- USER CONFIG -----------------
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GOOGLE_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set")
    print("Set it with: set GEMINI_API_KEY=your_api_key_here")
    exit(1)

HARDCODED_MODEL_NAME = "models/gemini-2.5-flash"
OVERLAY_DURATION_MS = 2500
COOLDOWN = 1.2  # seconds

# Overlay scaling (30% of previous size)
SCALE = 0.30
BASE_WIN_W = 280
BASE_WIN_H = 52
BASE_FONT_SIZE = 14
MIN_FONT_SIZE = 8   # keep text legible
MIN_WIN_H = 20      # ensure window can render

# ------------------------------------------------

# Initialize genai
genai = None
try:
    import google.generativeai as genai_lib
    genai_lib.configure(api_key=GOOGLE_API_KEY)
    genai = genai_lib
    print("[*] google.generativeai configured.")
except Exception:
    genai = None
    print("[!] google.generativeai unavailable or failed to configure. Traceback:")
    print(traceback.format_exc())

# ---------- Screenshot helper ----------
def capture_image_bytes() -> bytes:
    """Capture full-screen screenshot and return PNG bytes."""
    img = ImageGrab.grab()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

# ---------- Model query (uses generate_content path that worked for you) ----------
def query_model_with_image(image_bytes: bytes, model_name: str, debug: bool = False) -> str:
    """
    Send the image + instruction to the hardcoded model via GenerativeModel.generate_content.
    Returns the raw textual response (stripped) or raises an exception.
    """
    if genai is None:
        raise RuntimeError("genai not configured")

    instruction = (
        "You are shown a screenshot that contains a multiple-choice question (MCQ). "
        "Return ONLY the correct option letter (A, B, C or D). NOTHING ELSE."
    )

    prompt = [instruction, {"mime_type": "image/png", "data": image_bytes}]
    model_obj = genai.GenerativeModel(model_name)
    resp = model_obj.generate_content(prompt)

    if hasattr(resp, "text"):
        return resp.text.strip()
    # fallback to string conversion
    return str(resp).strip()

# ---------- OCR fallback ----------
def ocr_fallback_extract_option(image_bytes: bytes) -> str:
    if not OCR_AVAILABLE:
        return "OCR not available (install pytesseract + Tesseract)"
    try:
        img = Image.open(BytesIO(image_bytes)).convert("L")
        text = pytesseract.image_to_string(img)
        m = re.search(r'\b([A-D])\b', text, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
        m = re.search(r'([A-D])\)', text, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
        cleaned = " ".join(line.strip() for line in text.splitlines() if line.strip())
        snippet = cleaned[:140].replace("\n", " ")
        return f"OCR_RAW: {snippet}"
    except Exception:
        print("[WARN] OCR fallback failed; traceback:")
        print(traceback.format_exc())
        return "OCR ERR"

# ---------- Overlay ----------
def create_overlay(text: str, duration_ms: int = OVERLAY_DURATION_MS):
    """Show a small bottom-right overlay with scaled size and 30% opacity (runs in its own thread)."""
    def _show():
        try:
            root = tk.Tk()
            root.attributes("-topmost", True)
            # 0.0 = fully transparent, 1.0 = fully opaque
            root.attributes("-alpha", 0.30)   # 30% opacity per your request
            root.overrideredirect(True)

            # compute scaled sizes
            win_w = max(24, int(BASE_WIN_W * SCALE))
            win_h = max(MIN_WIN_H, int(BASE_WIN_H * SCALE))
            font_size = max(MIN_FONT_SIZE, int(BASE_FONT_SIZE * SCALE))

            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            x = screen_w - win_w - 16
            y = screen_h - win_h - 48
            root.geometry(f"{win_w}x{win_h}+{x}+{y}")

            frame = tk.Frame(root, bg="#ffffff", bd=0)
            frame.pack(expand=True, fill="both")

            # smaller font and wrap length adjusted for tiny window
            lbl = tk.Label(
                frame,
                text=text,
                font=("Segoe UI", font_size, "bold"),
                bg="#ffffff",
                fg="#000000",
                padx=2,
                pady=1,
                wraplength=max(20, win_w - 8),
                justify="center"
            )
            lbl.pack(expand=True, fill="both")

            # auto-close after duration
            root.after(duration_ms, root.destroy)
            root.mainloop()
        except Exception:
            print("[WARN] Overlay show failed; traceback:")
            print(traceback.format_exc())

    t = threading.Thread(target=_show, daemon=True)
    t.start()

# ---------- Worker and hotkey control ----------
processing_lock = threading.Lock()
_last_trigger = 0

def worker():
    global _last_trigger
    now = time.time()
    if now - _last_trigger < COOLDOWN:
        print("[*] Ignored - cooldown")
        return
    _last_trigger = now

    if not processing_lock.acquire(blocking=False):
        print("[*] Previous run still executing; ignoring trigger.")
        return

    try:
        print("⚡ Activating process...")
        print("📸 Capturing screenshot...")
        image_b = capture_image_bytes()

        raw_out = None
        if genai is not None:
            try:
                print("🧠 Sending to Gemini model:", HARDCODED_MODEL_NAME)
                raw_out = query_model_with_image(image_b, HARDCODED_MODEL_NAME, debug=True)
                print("[RAW MODEL RESPONSE repr]:", repr(raw_out))
            except Exception:
                print("[!] Model query failed; traceback:")
                print(traceback.format_exc())

        if not raw_out:
            print("[*] Using OCR fallback...")
            raw_out = ocr_fallback_extract_option(image_b)
            print("[OCR RAW]:", repr(raw_out))

        # sanitize: extract A-D letter
        m = re.search(r'\b([A-D])\b', str(raw_out), flags=re.IGNORECASE)
        if m:
            answer = m.group(1).upper()
            print("[*] Extracted answer:", answer)
        else:
            # show short preview
            single_line = str(raw_out).strip().splitlines()[0] if raw_out else ""
            preview = (single_line[:60] + "...") if len(single_line) > 60 else single_line
            answer = preview or "NO RESPONSE"
            print("[*] No single-letter found; preview:", repr(answer))

        create_overlay(answer)

    except Exception:
        print("[ERROR] worker top-level exception:")
        print(traceback.format_exc())
        create_overlay("ERROR")
    finally:
        processing_lock.release()

def exit_program():
    print("Exiting.")
    os._exit(0)

def main():
    print("🚀 Press 'A' + 'S' together to capture screen and query Gemini.")
    print("❎ Press 'Alt + 4' to exit the program.")
    print("[INFO] If hotkeys don't respond on Windows, run PowerShell as Administrator.")
    keyboard.add_hotkey("a+s", lambda: threading.Thread(target=worker, daemon=True).start())
    keyboard.add_hotkey("alt+4", lambda: exit_program())
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()