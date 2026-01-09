# GestureMate

A gesture drawing practice application for artists. GestureMate helps you practice figure drawing by displaying images from your chosen folders with customizable timers.

## Features

- 📁 **Multiple Folder Support**: Load images from multiple directories
- ⏱️ **Customizable Timers**: Set duration per image and total session length
- 🖼️ **Smart Image Scaling**: Images automatically fit to your screen size
- 🎨 **Clean Interface**: Simple, distraction-free dark theme
- 🐧 **Linux Compatible**: Built with PyQt6 for cross-platform support
- ⌨️ **Keyboard Shortcuts**: Quick access to common actions

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
chmod +x ~/.local/share/applications/gesturemate.desktop
```

Make sure to edit the `Exec` line in the desktop file to point to the correct path.

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
   - Set the duration per image (in seconds)
   - Set the total session duration (in minutes)
   - Click OK to apply settings

2. **Start Your Session**
   - Click "Start Session" to begin
   - Images will automatically advance based on your timer settings
   - Use "Pause" to take a break
   - Use "Next Image" to skip to the next reference
   - Use "Stop" to end the session early

### Keyboard Shortcuts

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
