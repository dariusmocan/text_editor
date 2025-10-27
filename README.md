# Text Editor (Tkinter)

A lightweight, tabbed text editor built with Python's Tkinter. It supports multiple tabs, windows, saving and opening existing .txt files,  standard editing operations, a handy Find dialog, and a customization window for fonts, styles, sizes, and colors. Font and color preferences are saved and automatically reused.

## Features

- Multiple tabs
- Standard file operations: Open, Save, Save As
- Window management: New Tab, Close Tab, New Window, Close Window, Exit All
- Edit operations: Undo, Redo, Copy, Paste, Cut, Select All
- Find dialog with Find Next / Find Previous and match highlighting
- Customization window:
  - Font family selection
  - Style toggles (Normal, Bold, Italic)
  - Font size
  - Text color and background color pickers
- Auto-persistent preferences (font family, size, weight, slant, fg/bg colors) saved in `font.json`
- Unsaved changes indicator: an asterisk `*` on the tab title
- Helpful text navigation:
  - Ctrl+Left moves to beginning of the pervious word
  - Ctrl+Right moves to end of the current/next word
  - Ctrl+Backspace deletes the whole previous word

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Open File | Ctrl + O |
| Save | Ctrl + S |
| Save As | Ctrl + Shift + S |
| New Tab | Ctrl + N |
| Close Tab | Ctrl + W |
| New Window | Ctrl + Shift + N |
| Close Window | Ctrl + Shift + W |
| Exit All | (via File menu) |
| Undo | Ctrl + Z |
| Redo | Ctrl + Y |
| Copy | Ctrl + C |
| Paste | Ctrl + V |
| Cut | Ctrl + X |
| Select All | Ctrl + A |
| Find | Ctrl + F |
| Move to end of word | Ctrl + Right |
| Delete whole previous word | Ctrl + Backspace |

Note: If a shortcut doesn’t trigger in your environment, use the corresponding menu item.

## Requirements

- Python (preferably 10+)
- Tkinter (bundled with the standard Python installer on Windows/macOS; on some Linux distros you may need to install it separately, e.g., `python3-tk`).

No third-party packages are required.

## Getting Started

### Run (Windows PowerShell)

```powershell
# From the project directory
python .\text_editor.py
```

Optional (use a virtual environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python .\text_editor.py
```

### Run (macOS/Linux)

```bash
python3 text_editor.py
```

## Usage

- File menu:
  - Open an existing text file, Save current file, or Save As a new file.
  - Create a New Tab or a New Window.
  - Close the current Tab or Window, or Exit All windows.
- Edit menu:
  - Undo/Redo, Copy/Paste/Cut, Select All, and open the Find dialog.
- Custom menu:
  - Open the customization window to adjust font family, style (Normal/Bold/Italic), size, and colors (text/background).
- Find dialog:
  - Enter the search term and use Find Next or Find Prev to jump between matches; matches are highlighted.
- Unsaved changes:
  - Tabs with unsaved changes show an asterisk `*` in the title. Closing a tab or window with unsaved changes prompts you to save.

## Preferences and Persistence

- Preferences are stored in `font.json` in the project directory.
- When you open the customization window and close it, settings (font family, size, weight, slant, text color, background color) are saved automatically.
- New tabs load these preferences on creation.


