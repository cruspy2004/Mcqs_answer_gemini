import keyboard
import time

print("Testing keyboard library...")
print("Press ALT+S to test (or wait 10 seconds)")

triggered = False

def on_hotkey():
    global triggered
    print(">>> HOTKEY TRIGGERED!")
    triggered = True

keyboard.add_hotkey('alt+s', on_hotkey)
print("Hotkey registered. Waiting...")

start = time.time()
while time.time() - start < 10 and not triggered:
    time.sleep(0.1)

if triggered:
    print("SUCCESS - Hotkey worked!")
else:
    print("No hotkey detected in 10 seconds")

keyboard.unhook_all()
print("Done")
