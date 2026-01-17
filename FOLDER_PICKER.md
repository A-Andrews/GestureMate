# Enhanced Folder Picker Feature

## Overview

The folder picker in GestureMate has been enhanced to provide detailed information about image counts and subfolder structure. This makes it easier to manage large image collections organized in hierarchical folder structures.

## New Features

### 1. Tree View with Image Counts

- **Before**: Folders were shown in a simple list
- **After**: Folders are displayed in a tree structure with expandable/collapsible nodes
- Each folder and subfolder shows the exact number of images it contains (recursively)

### 2. Subfolder Management

When you add a folder:
- All subfolders containing images are automatically discovered
- Subfolders are shown as child nodes in the tree
- Each subfolder has its own checkbox for selective inclusion/exclusion
- Image counts are displayed for both parent folders and subfolders

### 3. Detailed Image Counting

The folder picker now shows two columns:
- **Folder**: The folder/subfolder name
- **Images**: The number of images in that folder (including all descendants)

### 4. Persistent State

- Folder selections are remembered between sessions
- Subfolder checkbox states are also saved
- The tree structure is rebuilt on reload, showing your previously selected folders

## How to Use

### Adding a Folder

1. Click "Settings" (Ctrl+S)
2. Click "Add Folder"
3. Select a folder containing images
4. The folder will appear in the tree with:
   - Total image count
   - All subfolders that contain images
   - Checkboxes for each folder/subfolder

### Managing Subfolders

- Click the arrow/triangle next to a folder to expand/collapse it
- Uncheck any subfolder you want to exclude from the session
- Keep the parent folder checked if you want images from the parent folder itself

### Removing Folders

1. Select a folder or subfolder in the tree
2. Click "Remove Selected"
3. If you remove a parent folder, all its subfolders are also removed
4. If you remove a subfolder, only that subfolder is removed

## Example Folder Structure

```
📁 My References (9 images)
  ├─ 📁 Poses (5 images)
  ├─ 📁 Hands (2 images)
  └─ 📁 Faces (2 images)
```

In this example:
- "My References" contains 9 images total (including all subfolders)
- You can selectively enable/disable Poses, Hands, or Faces
- Each subfolder shows its individual image count

## Technical Details

### Supported Image Formats

The folder picker counts the following image formats:
- JPG/JPEG
- PNG
- BMP
- GIF
- WEBP

### Recursive Counting

Image counts include:
- Images directly in the folder
- Images in all subfolders
- Images in sub-subfolders (and so on)

### Performance

- Image counting is done when you add a folder or load saved settings
- Large folder hierarchies may take a moment to scan
- Counts are cached during the session

## Benefits

1. **Better Organization**: See your entire image collection hierarchy at a glance
2. **Precise Control**: Enable/disable specific subfolders without affecting others
3. **Informed Decisions**: Know exactly how many images you're working with
4. **Flexibility**: Mix and match folders and subfolders from different locations

## Backward Compatibility

- Existing saved folder configurations will be migrated automatically
- Simple folder selections (without subfolders) continue to work as before
- You can still add folders without subfolders
