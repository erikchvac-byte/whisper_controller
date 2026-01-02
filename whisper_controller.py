"""
Whisper process controller for managing Whisper Auto transcription service.
Handles process lifecycle, status monitoring, and model downloads.
"""

import subprocess
import os
import sys
import time
import psutil
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from config import config


class WhisperController:
    """Controller for Whisper Auto process management."""

    def __init__(self):
        """Initialize Whisper controller."""
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.status_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for status updates."""
        self.status_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for log messages."""
        self.log_callback = callback

    def _log(self, message: str) -> None:
        """Send log message to callback."""
        if self.log_callback:
            self.log_callback(message)

    def _update_status(self, status: str) -> None:
        """Send status update to callback."""
        if self.status_callback:
            self.status_callback(status)

    def is_running(self) -> bool:
        """Check if Whisper process is running."""
        if self.pid is None:
            return False

        try:
            process = psutil.Process(self.pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def start(self, model: Optional[str] = None) -> bool:
        """
        Start Whisper Auto process.

        Args:
            model: Whisper model to use (tiny, base, small, medium, large, turbo)

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running():
            self._log("Error: Whisper is already running")
            return False

        script_path = config.get_script_path()
        if not script_path or not os.path.exists(script_path):
            self._log("Error: Whisper script path not configured or invalid")
            return False

        python_path = config.get_python_path()
        if not os.path.exists(python_path):
            self._log(f"Error: Python interpreter not found at {python_path}")
            return False

        model = model or config.get_selected_model()

        try:
            # Construct command
            cmd = [python_path, script_path]

            self._log(f"Starting Whisper with model: {model}")
            self._log(f"Command: {' '.join(cmd)}")

            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            self.pid = self.process.pid

            # Wait a moment to check if it started successfully
            time.sleep(0.5)

            if self.is_running():
                self._log(f"Whisper started successfully (PID: {self.pid})")
                self._update_status("Running")
                return True
            else:
                self._log("Error: Whisper process terminated immediately")
                self.pid = None
                self.process = None
                return False

        except Exception as e:
            self._log(f"Error starting Whisper: {str(e)}")
            self.process = None
            self.pid = None
            return False

    def stop(self) -> bool:
        """
        Stop Whisper Auto process.

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_running():
            self._log("Whisper is not running")
            return False

        try:
            self._log(f"Stopping Whisper (PID: {self.pid})")

            process = psutil.Process(self.pid)

            # Try graceful termination first
            process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                process.wait(timeout=5)
                self._log("Whisper stopped successfully")
            except psutil.TimeoutExpired:
                # Force kill if necessary
                self._log("Force killing Whisper process")
                process.kill()
                process.wait(timeout=2)
                self._log("Whisper force stopped")

            self.pid = None
            self.process = None
            self._update_status("Stopped")
            return True

        except Exception as e:
            self._log(f"Error stopping Whisper: {str(e)}")
            return False

    def restart(self, model: Optional[str] = None) -> bool:
        """
        Restart Whisper Auto process.

        Args:
            model: Whisper model to use

        Returns:
            True if restarted successfully, False otherwise
        """
        self._log("Restarting Whisper...")

        if self.is_running():
            if not self.stop():
                return False
            time.sleep(1)

        return self.start(model)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status information.

        Returns:
            Dictionary with status information
        """
        running = self.is_running()

        status = {
            'running': running,
            'pid': self.pid if running else None,
            'model': config.get_selected_model(),
            'python_path': config.get_python_path(),
            'script_path': config.get_script_path(),
            'status_text': 'Running' if running else 'Stopped'
        }

        if running and self.pid:
            try:
                process = psutil.Process(self.pid)
                status['memory_mb'] = process.memory_info().rss / 1024 / 1024
                status['cpu_percent'] = process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return status

    def download_model(self, model: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download Whisper model.

        Args:
            model: Model name to download
            progress_callback: Optional callback for progress updates

        Returns:
            True if download successful, False otherwise
        """
        if model not in config.WHISPER_MODELS:
            self._log(f"Error: Invalid model '{model}'")
            return False

        try:
            self._log(f"Downloading Whisper model: {model}")

            if progress_callback:
                progress_callback(f"Preparing to download {model} model...")

            # Import whisper to trigger model download
            python_path = config.get_python_path()

            cmd = [
                python_path,
                '-c',
                f'import whisper; whisper.load_model("{model}")'
            ]

            self._log(f"Running: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    self._log(line)
                    if progress_callback:
                        progress_callback(line)

            process.wait()

            if process.returncode == 0:
                self._log(f"Model '{model}' downloaded successfully")
                if progress_callback:
                    progress_callback(f"Model '{model}' downloaded successfully!")
                return True
            else:
                self._log(f"Error downloading model (exit code: {process.returncode})")
                return False

        except Exception as e:
            self._log(f"Error downloading model: {str(e)}")
            if progress_callback:
                progress_callback(f"Error: {str(e)}")
            return False


# Global controller instance
controller = WhisperController()
