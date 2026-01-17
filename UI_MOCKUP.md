# UI Mockup - Enhanced Folder Picker

This document shows what the enhanced folder picker looks like.

## Settings Dialog - Folder Selection Section

```
┌────────────────────────────────────────────────────────────────┐
│ Session Settings                                        [X]    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Image Folders                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Folder                                        │ Images    │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ ☑ My References                              │ 150       │ │
│  │   ├─ ☑ Poses                                 │ 50        │ │
│  │   ├─ ☑ Hands                                 │ 35        │ │
│  │   ├─ ☐ Faces (unchecked)                     │ 40        │ │
│  │   └─ ☑ Animals                               │ 25        │ │
│  │ ☑ Photo References                           │ 75        │ │
│  │   ├─ ☑ Studio Shots                          │ 45        │ │
│  │   └─ ☑ Outdoor                               │ 30        │ │
│  │                                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  [Add Folder]  [Remove Selected]                              │
│                                                                │
│  Timer Settings                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Duration per image:       [60] seconds                   │ │
│  │ Total session duration:   [30] minutes                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Session Options                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ☑ Shuffle images                                         │ │
│  │ ☑ Play sound halfway through each image                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│                                          [OK]  [Cancel]        │
└────────────────────────────────────────────────────────────────┘
```

## Key Features Illustrated

1. **Tree Structure**: Folders can be expanded/collapsed (indicated by ├─ and └─)
2. **Checkboxes**: Each folder and subfolder has an independent checkbox (☑/☐)
3. **Image Counts**: Right column shows exact number of images in each folder
4. **Recursive Counts**: Parent folders show total images including all subfolders
5. **Visual Hierarchy**: Indentation clearly shows parent-child relationships

## User Workflows

### Adding a Folder with Subfolders

```
User Action: Click "Add Folder" → Select "/home/user/art-references"

Result:
┌──────────────────────────────────────────────────────────┐
│ ☑ art-references                             │ 225       │
│   ├─ ☑ anatomy                               │ 100       │
│   ├─ ☑ gestures                              │ 75        │
│   └─ ☑ clothing                              │ 50        │
└──────────────────────────────────────────────────────────┘
```

All subfolders are automatically discovered and checked by default.

### Selectively Disabling Subfolders

```
User Action: Uncheck "clothing" subfolder

Result:
┌──────────────────────────────────────────────────────────┐
│ ☑ art-references                             │ 225       │
│   ├─ ☑ anatomy                               │ 100       │
│   ├─ ☑ gestures                              │ 75        │
│   └─ ☐ clothing                              │ 50        │
└──────────────────────────────────────────────────────────┘

Session will use: anatomy (100) + gestures (75) = 175 images
```

Only checked folders are included in the session.

### Removing a Subfolder

```
User Action: Select "clothing" → Click "Remove Selected"

Result:
┌──────────────────────────────────────────────────────────┐
│ ☑ art-references                             │ 225       │
│   ├─ ☑ anatomy                               │ 100       │
│   └─ ☑ gestures                              │ 75        │
└──────────────────────────────────────────────────────────┘
```

The subfolder is removed from the tree but still exists on disk.

## Benefits

- **At-a-glance information**: See exactly how many images you're working with
- **Granular control**: Pick and choose specific subfolders
- **Organized view**: Maintain your folder structure in the UI
- **Quick setup**: Auto-discovery of subfolders saves time
