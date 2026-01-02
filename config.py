"""
Configuration management for Whisper Auto Control application.
Handles settings, paths, and persistent configuration storage.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the application."""

    # Application constants
    APP_NAME = "Whisper Auto Control"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Whisper Auto Team"

    # Color scheme
    COLORS = {
        'primary': '#00d4ff',
        'background': '#1a1a2e',
        'secondary': '#16213e',
        'success': '#00ff88',
        'error': '#ff4444',
        'warning': '#ffaa00',
        'text': '#ffffff',
        'text_secondary': '#a0a0a0'
    }

    # Available Whisper models
    WHISPER_MODELS = [
        'tiny',
        'base',
        'small',
        'medium',
        'large',
        'turbo'
    ]

    # Default settings
    DEFAULT_SETTINGS = {
        'selected_model': 'base',
        'auto_start': False,
        'minimize_to_tray': False,
        'log_level': 'INFO',
        'python_path': r'C:\whisper\venv\Scripts\python.exe',
        'script_path': r'C:\whisper\ptt_whisper.py',
        'window_geometry': '600x500',
        'window_position': None
    }

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.whisper_auto'
        self.config_file = self.config_dir / 'config.json'
        self.settings: Dict[str, Any] = {}
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded_settings}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.settings = self.DEFAULT_SETTINGS.copy()
        else:
            self.settings = self.DEFAULT_SETTINGS.copy()

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.settings[key] = value

    def get_python_path(self) -> str:
        """Get Python interpreter path."""
        return self.get('python_path', sys.executable)

    def set_python_path(self, path: str) -> None:
        """Set Python interpreter path."""
        self.set('python_path', path)

    def get_script_path(self) -> str:
        """Get Whisper script path."""
        return self.get('script_path', '')

    def set_script_path(self, path: str) -> None:
        """Set Whisper script path."""
        self.set('script_path', path)

    def get_selected_model(self) -> str:
        """Get selected Whisper model."""
        model = self.get('selected_model', 'base')
        return model if model in self.WHISPER_MODELS else 'base'

    def set_selected_model(self, model: str) -> None:
        """Set selected Whisper model."""
        if model in self.WHISPER_MODELS:
            self.set('selected_model', model)

    def get_window_geometry(self) -> Optional[str]:
        """Get saved window geometry."""
        return self.get('window_geometry')

    def set_window_geometry(self, geometry: str) -> None:
        """Set window geometry."""
        self.set('window_geometry', geometry)

    def get_window_position(self) -> Optional[str]:
        """Get saved window position."""
        return self.get('window_position')

    def set_window_position(self, position: str) -> None:
        """Set window position."""
        self.set('window_position', position)


# Global config instance
config = Config()
