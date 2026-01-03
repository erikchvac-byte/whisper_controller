# CUDA Optimization (Future Enhancement)

## Current Status: ✅ Working on CPU

The transcription is **currently working on CPU mode**. Don't change anything until you want faster performance.

## Your Hardware

- **GPU**: NVIDIA GeForce RTX 3060 Ti
- **CUDA Cores**: 4,864
- **CUDA Version**: 12.6 (driver installed)
- **Architecture**: Ampere

## The Issue

PyTorch in your `C:\whisper\venv` was installed **without CUDA support**. This is why `torch.cuda.is_available()` returns `False` even though you have a GPU.

## How to Enable CUDA (When Ready)

### Step 1: Check Current PyTorch Installation

```powershell
cd C:\whisper
.\venv\Scripts\Activate.ps1
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

Expected output currently:
```
PyTorch: 2.x.x+cpu
CUDA: False
```

### Step 2: Reinstall PyTorch with CUDA Support

**IMPORTANT**: This will reinstall PyTorch and may take 10-20 minutes.

```powershell
cd C:\whisper
.\venv\Scripts\Activate.ps1

# Uninstall current PyTorch
pip uninstall torch torchvision torchaudio

# Install PyTorch with CUDA 12.6 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

### Step 3: Verify CUDA Works

```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

Expected output after fix:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060 Ti
```

### Step 4: Re-enable CUDA in Script

Edit `C:\whisper\ptt_whisper.py` line 63:
```python
# Change from:
"--device", "cpu",

# Back to:
"--device", "cuda",
```

## Performance Comparison

With your RTX 3060 Ti:

| Model | CPU Time | GPU Time (Est.) | Speedup |
|-------|----------|-----------------|---------|
| tiny  | ~3s      | ~0.5s          | 6x      |
| base  | ~5s      | ~0.8s          | 6x      |
| small | ~10s     | ~1.5s          | 7x      |
| medium| ~25s     | ~3s            | 8x      |
| large | ~60s     | ~6s            | 10x     |

## Why It Failed Initially

The PyTorch package installed in your venv was the **CPU-only version** (`torch+cpu`), not the CUDA version (`torch+cu126`). This happens when:

1. PyTorch is installed via `pip install torch` (defaults to CPU)
2. Instead of `pip install torch --index-url https://download.pytorch.org/whl/cu126`

## When to Optimize

Enable CUDA when:
- ✅ Current CPU transcription is too slow for you
- ✅ You have 10-20 minutes for the PyTorch reinstall
- ✅ You're comfortable testing after the change

## Rollback Plan

If enabling CUDA breaks anything:

```powershell
cd C:\whisper
.\venv\Scripts\Activate.ps1
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio

# Then change ptt_whisper.py back to "cpu"
```

## Current Working Configuration

**DO NOT CHANGE** until ready:
- ✅ `ptt_whisper.py` line 63: `"--device", "cpu"`
- ✅ PyTorch: CPU-only version
- ✅ Transcription: Working (slower but reliable)

---

**Last Updated**: 2026-01-03
**Status**: CPU mode working, CUDA optimization deferred
