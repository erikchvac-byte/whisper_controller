"""
Whisper Auto Control - Modern dark mode GUI application.
Main application entry point with CustomTkinter interface.
"""

import customtkinter as ctk
import threading
import time
from datetime import datetime
from typing import Optional
from tkinter import messagebox, filedialog
from config import config, Config
from whisper_controller import controller, WhisperController


class WhisperAutoGUI(ctk.CTk):
    """Main GUI application for Whisper Auto Control."""

    def __init__(self):
        """Initialize the GUI application."""
        super().__init__()

        # Application state
        self.is_running = False
        self.status_update_thread: Optional[threading.Thread] = None
        self.stop_status_thread = False

        # Configure window
        self.title(config.APP_NAME)
        self.geometry("600x500")
        self.minsize(500, 400)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure colors
        self.colors = config.COLORS

        # Restore window geometry if saved
        self._restore_window_geometry()

        # Setup UI
        self._setup_ui()

        # Setup controller callbacks
        controller.set_log_callback(self._log_message)
        controller.set_status_callback(self._update_status_display)

        # Start status update thread
        self._start_status_thread()

        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initial status update
        self._update_status_display()
        self._log_message(f"{config.APP_NAME} v{config.APP_VERSION} initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)  # Log area expands

        # Header
        self._create_header()

        # Control buttons
        self._create_control_buttons()

        # Status display
        self._create_status_display()

        # Model selection and download
        self._create_model_section()

        # Configuration display
        self._create_config_section()

        # Activity log
        self._create_log_section()

        # Footer
        self._create_footer()

    def _create_header(self):
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        title_label = ctk.CTkLabel(
            header_frame,
            text=config.APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.pack(pady=15)

    def _create_control_buttons(self):
        """Create start/stop control buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Start button
        self.start_button = ctk.CTkButton(
            button_frame,
            text="START",
            command=self._on_start,
            fg_color=self.colors['success'],
            hover_color="#00cc70",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.start_button.grid(row=0, column=0, padx=5, sticky="ew")

        # Stop button
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="STOP",
            command=self._on_stop,
            fg_color=self.colors['error'],
            hover_color="#cc3333",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5, sticky="ew")

    def _create_status_display(self):
        """Create status display section."""
        status_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        status_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)

        # Status labels
        labels = [
            ("Status:", 0),
            ("PID:", 1),
            ("Model:", 2)
        ]

        for label_text, row in labels:
            label = ctk.CTkLabel(
                status_frame,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        # Status values
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Stopped",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['error'],
            anchor="w"
        )
        self.status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.pid_label = ctk.CTkLabel(
            status_frame,
            text="N/A",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        self.pid_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.model_status_label = ctk.CTkLabel(
            status_frame,
            text=config.get_selected_model(),
            font=ctk.CTkFont(size=12),
            text_color=self.colors['primary'],
            anchor="w"
        )
        self.model_status_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def _create_model_section(self):
        """Create model selection and download section."""
        model_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        model_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        model_frame.grid_columnconfigure(1, weight=1)

        # Model selector label
        model_label = ctk.CTkLabel(
            model_frame,
            text="Whisper Model:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        model_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Model dropdown
        self.model_selector = ctk.CTkOptionMenu(
            model_frame,
            values=config.WHISPER_MODELS,
            command=self._on_model_change,
            fg_color=self.colors['background'],
            button_color=self.colors['primary'],
            button_hover_color="#0099cc"
        )
        self.model_selector.set(config.get_selected_model())
        self.model_selector.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Download button
        self.download_button = ctk.CTkButton(
            model_frame,
            text="Download Model",
            command=self._on_download_model,
            fg_color=self.colors['primary'],
            hover_color="#0099cc",
            width=150
        )
        self.download_button.grid(row=0, column=2, padx=10, pady=10)

    def _create_config_section(self):
        """Create configuration display section."""
        config_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        config_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        # Python path
        python_label = ctk.CTkLabel(
            config_frame,
            text="Python:",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        python_label.grid(row=0, column=0, padx=10, pady=3, sticky="w")

        self.python_path_label = ctk.CTkLabel(
            config_frame,
            text=config.get_python_path(),
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        self.python_path_label.grid(row=0, column=1, padx=10, pady=3, sticky="w")

        # Script path
        script_label = ctk.CTkLabel(
            config_frame,
            text="Script:",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        script_label.grid(row=1, column=0, padx=10, pady=3, sticky="w")

        self.script_path_label = ctk.CTkLabel(
            config_frame,
            text=config.get_script_path() or "Not configured",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        self.script_path_label.grid(row=1, column=1, padx=10, pady=3, sticky="w")

        # Configure button
        config_button = ctk.CTkButton(
            config_frame,
            text="Configure Paths",
            command=self._on_configure_paths,
            fg_color=self.colors['background'],
            hover_color=self.colors['secondary'],
            width=120,
            height=25
        )
        config_button.grid(row=0, column=2, rowspan=2, padx=10, pady=3)

    def _create_log_section(self):
        """Create activity log section."""
        log_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        log_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        # Log header
        log_header = ctk.CTkLabel(
            log_frame,
            text="Activity Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        log_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Log textbox
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            fg_color=self.colors['background'],
            font=ctk.CTkFont(size=10, family="Consolas"),
            wrap="word",
            state="disabled"
        )
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _create_footer(self):
        """Create footer section."""
        footer_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary'], corner_radius=10)
        footer_frame.grid(row=6, column=0, padx=10, pady=(5, 10), sticky="ew")

        footer_text = f"{config.APP_NAME} v{config.APP_VERSION} | {config.APP_AUTHOR}"
        footer_label = ctk.CTkLabel(
            footer_frame,
            text=footer_text,
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        footer_label.pack(pady=8)

    # Event handlers
    def _on_start(self):
        """Handle start button click."""
        def start_async():
            model = self.model_selector.get()
            success = controller.start(model)

            if success:
                self.after(0, self._set_running_state, True)
            else:
                self.after(0, self._log_message, "Failed to start Whisper")

        threading.Thread(target=start_async, daemon=True).start()

    def _on_stop(self):
        """Handle stop button click."""
        def stop_async():
            success = controller.stop()

            if success:
                self.after(0, self._set_running_state, False)
            else:
                self.after(0, self._log_message, "Failed to stop Whisper")

        threading.Thread(target=stop_async, daemon=True).start()

    def _on_model_change(self, model: str):
        """Handle model selection change."""
        config.set_selected_model(model)
        config.save()
        self._log_message(f"Model changed to: {model}")

    def _on_download_model(self):
        """Handle download model button click."""
        model = self.model_selector.get()

        # Disable button during download
        self.download_button.configure(state="disabled", text="Downloading...")

        def download_async():
            def progress_callback(message: str):
                self.after(0, self._log_message, message)

            success = controller.download_model(model, progress_callback)

            # Re-enable button
            self.after(0, lambda: self.download_button.configure(
                state="normal",
                text="Download Model"
            ))

            if success:
                self.after(0, self._log_message, f"Model '{model}' ready for use")

        threading.Thread(target=download_async, daemon=True).start()

    def _on_configure_paths(self):
        """Handle configure paths button click."""
        dialog = ConfigDialog(self)
        self.wait_window(dialog)

        # Update displayed paths
        self.python_path_label.configure(text=config.get_python_path())
        self.script_path_label.configure(text=config.get_script_path() or "Not configured")

    def _set_running_state(self, running: bool):
        """Set UI state based on running status."""
        self.is_running = running

        if running:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def _update_status_display(self, status_text: Optional[str] = None):
        """Update status display with current information."""
        status = controller.get_status()

        # Update status text
        if status['running']:
            self.status_label.configure(
                text="Running",
                text_color=self.colors['success']
            )
        else:
            self.status_label.configure(
                text="Stopped",
                text_color=self.colors['error']
            )

        # Update PID
        if status['pid']:
            self.pid_label.configure(
                text=str(status['pid']),
                text_color=self.colors['text']
            )
        else:
            self.pid_label.configure(
                text="N/A",
                text_color=self.colors['text_secondary']
            )

        # Update model
        self.model_status_label.configure(text=status['model'])

        # Update button states
        self._set_running_state(status['running'])

    def _log_message(self, message: str):
        """Add message to activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _start_status_thread(self):
        """Start background thread for status updates."""
        def status_loop():
            while not self.stop_status_thread:
                try:
                    self.after(0, self._update_status_display)
                    time.sleep(0.5)  # 500ms refresh rate
                except Exception as e:
                    print(f"Status thread error: {e}")
                    break

        self.status_update_thread = threading.Thread(target=status_loop, daemon=True)
        self.status_update_thread.start()

    def _restore_window_geometry(self):
        """Restore saved window geometry."""
        geometry = config.get_window_geometry()
        if geometry:
            try:
                self.geometry(geometry)
            except:
                pass

        position = config.get_window_position()
        if position:
            try:
                self.geometry(position)
            except:
                pass

    def _save_window_geometry(self):
        """Save current window geometry."""
        geometry = self.geometry()
        config.set_window_geometry(geometry)
        config.save()

    def _on_closing(self):
        """Handle window close event."""
        # Check if process is running
        if controller.is_running():
            response = messagebox.askyesno(
                "Confirm Exit",
                "Whisper is currently running. Stop and exit?",
                icon='warning'
            )

            if not response:
                return

            # Stop the process
            controller.stop()

        # Save window geometry
        self._save_window_geometry()

        # Stop status thread
        self.stop_status_thread = True

        # Destroy window
        self.destroy()


class ConfigDialog(ctk.CTkToplevel):
    """Configuration dialog for setting paths."""

    def __init__(self, parent):
        """Initialize configuration dialog."""
        super().__init__(parent)

        self.title("Configure Paths")
        self.geometry("500x200")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Setup dialog UI."""
        # Python path
        python_label = ctk.CTkLabel(
            self,
            text="Python Interpreter:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        python_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        python_frame = ctk.CTkFrame(self, fg_color="transparent")
        python_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        python_frame.grid_columnconfigure(0, weight=1)

        self.python_entry = ctk.CTkEntry(python_frame)
        self.python_entry.insert(0, config.get_python_path())
        self.python_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        python_browse = ctk.CTkButton(
            python_frame,
            text="Browse",
            command=self._browse_python,
            width=80
        )
        python_browse.grid(row=0, column=1)

        # Script path
        script_label = ctk.CTkLabel(
            self,
            text="Whisper Script:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        script_label.grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")

        script_frame = ctk.CTkFrame(self, fg_color="transparent")
        script_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        script_frame.grid_columnconfigure(0, weight=1)

        self.script_entry = ctk.CTkEntry(script_frame)
        self.script_entry.insert(0, config.get_script_path())
        self.script_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        script_browse = ctk.CTkButton(
            script_frame,
            text="Browse",
            command=self._browse_script,
            width=80
        )
        script_browse.grid(row=0, column=1)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=20, pady=20, sticky="e")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray",
            width=100
        )
        cancel_button.grid(row=0, column=0, padx=5)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save,
            width=100
        )
        save_button.grid(row=0, column=1, padx=5)

        self.grid_columnconfigure(0, weight=1)

    def _browse_python(self):
        """Browse for Python interpreter."""
        filename = filedialog.askopenfilename(
            title="Select Python Interpreter",
            filetypes=[("Python", "python.exe"), ("All files", "*.*")]
        )
        if filename:
            self.python_entry.delete(0, "end")
            self.python_entry.insert(0, filename)

    def _browse_script(self):
        """Browse for Whisper script."""
        filename = filedialog.askopenfilename(
            title="Select Whisper Script",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.script_entry.delete(0, "end")
            self.script_entry.insert(0, filename)

    def _save(self):
        """Save configuration."""
        config.set_python_path(self.python_entry.get())
        config.set_script_path(self.script_entry.get())
        config.save()
        self.destroy()


def main():
    """Main application entry point."""
    app = WhisperAutoGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
