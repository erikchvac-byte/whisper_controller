"""
Whisper process controller for managing Whisper Auto transcription service.
Handles process lifecycle, status monitoring, and model downloads.
"""

import subprocess
import os
import sys
import time
import threading
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
        self.process_output_callback: Optional[Callable] = None
        self.output_threads: list = []
        self.stop_output_reading = False

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for status updates."""
        self.status_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for log messages."""
        self.log_callback = callback

    def set_process_output_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for process output messages.

        Args:
            callback: Function accepting (stream_type, message) where stream_type is 'stdout' or 'stderr'
        """
        self.process_output_callback = callback

    def _log(self, message: str) -> None:
        """Send log message to callback."""
        if self.log_callback:
            self.log_callback(message)

    def _update_status(self, status: str) -> None:
        """Send status update to callback."""
        if self.status_callback:
            self.status_callback(status)

    def _read_output_stream(self, stream, stream_name: str) -> None:
        """Read output from a process stream in a background thread.

        Args:
            stream: The stream to read from (stdout or stderr)
            stream_name: Name of the stream ('stdout' or 'stderr')
        """
        try:
            for line in iter(stream.readline, b''):
                if self.stop_output_reading:
                    break

                # Decode and strip the line
                try:
                    decoded_line = line.decode('utf-8', errors='replace').rstrip()
                except Exception:
                    decoded_line = str(line).rstrip()

                # Only send non-empty lines
                if decoded_line:
                    if self.process_output_callback:
                        self.process_output_callback(stream_name, decoded_line)
                    # Also log to main log for debugging
                    self._log(f"[{stream_name.upper()}] {decoded_line}")

        except Exception as e:
            self._log(f"Error reading {stream_name}: {str(e)}")
        finally:
            # Ensure stream is closed
            try:
                stream.close()
            except Exception:
                pass

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
        if not script_path:
            self._log("Error: Whisper script path not configured")
            self._log("Action: Click 'Configure Paths' to set the script location")
            return False

        if not os.path.exists(script_path):
            self._log(f"Error: Whisper script not found at {script_path}")
            self._log("Action: Verify the file exists or update the path")
            return False

        if not script_path.endswith('.py'):
            self._log(f"Error: Script must be a .py file. Found: {script_path}")
            self._log("Action: Select a valid Python script file")
            return False

        python_path = config.get_python_path()
        if not os.path.exists(python_path):
            self._log(f"Error: Python interpreter not found at {python_path}")
            self._log("Action: Install Python or update the interpreter path")
            return False

        if not os.access(python_path, os.X_OK):
            self._log(f"Error: Python interpreter at {python_path} is not executable")
            self._log("Action: Verify file permissions or select python.exe")
            return False

        # Check Python version
        try:
            result = subprocess.run(
                [python_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_line = result.stdout.strip() if result.stdout else result.stderr.strip()

            if 'Python 3.' not in version_line:
                self._log(f"Error: Invalid Python version: {version_line}")
                self._log("Action: Whisper requires Python 3.8 or higher")
                return False

            # Extract version number for more detailed check
            try:
                version_parts = version_line.replace('Python ', '').split('.')
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0

                if major < 3 or (major == 3 and minor < 8):
                    self._log(f"Error: Python {major}.{minor} is too old")
                    self._log("Action: Upgrade to Python 3.8 or higher")
                    return False

                self._log(f"Using Python {major}.{minor} at {python_path}")

            except (ValueError, IndexError):
                # Couldn't parse version, but "Python 3." was in output, so proceed
                self._log(f"Python version check: {version_line}")

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            self._log(f"Error: Could not verify Python version at {python_path}")
            self._log(f"Details: {str(e)}")
            self._log("Action: Ensure Python is properly installed")
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

            # Reset the stop flag
            self.stop_output_reading = False

            # Start output reading threads
            stdout_thread = threading.Thread(
                target=self._read_output_stream,
                args=(self.process.stdout, 'stdout'),
                daemon=True,
                name="WhisperStdoutReader"
            )
            stderr_thread = threading.Thread(
                target=self._read_output_stream,
                args=(self.process.stderr, 'stderr'),
                daemon=True,
                name="WhisperStderrReader"
            )

            self.output_threads = [stdout_thread, stderr_thread]
            stdout_thread.start()
            stderr_thread.start()

            self._log("Started output capture threads")

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

            # Signal output threads to stop
            self.stop_output_reading = True

            # Wait for output threads to finish (with timeout)
            for thread in self.output_threads:
                if thread.is_alive():
                    thread.join(timeout=2.0)

            self.output_threads = []
            self._log("Stopped output capture threads")

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
