#!/usr/bin/env python3
import sys
print("Script started!", flush=True)

try:
    from pynput import keyboard
    print("pynput imported", flush=True)
except Exception as e:
    print(f"Import error: {e}", flush=True)
    sys.exit(1)

def on_press(key):
    print(f"Key pressed: {key}", flush=True)
    try:
        if key == keyboard.Key.alt:
            print("ALT pressed!", flush=True)
        elif hasattr(key, 'char') and key.char == 's':
            print("S pressed!", flush=True)
    except:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.esc:
            print("ESC released - exiting", flush=True)
            return False
    except:
        pass

print("Starting listener...", flush=True)
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listener active - press keys", flush=True)
        listener.join()
except Exception as e:
    print(f"Listener error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("Script ended", flush=True)
