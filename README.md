# GestureMate

A gesture drawing practice application for artists. GestureMate helps you practice figure drawing by displaying images from your chosen folders with customizable timers.

## What's New

- 🌳 **Enhanced Folder Picker**: Tree view with expandable subfolders and image counts for each folder/subfolder
- ✨ **Fixed Sound System**: Halfway notification now uses a reliable cross-platform WAV file instead of system beep
- 🔄 **Image Rotation**: Rotate images 90° clockwise or counter-clockwise during your session
- 🎨 **App Icon**: New custom icon for GestureMate (gesturemate.png and gesturemate.ico)
- 📦 **Linux Packaging**: New `package.sh` script creates a standalone executable you can run without the command line

## Features

- 📁 **Multiple Folder Support**: Load images from multiple directories
- 🌳 **Subfolder Management**: See and manage subfolders in a tree view with individual checkboxes
- ✅ **Persistent Settings**: Folder selections and timer presets are saved and can be toggled on/off
- 📊 **Detailed Folder Statistics**: See exactly how many images are in each folder and subfolder
- 🔀 **Shuffle Control**: Choose to shuffle images or display them in order
- ⏱️ **Customizable Timers**: Set duration per image and total session length (presets saved automatically)
- ⬅️ **Image Navigation**: Move forward and backward through images
- ⌨️ **Full Keyboard Support**: Complete hotkey support for hands-free operation
- 🔄 **Image Transformations**: Flip horizontally, vertically, rotate 90°, or convert to greyscale
- 🔔 **Halfway Notification**: Optional audio beep at 50% of image time (now with reliable cross-platform sound)
- 🚀 **Quick Start**: Start sessions immediately without configuring settings
- 🖼️ **Smart Image Scaling**: Images automatically fit to your screen size
- 🎨 **Clean Interface**: Simple, distraction-free dark theme
- 🐧 **Linux Compatible**: Built with PyQt6 for cross-platform support

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- PyQt6 dependencies (usually pre-installed on most Linux distributions)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/A-Andrews/GestureMate.git
cd GestureMate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Linux Desktop Integration (Optional)

To add GestureMate to your application menu:

```bash
cp gesturemate.desktop ~/.local/share/applications/
cp gesturemate.png ~/.local/share/icons/
chmod +x ~/.local/share/applications/gesturemate.desktop
```

Make sure to edit the `Exec` line in the desktop file to point to the correct path.

### Creating a Standalone Package (Linux)

To create a standalone executable that doesn't require command-line launching:

```bash
./package.sh
```

This will create a `dist/` directory with a standalone executable. You can then:
- Run `./dist/GestureMate` directly
- Or use the launcher script: `./dist/run-gesturemate.sh`
- Follow the instructions in `dist/README.txt` for desktop integration

Requirements for packaging:
- PyInstaller (will be installed automatically by the script)
- All dependencies from requirements.txt

## Usage

### Running the Application

```bash
python gesturemate.py
```

Or make it executable:

```bash
chmod +x gesturemate.py
./gesturemate.py
```

### Getting Started

1. **Configure Settings** (Ctrl+S or File → Settings)
   - Click "Add Folder" to select directories containing your reference images
   - **NEW**: See image counts displayed next to each folder
   - **NEW**: When you add a folder, subfolders are automatically shown in a tree structure
   - **NEW**: Expand/collapse folder trees to see subfolders with their individual image counts
   - Toggle folders and subfolders on/off with checkboxes to include/exclude them from the session
   - Previously selected folders will be remembered with their subfolder states
   - Set the duration per image (in seconds)
   - Set the total session duration (in minutes)
   - Choose whether to shuffle images (enabled by default)
   - Click OK to apply settings

2. **Start Your Session**
   - Click "Start Session" to begin
   - Images will automatically advance based on your timer settings
   - Use "Previous" to go back to the previous image
   - Use "Next Image" to skip to the next reference
   - Use "Pause" to take a break
   - Use transformation buttons to flip, rotate images, or convert to greyscale
   - Use "Reset Transform" to clear all transformations
   - Use "Stop" to end the session early

### Keyboard Shortcuts

#### Session Control
- `Space`: Start Session
- `P`: Pause/Resume Session
- `Escape`: Stop Session

#### Image Navigation
- `Right Arrow`: Next Image
- `Left Arrow`: Previous Image

#### Image Transformations
- `H`: Flip Horizontal
- `V`: Flip Vertical
- `G`: Toggle Greyscale
- `R`: Rotate Clockwise (90°)
- `Shift+R`: Rotate Counter-Clockwise (90°)
- `T`: Reset All Transformations

#### Application
- `Ctrl+S`: Open Settings
- `Ctrl+Q`: Quit Application

## Supported Image Formats

- JPG/JPEG
- PNG
- BMP
- GIF
- WEBP

## Tips

- Organize your reference images into folders by category (e.g., poses, hands, animals)
- Start with longer durations (2-5 minutes) and work your way down to quick 30-second sketches
- The app will shuffle images randomly for variety
- Images are automatically scaled to fit your screen while maintaining aspect ratio

## License

MIT License - Feel free to use and modify as needed!

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
