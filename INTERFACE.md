# GestureMate Interface Guide

## Application Layout

### Main Window

The GestureMate window consists of three main areas:

```
┌─────────────────────────────────────────────────────────────┐
│ File                                            Help         │ Menu Bar
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                                                               │
│                                                               │
│                                                               │
│                     IMAGE DISPLAY AREA                        │
│                  (Dark gray background)                       │
│                                                               │
│                                                               │
│                                                               │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Image: 01:30              Session: 28:45                     │ Timers
│ [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15%          │ Progress
│ [Start Session] [Pause] [Next Image] [Stop]                 │ Controls
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Menu Bar** (Top)
   - File menu: Settings (Ctrl+S), Exit (Ctrl+Q)
   - Help menu: About

2. **Image Display Area** (Center)
   - Large dark gray canvas
   - Reference image centered and scaled to fit
   - Maintains aspect ratio

3. **Timer Display** (Bottom)
   - Left: Current image timer (MM:SS)
   - Right: Total session timer (MM:SS)
   - Bold, white text on dark background

4. **Progress Bar**
   - Visual indicator of session completion
   - Updates in real-time

5. **Control Buttons**
   - Start Session: Begin a new drawing session
   - Pause: Pause/Resume the current session
   - Next Image: Skip to next reference
   - Stop: End the session early

## Settings Dialog

```
┌─────────────────────────────────────────────────────┐
│                  Session Settings            [X]    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Image Folders                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │ /home/user/images/poses                        │ │
│  │ /home/user/images/hands                        │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│  [Add Folder]  [Remove Selected]                    │
│                                                      │
│  Timer Settings                                      │
│  Duration per image:      [  60  ▼] seconds         │
│  Total session duration:  [  30  ▼] minutes         │
│                                                      │
│                              [  OK  ]  [ Cancel ]   │
└─────────────────────────────────────────────────────┘
```

### Settings Features

1. **Folder List**
   - Shows all selected image folders
   - Scrollable if many folders are added
   - Click to select for removal

2. **Folder Management**
   - Add Folder: Opens folder browser dialog
   - Remove Selected: Removes highlighted folder

3. **Timer Controls**
   - Spin boxes for easy adjustment
   - Clear labels with units (seconds/minutes)
   - Reasonable min/max ranges

## Color Scheme

The application uses a professional dark theme:

- **Background:** Dark gray (#353535)
- **Text:** White
- **Highlights:** Blue (#2A82DA)
- **Image Background:** Darker gray (#2B2B2B)
- **Buttons:** Medium gray (#353535)

This reduces eye strain during long drawing sessions and keeps focus on the reference image.

## Window Behavior

- **Starts Maximized:** Opens in fullscreen for maximum image size
- **Resizable:** Can be resized, images automatically rescale
- **Responsive:** All UI elements adjust to window size
- **No Distraction:** Minimal UI during sessions

## User Flow

1. **First Launch**
   ```
   Launch App → Empty screen → Click Settings (or Ctrl+S)
   → Add folders → Set timers → OK
   → Click Start Session → Drawing begins!
   ```

2. **During Session**
   ```
   Image displayed → Timer counts down
   → Auto-advance to next image
   → Repeat until session ends
   ```

3. **Session Controls**
   ```
   Pause → Take break → Resume when ready
   Next → Skip current image → Continue
   Stop → End early → Return to ready state
   ```

## Accessibility

- Large, readable fonts (18px for timers)
- High contrast dark theme
- Clear button labels
- Keyboard shortcuts for common actions
- Intuitive icon usage (where applicable)

## Performance

- Smooth image transitions
- Efficient memory usage
- No lag during timer updates
- Quick startup time
- Handles large image collections

## Platform Notes

### Linux
- Native Qt6 integration
- Follows system theme where appropriate
- Standard Linux file dialogs
- Desktop integration via .desktop file

### Window Management
- Works with any window manager
- Fullscreen/maximize supported
- Stays on top option available (via window manager)
