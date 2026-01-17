# Checkbox Propagation Feature

## How It Works

When you check or uncheck a parent folder, all its subfolders automatically follow the same state.

### Example 1: Checking a Parent Folder

**Before clicking the parent checkbox:**
```
┌──────────────────────────────────────┐
│ ☐ My References              │ 225  │  ← Parent unchecked
│   ├─ ☐ anatomy                │ 100  │
│   ├─ ☐ gestures               │ 75   │
│   └─ ☐ clothing               │ 50   │
└──────────────────────────────────────┘
```

**After clicking the parent checkbox to check it:**
```
┌──────────────────────────────────────┐
│ ☑ My References              │ 225  │  ← Parent now checked
│   ├─ ☑ anatomy                │ 100  │  ← Automatically checked
│   ├─ ☑ gestures               │ 75   │  ← Automatically checked
│   └─ ☑ clothing               │ 50   │  ← Automatically checked
└──────────────────────────────────────┘
```

All 225 images will be included in the session.

### Example 2: Unchecking a Parent Folder

**Before clicking the parent checkbox:**
```
┌──────────────────────────────────────┐
│ ☑ My References              │ 225  │  ← Parent checked
│   ├─ ☑ anatomy                │ 100  │
│   ├─ ☐ gestures               │ 75   │  ← This one was manually unchecked
│   └─ ☑ clothing               │ 50   │
└──────────────────────────────────────┘
```

**After clicking the parent checkbox to uncheck it:**
```
┌──────────────────────────────────────┐
│ ☐ My References              │ 225  │  ← Parent now unchecked
│   ├─ ☐ anatomy                │ 100  │  ← Automatically unchecked
│   ├─ ☐ gestures               │ 75   │  ← Also unchecked
│   └─ ☐ clothing               │ 50   │  ← Automatically unchecked
└──────────────────────────────────────┘
```

No images from this folder will be included in the session.

### Example 3: Selective Subfolder Control

You can still control individual subfolders independently:

```
┌──────────────────────────────────────┐
│ ☑ My References              │ 225  │  ← Parent checked
│   ├─ ☑ anatomy                │ 100  │  ← Included
│   ├─ ☐ gestures               │ 75   │  ← Manually unchecked - excluded
│   └─ ☑ clothing               │ 50   │  ← Included
└──────────────────────────────────────┘
```

In this case, the session will use 150 images (anatomy + clothing only).

**If you then click the parent checkbox:**

1. **Uncheck parent** → All subfolders become unchecked
2. **Check parent again** → All subfolders become checked (your previous manual selection is overridden)

## Benefits

- **Quick bulk selection**: Enable or disable entire folder trees with one click
- **Efficient workflow**: No need to manually check/uncheck each subfolder
- **Clear visual feedback**: Immediately see which folders will be included
- **Flexible control**: Can still fine-tune individual subfolders after bulk selection

## Technical Implementation

The feature uses PyQt6's `itemChanged` signal to detect when a checkbox state changes:

1. When a top-level folder's checkbox changes, the signal handler is triggered
2. The handler uses `blockSignals(True)` to prevent recursive signal emissions
3. All child items are updated to match the parent's state
4. Signals are unblocked using a try-finally block for safety
5. Child items can still be manually adjusted after propagation

This approach is safer than disconnect/reconnect when multiple signal handlers might be connected.
