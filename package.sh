#!/bin/bash
# GestureMate Linux Packaging Script
# This script creates a standalone executable package for GestureMate

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="GestureMate"
APP_VERSION="1.0"
BUILD_DIR="build"
DIST_DIR="dist"

echo "========================================="
echo "GestureMate Linux Packaging Script"
echo "========================================="
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Check/Install PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install --user pyinstaller
fi

echo "✓ PyInstaller ready"

# Install dependencies
echo "Installing dependencies..."
pip install --user -r requirements.txt

echo "✓ Dependencies installed"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR" *.spec

# Create the beep sound if it doesn't exist
if [ ! -f "beep.wav" ]; then
    echo "Creating beep sound..."
    python3 << 'EOF'
import wave
import struct
import math

def create_beep_sound(filename='beep.wav', duration=0.2, frequency=800, sample_rate=44100):
    num_samples = int(duration * sample_rate)
    samples = []
    for i in range(num_samples):
        value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(struct.pack('h', value))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))

create_beep_sound()
EOF
fi

echo "✓ Resources ready"

# Build with PyInstaller
echo "Building executable with PyInstaller..."
pyinstaller --clean \
    --onefile \
    --windowed \
    --name "$APP_NAME" \
    --add-data "beep.wav:." \
    --add-data "gesturemate.png:." \
    --icon "gesturemate.ico" \
    gesturemate.py

echo "✓ Build complete"

# Create a launcher script
cat > "$DIST_DIR/run-gesturemate.sh" << 'LAUNCHER_EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
./GestureMate "$@"
LAUNCHER_EOF

chmod +x "$DIST_DIR/run-gesturemate.sh"

# Copy icon to dist
if [ -f "gesturemate.png" ]; then
    cp gesturemate.png "$DIST_DIR/"
fi

# Create desktop file
cat > "$DIST_DIR/gesturemate.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=GestureMate
Comment=Gesture drawing practice application
Exec=./GestureMate
Icon=./gesturemate.png
Terminal=false
Categories=Graphics;Education;Art;
Keywords=drawing;gesture;practice;art;figure;
Path=
DESKTOP_EOF

# Create README for the package
cat > "$DIST_DIR/README.txt" << 'README_EOF'
GestureMate - Standalone Package
=================================

To run GestureMate:

Method 1 (Recommended):
  Double-click the "GestureMate" executable

Method 2 (From terminal):
  ./GestureMate

Method 3 (Using launcher script):
  ./run-gesturemate.sh

Desktop Integration:
  To add GestureMate to your application menu:
  1. Edit the Path= line in gesturemate.desktop to point to this directory
  2. Copy gesturemate.desktop to ~/.local/share/applications/
  3. Run: chmod +x ~/.local/share/applications/gesturemate.desktop

Enjoy your gesture drawing practice!
README_EOF

echo ""
echo "========================================="
echo "✓ Packaging Complete!"
echo "========================================="
echo ""
echo "Executable location: $DIST_DIR/$APP_NAME"
echo "Package directory: $DIST_DIR/"
echo ""
echo "To run the application:"
echo "  cd $DIST_DIR"
echo "  ./$APP_NAME"
echo ""
echo "Or run the launcher script:"
echo "  $DIST_DIR/run-gesturemate.sh"
echo ""
