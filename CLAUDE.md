# Claude Code Instructions - Whisper Auto Control

## Project Overview
Whisper Auto Control is a modern, dark-mode GUI application for controlling OpenAI Whisper voice transcription without requiring terminal usage.

## Development Guidelines

### Code Quality Standards
- Use TypeScript strict mode for any TypeScript code
- Write tests for everything (unit tests required)
- Follow Python PEP 8 style guidelines
- All classes and public methods must have docstrings
- Use type hints throughout the codebase
- Thread all I/O operations to prevent UI freezing

### Testing Requirements
- Unit tests for all new features
- Integration tests for process management
- Mock subprocess calls in tests
- Test cross-platform compatibility

### Architecture Principles
- **config.py** - Configuration management with JSON persistence
- **whisper_controller.py** - Process lifecycle management
- **main.py** - CustomTkinter GUI with async threading
- All long-running operations run in background threads
- Use callback-based logging to GUI
- Graceful shutdown with timeouts

---

## Forward-Facing Roadmap

### Current Version: 1.2.0 (January 3, 2026)

### High Priority Features

#### 1. Bug Hunting and Fixes
**Status**: Next up
**Description**: Systematic bug identification and resolution
- Search for edge cases in process management
- Validate error handling paths
- Test model switching scenarios
- Verify thread cleanup on all exit paths
- Check for memory leaks in long-running sessions

#### 2. Working Indicator for Processing
**Status**: Planned
**Description**: Clear visual feedback during transcription
- Add animated indicator when Whisper is processing audio
- Show "Listening..." state when spacebar is held
- Display "Transcribing..." state during processing
- Add progress spinner or pulsing animation
- Ensure indicator is visible and non-intrusive

#### 3. Enable CUDA GPU Acceleration (Optional)
**Status**: Documented, awaiting user decision
**Description**: Leverage RTX 3060 Ti for faster transcription
- Reinstall PyTorch with CUDA 12.6 support
- Modify ptt_whisper.py to use `--device cuda`
- Expected 6-10x speedup over CPU
- See [CUDA_OPTIMIZATION.md](CUDA_OPTIMIZATION.md) for full instructions

### Medium Priority Features

#### 4. UI Dashboard Cleanup
**Status**: Planned
**Description**: Achieve appliance-style dashboard aesthetic
- Simplify control layout
- Enhance visual hierarchy
- Add status indicators with better visibility
- Improve spacing and alignment
- Consider card-based layout for sections

#### 5. Keyboard Shortcuts
**Status**: Not started
**Description**: Add keyboard shortcuts for common actions
- `Ctrl+S`: Start Whisper
- `Ctrl+Q`: Stop Whisper
- `Ctrl+R`: Restart Whisper
- `Ctrl+D`: Download current model
- `Ctrl+P`: Configure paths

#### 6. Enhanced Model Download UI
**Status**: Not started
**Description**: Better feedback during model downloads
- Progress bar for downloads
- Download speed indicator
- Estimated time remaining
- Model size information in dropdown
- Cancel download option

### Low Priority Features

#### 7. Auto-detection of Whisper Installation
**Status**: Not started
**Description**: Automatic discovery of Whisper installation
- Scan common installation paths
- Detect virtual environment automatically
- Validate installation on first run
- Suggest installation if not found

#### 8. Cross-platform Support
**Status**: Not started
**Description**: Expand beyond Windows
- Linux support
- macOS support
- Platform-specific path handling
- Unified testing across platforms

#### 9. Additional Features
**Status**: Ideas for future consideration
- Model comparison table in GUI
- Export activity log to file
- Custom hotkey configuration for Whisper (beyond spacebar)
- Language selection for transcription
- Multiple microphone support
- Audio device selection in GUI

---

## Technical Debt

### Known Issues
- Paths are hardcoded to Windows (`C:\whisper\`)
- No validation of Whisper installation before first run
- Model switching requires stopping and restarting
- No progress indicator during startup
- Auto-start setting exists but not implemented

### Code Improvements Needed
- Add unit test coverage
- Add integration tests
- Improve type hint coverage
- Better error message localization
- Add logging to file (not just GUI)

---

## Routing Policy (Ollama/Claude)
**See [ROUTING_POLICY.md](ROUTING_POLICY.md) for full details**

**Current Strategy**: Auto-route with Ollama-first (qwen3-coder:30b), escalate to Claude Sonnet 4.5 when needed

**Guidelines**:
- Use Ollama for straightforward coding tasks
- Use Claude for complex architecture, debugging loops, or high-stakes features
- Target ≥80% Ollama usage for cost efficiency
- Monitor override rate (keep ≤15%)

---

## Quick Start Commands

### Run the application
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

### Install dependencies
```powershell
pip install -r requirements.txt
```

### Run tests (when available)
```powershell
pytest tests/
```

---

## File Encoding Rules
- Always use UTF-8 encoding for text files
- Never use PowerShell `Out-File` (defaults to UTF-16)
- Use bash heredoc for file creation in Git Bash
- Verify encoding with `file` command

---

## Contact
**Developer**: Erik (erikchvac-byte@users.noreply.github.com)
**Version**: 1.2.0
**Last Updated**: January 5, 2026
