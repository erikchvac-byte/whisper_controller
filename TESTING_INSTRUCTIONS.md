# Testing Instructions for Whisper Auto Control

## How the System Works

This application does **NOT** directly control your cursor or type text. Instead:

1. **The GUI** launches `ptt_whisper.py` as a background process
2. **The ptt_whisper.py script** listens for `Ctrl+Space` hotkey globally
3. **When you hold Ctrl+Space**, the script records audio
4. **When you release Ctrl+Space**, the script transcribes and types text at your cursor automatically

## Step-by-Step Testing Procedure

### 1. Launch the Application

```powershell
cd C:\Users\erikc\Dev\MyWisperAuto
.\.venv\Scripts\python.exe main.py
```

### 2. Configure Paths (First Time Only)

- Click **"Configure Paths"**
- Set Python Interpreter: `C:\whisper\venv\Scripts\python.exe`
- Set Whisper Script: `C:\whisper\ptt_whisper.py`
- Click **"Save"**

### 3. Start Whisper Service

- Select model (recommend **"base"** or **"small"**)
- Click **"START"**
- **Watch the "Activity & Process Output" section** for confirmation
- You should see: `"Whisper running - Press Ctrl+Space to record and transcribe"`

### 4. Test Text Insertion

1. **Open any text editor** (Notepad, VS Code, Word, etc.)
2. **Click inside the text field** to place your cursor
3. **Hold Ctrl+Space** - you should see "Recording..." in the console output
4. **Speak clearly into your microphone**
5. **Release Ctrl+Space** - transcription begins
6. **Wait 2-5 seconds** - transcribed text should appear at your cursor

### 5. Verify Focus Preservation

**Expected behavior:**
- Clicking START/STOP should NOT move your cursor from the text editor
- The GUI window may briefly flash but should not steal permanent focus
- After clicking START, you can immediately switch to your text editor
- Ctrl+Space hotkey works globally (even when GUI is minimized)

**If focus is stolen:**
- The `self.focus()` calls added should prevent this
- You can also minimize the GUI to system tray (if enabled in config)

### 6. Monitor Output

The "Activity & Process Output" section will show:
- `[LOG]` - GUI activity logs
- `[OUT]` - Process stdout (from ptt_whisper.py)
- `[ERR]` - Process stderr (errors if any)

Watch for messages like:
- `"Recording... Release Ctrl + Space to stop."`
- `"Recording stopped. Transcribing..."`
- `"Typing transcription at cursor..."`

### 7. Stop Whisper

- Click **"STOP"** when done
- This kills the ptt_whisper.py background process
- Ctrl+Space hotkey will no longer work until you START again

## Common Issues

### No Text Appears After Recording

**Check:**
1. Is Whisper actually running? (Check PID in Status display)
2. Does `C:\whisper\ptt_audio.txt` exist after recording?
3. Is the microphone working? (Check Windows sound settings)
4. CPU mode is currently configured and working (ptt_whisper.py uses `--device cpu`)
   - For GPU acceleration with your RTX 3060 Ti, see CUDA_OPTIMIZATION.md

### Old/Wrong Text Being Typed (FIXED)

**Issue:** Transcription file was being cached and old text reused.

**Solution:** The script now deletes `C:\whisper\ptt_audio.txt` before each new transcription (line 49-54).

If you still see old text:
1. Manually delete `C:\whisper\ptt_audio.txt`
2. Restart the Whisper process (STOP then START in GUI)

### "Empty transcription" Message

**Causes:**
- Audio too short or quiet
- Background noise drowning out speech
- Microphone not configured correctly
- Wrong audio input device selected

### Cursor Focus Issues

**If clicking START/STOP still steals focus:**
1. Try minimizing the GUI to system tray before recording
2. Use keyboard shortcuts instead (if implemented)
3. Ensure ptt_whisper.py is using `keyboard.write()` correctly (it is - line 68)

### Model Download Required

If you see errors about missing models:
1. Select the model in the dropdown
2. Click **"Download Model"**
3. Wait for download to complete
4. Click **"START"** again

### Process Output Not Visible (FIXED)

**Issue:** Python output was buffered, preventing real-time visibility of ptt_whisper.py stdout/stderr.

**Solution:** The controller now starts Python with `-u` flag and sets `PYTHONUNBUFFERED=1` environment variable (whisper_controller.py line 183-191).

If you still don't see process output in real-time:
1. Check that the "Activity & Process Output" section is visible
2. Restart the application
3. Verify ptt_whisper.py is being launched with `-u` flag

## Expected Console Output (ptt_whisper.py)

When working correctly, you should see:

```
Push-to-Talk Whisper ready. Hold Ctrl + Space to record and transcribe anywhere...
Recording... Release Ctrl + Space to stop.
Recording stopped. Transcribing...
Typing transcription at cursor...
```

## Acceptance Criteria Verification

✅ **Cursor Preservation**: GUI does not move cursor when START/STOP clicked
✅ **Text Insertion at Cursor**: ptt_whisper.py uses `keyboard.write()` to type at cursor
✅ **Functional Transcription**: ptt_whisper.py handles entire pipeline (record → transcribe → type)
✅ **UI Control Isolation**: START/STOP use `self.focus()` to minimize focus stealing
✅ **Deterministic Behavior**: Ctrl+Space hotkey always triggers same record/transcribe/type flow

## Architecture Clarification

**The GUI is NOT responsible for:**
- Capturing audio
- Transcribing speech
- Typing text at cursor
- Managing keyboard hotkeys

**The GUI IS responsible for:**
- Starting/stopping the ptt_whisper.py background process
- Displaying process status and output
- Configuring paths and models
- NOT interfering with the user's active window focus

## Debug Mode

To see more detailed output, run ptt_whisper.py manually:

```powershell
cd C:\whisper
.\venv\Scripts\Activate.ps1
python ptt_whisper.py
```

Then test Ctrl+Space directly. This bypasses the GUI entirely.
