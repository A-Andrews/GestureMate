#!/usr/bin/env python3
"""Render a promotional demo video of GestureMate frame-by-frame, offscreen."""
import sys, os, shutil

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["XDG_CONFIG_HOME"] = "/tmp/gm-config-demo"
sys.path.insert(0, "/home/augustine/projects/GestureMate")

from PyQt6.QtWidgets import QApplication
import gesturemate

FRAMES = "/tmp/gm-frames"
shutil.rmtree(FRAMES, ignore_errors=True)
os.makedirs(FRAMES)

FPS = 30
DEMO_FOLDERS = {
    "/tmp/gm-demo/Figure_Studies": True,
    "/tmp/gm-demo/Hands_and_Feet": True,
    "/tmp/gm-demo/Animal_Sketches": True,
}

app = QApplication(sys.argv)
app.setApplicationName("GestureMate")
app.setStyle("Fusion")

win = gesturemate.GestureMate()
app.setPalette(win.palette())
win.showNormal()
win.resize(1920, 1080)
app.processEvents()

win.saved_folders = dict(DEMO_FOLDERS)
win.image_duration = 30
win.session_duration = 1800
win.halfway_sound_enabled = False
win.shuffle_enabled = False

frame_no = 0
def grab(seconds):
    """Capture the current state for `seconds` of video time."""
    global frame_no
    app.processEvents()
    pm = win.grab()
    for _ in range(round(seconds * FPS)):
        pm.save(f"{FRAMES}/{frame_no:05d}.jpg", "JPG", 92)
        frame_no += 1

def tick(n=1, hold=1.0):
    """Advance n simulated seconds, holding each state on screen for `hold` video-seconds."""
    for _ in range(n):
        win.update_image_timer()
        win.update_session_timer()
        grab(hold)

def press(btn, hold_after=0.0):
    """Show the button visibly pressed, release, then trigger it."""
    btn.setDown(True)
    grab(0.30)
    btn.setDown(False)
    btn.click()
    if hold_after:
        grab(hold_after)

def show(substr):
    for i, p in enumerate(win.images):
        if substr.lower() in os.path.basename(p).lower():
            win.current_image_index = i
            win.display_current_image()
            app.processEvents()
            return
    raise SystemExit(f"no image matching {substr!r}")

# --- opening: idle window, then Start Session pressed ---
win.image_label.setText("Session ended. Click 'Start Session' to begin.")
grab(1.3)
press(win.start_btn)
# stop the real timers; we simulate ticks deterministically
win.session_timer.stop()
win.image_timer.stop()

# shot 1: first figure study, timers running
show("Nude Study for the Figure")
grab(1.0)
tick(3)

# shot 2: Next Image pressed -> new image
press(win.next_btn)
show("Men in oriental dress")
grab(0.8)
tick(2)

# shot 3: transformations — flip horizontal, then greyscale, then reset
press(win.flip_h_btn, hold_after=1.4)
press(win.greyscale_btn, hold_after=1.4)
tick(1)
press(win.reset_transform_btn, hold_after=1.0)

# shot 4: hands study, brief hold
press(win.next_btn)
show("Praying Hands")
grab(0.8)
tick(2)

# shot 5: timer counts down to zero and auto-advances
win.image_time_remaining = 4
tick(3, hold=0.9)
tick(1)          # hits 0 -> auto next image
show("Two Figure Studies of a Young Woman")
grab(0.5)
tick(2)

print("frames:", frame_no, "-> duration %.1fs" % (frame_no / FPS))
