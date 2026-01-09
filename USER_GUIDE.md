# GestureMate User Guide

## Overview

GestureMate is a desktop application designed for artists who want to practice gesture drawing and figure studies. It displays reference images on a timer, helping you improve your quick sketching skills.

## Main Features

### 1. Multiple Folder Support
- Load reference images from as many folders as you want
- Great for organizing different types of references (poses, animals, objects, etc.)
- Recursively searches subfolders for images

### 2. Flexible Timer Settings

**Per-Image Timer:**
- Range: 10 seconds to 1 hour
- Perfect for everything from quick gestures to detailed studies
- Automatically advances to the next image when time expires

**Session Duration:**
- Range: 1 minute to 8 hours
- Set your practice session length
- Get notified when your session is complete

### 3. Smart Image Display
- Images automatically scale to fit your screen
- Maintains original aspect ratio (no distortion)
- Works with any screen size or resolution
- Dark background reduces eye strain

### 4. Session Controls

**Start/Stop:**
- Begin a new session with your configured settings
- Stop at any time to end early

**Pause/Resume:**
- Take breaks without losing your place
- Timer freezes until you're ready to continue

**Next Image:**
- Skip to the next reference if needed
- Useful if you finish early or want to try something different

### 5. Progress Tracking
- See how much time remains for the current image
- Track total session time remaining
- Visual progress bar shows overall session completion

## Keyboard Shortcuts

- `Ctrl+S` - Open Settings dialog
- `Ctrl+Q` - Quit application

## Tips for Practice

### For Beginners
1. Start with 2-5 minute poses to get comfortable
2. Focus on capturing the overall gesture, not details
3. Use a single folder of simple references

### Intermediate
1. Reduce timer to 1-2 minutes
2. Mix different types of references (standing, sitting, dynamic)
3. Challenge yourself with 30-second quick sketches

### Advanced
1. Try 10-30 second gesture studies
2. Use multiple folders with varied subjects
3. Set longer sessions (30-60 minutes) for intensive practice

## Recommended Folder Structure

```
/home/user/references/
├── poses/
│   ├── standing/
│   ├── sitting/
│   └── dynamic/
├── hands/
├── animals/
└── objects/
```

## Supported Image Formats

- JPEG/JPG (most common)
- PNG (with transparency)
- BMP (bitmap)
- GIF (static images)
- WEBP (modern format)

## Troubleshooting

### No images loading?
- Check that your folders contain supported image formats
- Verify folder paths are correct
- Make sure you have read permissions for the folders

### Images not fitting screen?
- The application automatically scales images
- Try maximizing the window for best results
- Images maintain their aspect ratio to prevent distortion

### Timer not advancing?
- Make sure the session is not paused
- Check that image duration is not set too high

## System Requirements

- **OS:** Linux (also works on Windows and macOS with Qt6)
- **Python:** 3.7 or higher
- **Memory:** 100MB+ depending on image sizes
- **Display:** Any resolution (tested on 1920x1080)

## Privacy

- GestureMate runs entirely offline
- No data is collected or transmitted
- All images remain on your local machine
- No account or registration required
