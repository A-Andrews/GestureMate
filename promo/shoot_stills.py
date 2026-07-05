#!/usr/bin/env python3
"""Capture promotional screenshots of GestureMate by driving the real app offscreen."""
import sys, os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["XDG_CONFIG_HOME"] = "/tmp/gm-config-demo"  # isolate from real user config
sys.path.insert(0, "/home/augustine/projects/GestureMate")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import gesturemate

OUT = "/tmp/gm-promo"
DEMO_FOLDERS = {
    "/tmp/gm-demo/Figure_Studies": True,
    "/tmp/gm-demo/Hands_and_Feet": True,
    "/tmp/gm-demo/Animal_Sketches": True,
}

app = QApplication(sys.argv)
app.setApplicationName("GestureMate")
app.setStyle("Fusion")  # match the style real desktop users get; offscreen defaults to a styleless look

win = gesturemate.GestureMate()
# Offscreen platform doesn't propagate the main-window palette to children the way
# the real desktop session does; apply the app's own dark palette application-wide
# so captures match what users actually see.
app.setPalette(win.palette())
win.showNormal()
win.resize(1920, 1080)
app.processEvents()
print("style:", app.style().objectName())

win.saved_folders = dict(DEMO_FOLDERS)
win.image_duration = 30
win.session_duration = 1800
win.halfway_sound_enabled = False
win.shuffle_enabled = False

win.start_session()
app.processEvents()
print("loaded images:", len(win.images))
for i, p in enumerate(win.images):
    print(i, os.path.basename(p)[:70])

def set_timers(img_sec, sess_sec):
    """Set timer displays to specific values via the app's own update handlers."""
    win.image_time_remaining = img_sec + 1
    win.session_time_remaining = sess_sec + 1
    win.update_image_timer()
    win.update_session_timer()
    app.processEvents()

def show_index(i):
    win.current_image_index = i % len(win.images)
    win.display_current_image()
    app.processEvents()

def pick(substr):
    for i, p in enumerate(win.images):
        if substr.lower() in os.path.basename(p).lower():
            return i
    return 0

# --- Shot 1: hero session view ---
hero = pick(sys.argv[1]) if len(sys.argv) > 1 else pick("Nude Study for the Figure")
show_index(hero)
set_timers(23, 24 * 60 + 37)
win.grab().save(f"{OUT}/screenshot-session.png")
print("saved screenshot-session.png, hero index", hero)

# --- Shot 2: transformations active (greyscale + flip) ---
show_index(pick("Lion, BI-F"))
win.flip_h_btn.click()
win.greyscale_btn.click()
set_timers(11, 18 * 60 + 2)
app.processEvents()
win.grab().save(f"{OUT}/screenshot-transforms.png")
win.reset_transform_btn.click()
print("saved screenshot-transforms.png")

# --- Shot 3: settings dialog with folder tree ---
dlg = gesturemate.SettingsDialog(win, dict(DEMO_FOLDERS), 30, 30, True)
dlg.resize(760, 640)
dlg.show()
app.processEvents()
try:
    dlg.folder_tree.expandAll()
except Exception:
    pass
app.processEvents()
dlg.grab().save(f"{OUT}/screenshot-settings.png")
dlg.close()
print("saved screenshot-settings.png")

QTimer.singleShot(0, app.quit)
app.exec()
