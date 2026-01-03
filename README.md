# Whisper Auto Control

A modern, dark-mode GUI application for controlling Whisper voice transcription without needing to use the terminal.

## Features

- **Modern Dark UI** - Beautiful CustomTkinter interface with blue accents
- **One-Click Start/Stop** - Control Whisper process without terminal commands
- **Model Selection** - Switch between all Whisper models (tiny, base, small, medium, large, turbo)
- **Model Download** - Download missing models directly from the GUI
- **Real-Time Status** - Live process monitoring with PID and status display
- **Activity Log** - Timestamped log of all operations
- **System Tray Support** - Minimize to system tray with notifications and quick controls
- **Process Output Capture** - Real-time stdout/stderr display in expandable UI section
- **Enhanced Error Handling** - Validates paths, Python version, and provides actionable error messages
- **Persistent Settings** - Saves window geometry and configuration
- **Path Configuration** - Easy setup of Python interpreter and script paths

## Installation

### Prerequisites

- Windows 11 (or Windows 10)
- Python 3.8 or higher
- Existing Whisper installation at `C:\whisper`

### Setup

1. **Navigate to the project directory:**
   ```powershell
   cd C:\Users\erikc\Dev\MyWisperAuto
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

   This will install:
   - CustomTkinter (modern GUI framework)
   - OpenAI Whisper (speech-to-text engine)
   - PyTorch and TorchAudio (ML dependencies)
   - psutil (process management)
   - pystray (system tray support)
   - Pillow (image processing)
   - python-dotenv (configuration)

## Usage

### Running the Application

Simply run the main script:

```powershell
python main.py
```

### First-Time Setup

1. **Launch the application**
2. **Click "Configure Paths"**
3. **Set the following:**
   - **Python Interpreter**: `C:\whisper\venv\Scripts\python.exe`
   - **Whisper Script**: `C:\whisper\ptt_whisper.py`
4. **Click "Save"**

### Using Whisper

1. **Select a model** from the dropdown (base is recommended for balance of speed/accuracy)
2. **Click "START"** to launch Whisper
3. **Hold Spacebar** to record audio
4. **Release Spacebar** to transcribe (text will type at your cursor)
5. **Click "STOP"** when you're done

### Downloading Models

If you need a model that isn't installed:

1. **Select the model** from the dropdown
2. **Click "Download Model"**
3. **Wait for the download** to complete (progress shown in Activity Log)
4. **The model is now ready** to use

### Using System Tray

The application supports system tray functionality:

1. **Minimize to tray** - Window minimizes to system tray (configurable in settings)
2. **Tray menu** - Right-click the tray icon for quick controls:
   - Show/Hide window
   - Start/Stop Whisper
   - Exit application
3. **Notifications** - Receive system notifications when Whisper starts or stops

### Viewing Process Output

Monitor Whisper's real-time output:

1. **Expand output section** - Click "▼ Show" under "Process Output"
2. **View logs** - See timestamped stdout and stderr output
3. **Clear output** - Click "Clear" to reset the display
4. **Collapse when done** - Click "▲ Hide" to minimize the section

## Whisper Models Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| **tiny** | 39M | Fastest | Low | Quick tests, low resources |
| **base** | 74M | Very Fast | Good | Daily use, recommended |
| **small** | 244M | Fast | Better | Good accuracy needs |
| **medium** | 769M | Moderate | High | High accuracy priority |
| **large** | 1550M | Slow | Best | Maximum accuracy |
| **turbo** | ~800M | Fast | High | Near-large quality, faster |

**Recommendation**: Start with **base** for good balance, upgrade to **small** or **medium** if you need better accuracy.

## Configuration

The application stores configuration in `~/.whisper_auto/config.json`:

```json
{
    "selected_model": "base",
    "auto_start": false,
    "minimize_to_tray": false,
    "log_level": "INFO",
    "python_path": "C:\\whisper\\venv\\Scripts\\python.exe",
    "script_path": "C:\\whisper\\ptt_whisper.py",
    "window_geometry": "600x500",
    "window_position": null
}
```

## File Structure

```
MyWisperAuto/
├── main.py                 # GUI application entry point
├── config.py               # Configuration management
├── whisper_controller.py   # Process control backend
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### Application Won't Start

1. **Check Python installation:**
   ```powershell
   python --version
   ```
   Should be Python 3.8+

2. **Verify dependencies:**
   ```powershell
   pip list | findstr customtkinter
   ```

3. **Check Whisper installation:**
   ```powershell
   dir C:\whisper
   ```

### Whisper Process Won't Start

1. **Check error messages** - The application now provides detailed validation:
   - Script path configured and exists
   - Python interpreter exists and is executable
   - Python version is 3.8 or higher
   - Error messages include "Action:" suggestions

2. **Verify paths in "Configure Paths":**
   - Python interpreter should exist and be python.exe
   - Whisper script should exist and be a .py file

3. **Check Activity Log** for detailed error messages

4. **Test Whisper manually:**
   ```powershell
   cd C:\whisper
   .\venv\Scripts\Activate.ps1
   python ptt_whisper.py
   ```

### Model Download Fails

1. **Check internet connection**
2. **Verify Python has internet access**
3. **Try downloading manually:**
   ```powershell
   cd C:\whisper
   .\venv\Scripts\Activate.ps1
   python -c "import whisper; whisper.load_model('base')"
   ```

## Development

### Architecture

- **config.py** - Handles JSON configuration persistence, path management, and default settings
- **whisper_controller.py** - Manages Whisper process lifecycle using psutil for robust process control
- **main.py** - CustomTkinter GUI with threading for async operations

### Key Design Decisions

1. **Threading** - All long-running operations (start, stop, download) run in background threads to prevent UI freezing
2. **Status Updates** - Background thread updates status every 500ms for real-time monitoring
3. **Process Management** - Uses psutil for cross-platform process control with graceful shutdown
4. **Configuration** - Persistent JSON storage in user's home directory

## Credits

Built with:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition engine
- [psutil](https://github.com/giampaolo/psutil) - Process management

## License

This project is open source and available for personal and educational use.

## Support

For issues or questions:
1. Check the Activity Log in the application
2. Review the Troubleshooting section above
3. Verify your Whisper installation is working manually

---

**Version:** 1.1.0
**Author:** Erik (erikchvac-byte)
**Last Updated:** January 2, 2026

## Recent Updates

### Version 1.1.0 (January 2, 2026)
- ✅ Added system tray support with notifications
- ✅ Added real-time process output capture and display
- ✅ Enhanced error handling with path and Python version validation
- ✅ Improved user experience with actionable error messages
