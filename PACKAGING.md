# GestureMate Packaging Guide

This guide explains how to create a standalone executable package for GestureMate on Linux.

## Quick Start

Simply run the packaging script:

```bash
./package.sh
```

The script will:
1. Check for required dependencies (Python 3, PyInstaller)
2. Install any missing dependencies
3. Create the beep sound file if needed
4. Build a standalone executable using PyInstaller
5. Create a distribution package in the `dist/` directory

## What's Included in the Package

The `dist/` directory will contain:

- **GestureMate** - The standalone executable
- **run-gesturemate.sh** - Launcher script (alternative way to run)
- **gesturemate.desktop** - Desktop entry file for menu integration
- **gesturemate.png** - Application icon
- **README.txt** - Instructions for end users

## Running the Packaged Application

### Method 1: Direct Execution (Recommended)
```bash
cd dist
./GestureMate
```

### Method 2: Using the Launcher Script
```bash
./dist/run-gesturemate.sh
```

### Method 3: Double-Click
Navigate to the `dist/` folder in your file manager and double-click the `GestureMate` executable.

## Desktop Integration

To add GestureMate to your application menu:

1. Edit `dist/gesturemate.desktop` and update the `Path=` line to point to your `dist/` directory
2. Copy the desktop file to your applications directory:
   ```bash
   cp dist/gesturemate.desktop ~/.local/share/applications/
   chmod +x ~/.local/share/applications/gesturemate.desktop
   ```
3. Copy the icon to your icons directory (optional):
   ```bash
   cp dist/gesturemate.png ~/.local/share/icons/
   ```

GestureMate should now appear in your application menu under Graphics/Education.

## Distribution

The entire `dist/` directory can be zipped and distributed to other users:

```bash
cd dist
tar -czf GestureMate-Linux.tar.gz *
```

Users can then extract and run without needing to install Python or any dependencies.

## Requirements for Building

- Python 3.7 or higher
- pip (Python package manager)
- PyInstaller (will be installed automatically)
- PyQt6 (will be installed automatically)

## Troubleshooting

### "Permission denied" when running the executable
```bash
chmod +x dist/GestureMate
```

### "No such file or directory" errors
Make sure you're in the correct directory and the packaging script completed successfully.

### Sound not working
The application includes a bundled `beep.wav` file. If sound still doesn't work, check your system's audio settings and ensure a sound output device is configured.

### PyInstaller not found
The script should install it automatically, but you can manually install it:
```bash
pip install --user pyinstaller
```

## Advanced Options

### Building without the packaging script

If you want to manually build with PyInstaller:

```bash
pyinstaller --clean --onefile --windowed \
  --name GestureMate \
  --add-data "beep.wav:." \
  --add-data "gesturemate.png:." \
  --icon "gesturemate.ico" \
  gesturemate.py
```

### Creating an AppImage

For even better distribution, you can create an AppImage:

1. First run `./package.sh` to create the base executable
2. Download appimagetool
3. Create the AppImage structure with the contents of `dist/`
4. Run appimagetool to create the final AppImage

(Detailed AppImage instructions coming soon)

## Notes

- The packaged executable is self-contained and includes all Python dependencies
- First launch may be slightly slower as the application unpacks
- The executable is specific to the architecture it was built on (x86_64, ARM, etc.)
- Configuration files are stored in `~/.config/gesturemate_config.json`

## Support

For issues with packaging or distribution, please open an issue on GitHub:
https://github.com/A-Andrews/GestureMate/issues
