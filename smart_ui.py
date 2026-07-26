import sys
import threading
import time
import json
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QGraphicsDropShadowEffect, QSizePolicy
import keyboard

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR   = _base_dir()
CONFIG_DIR = BASE_DIR / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"

def _read_full_config() -> dict:
    try:
        return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

class SmartIslandWindow(QWidget):
    subtitle_signal = pyqtSignal(str)
    state_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._muted = False
        self._ready = True
        self._assistant_name = _read_full_config().get("assistant_name", "ANSH") or "ANSH"
        
        self.on_text_command = None
        self.on_remote_clicked = None
        self.on_interrupt = None
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.base_width = 150
        self.base_height = 55
        self.expanded_width = 400
        self.expanded_height = 100
        self.is_expanded = False

        self.init_ui()
        self.setup_hotkey()

        self.subtitle_signal.connect(self.show_subtitle)
        self.state_signal.connect(self.update_state)
        
        # Idle timer (1 minute)
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.hide)
        self.idle_timer.start(60000)

        # Liquid motion timer
        self.liquid_timer = QTimer(self)
        self.liquid_timer.timeout.connect(self.animate_liquid)
        self.liquid_step = 0

        self.enforce_autostart()

    def enforce_autostart(self):
        try:
            import platform
            _OS = platform.system()
            script = str(Path(__file__).resolve().parent / "main.py")
            if _OS == "Windows":
                import winreg
                reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
                pythonw = Path(sys.executable).parent / "pythonw.exe"
                exe = str(pythonw if pythonw.exists() else sys.executable)
                winreg.SetValueEx(reg, "ANSH_AI", 0, winreg.REG_SZ, f'"{exe}" "{script}"')
                winreg.CloseKey(reg)
            print("[SYS] Auto-start enforced.")
        except Exception as e:
            print(f"[ERR] Auto-start failed: {e}")

    def init_ui(self):
        self.setFixedSize(self.base_width, self.base_height)
        screen = QApplication.primaryScreen().geometry()
        self.x_pos = (screen.width() - self.base_width) // 2
        self.y_pos = 10
        self.move(self.x_pos, self.y_pos)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)

        self.container = QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border-radius: 20px;
                border: 2px solid #333333;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(15, 10, 15, 10)
        self.container_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)

        self.subtitle_label = QLabel(self._assistant_name)
        self.subtitle_label.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px; border: none;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(False)
        self.subtitle_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.container_layout.addWidget(self.subtitle_label)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1c1c1e;
                color: white;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 5px 10px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
        """)
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.hide()
        self.input_field.returnPressed.connect(self.on_submit)
        self.container_layout.addWidget(self.input_field)

        self.layout.addWidget(self.container)

    def setup_hotkey(self):
        try:
            keyboard.add_hotkey('ctrl+shift+a', self.toggle_expand_safe)
        except Exception as e:
            print(f"Failed to bind hotkey: {e}")

    def reset_idle_timer(self):
        self.show()
        self.idle_timer.start(60000)

    def toggle_expand_safe(self):
        QTimer.singleShot(0, self.reset_idle_timer)
        QTimer.singleShot(0, self.toggle_expand)

    def toggle_expand(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.is_expanded = True
        self.input_field.show()
        self.input_field.setFocus()
        
        screen = QApplication.primaryScreen().geometry()
        new_x = (screen.width() - self.expanded_width) // 2
        
        self.setFixedSize(self.expanded_width, self.expanded_height)
        self.move(new_x, self.y_pos)

    def collapse(self):
        self.is_expanded = False
        self.input_field.hide()
        self.input_field.clear()
        
        screen = QApplication.primaryScreen().geometry()
        new_x = (screen.width() - self.base_width) // 2
        
        self.setFixedSize(self.base_width, self.base_height)
        self.move(new_x, self.y_pos)
        self.subtitle_label.setText(self._assistant_name)

    def show_subtitle(self, text):
        self.reset_idle_timer()
        self.subtitle_label.setText(text)

    def animate_liquid(self):
        colors = ["#00d4ff", "#0088ff", "#00ffff"]
        radius = [20, 23, 26, 23]
        c = colors[self.liquid_step % len(colors)]
        r = radius[self.liquid_step % len(radius)]
        self.container.setStyleSheet(f"""
            QWidget {{
                background-color: #000000;
                border-radius: {r}px;
                border: 2px solid {c};
            }}
        """)
        self.liquid_step += 1

    def update_state(self, state):
        self.reset_idle_timer()
        if state == "SPEAKING":
            self.liquid_timer.start(100)
        else:
            self.liquid_timer.stop()
            if state == "THINKING":
                self.container.setStyleSheet("""
                    QWidget {
                        background-color: #000000;
                        border-radius: 20px;
                        border: 2px solid #ffcc00;
                    }
                """)
            else:
                self.container.setStyleSheet("""
                    QWidget {
                        background-color: #000000;
                        border-radius: 20px;
                        border: 2px solid #333333;
                    }
                """)

    def on_submit(self):
        self.reset_idle_timer()
        text = self.input_field.text().strip()
        if text:
            if self.on_text_command:
                threading.Thread(target=self.on_text_command, args=(text,), daemon=True).start()
            self.collapse()

    def _toggle_mute(self):
        self._muted = not self._muted
        if self._muted:
            self.subtitle_signal.emit("MUTED")
        else:
            self.subtitle_signal.emit("LISTENING")
        self.reset_idle_timer()
        
    def notify_phone_connected(self): pass
    def start_camera_stream(self): pass
    def stop_camera_stream(self): pass


class _RootShim:
    def __init__(self, app: QApplication):
        self._app = app
    def mainloop(self):
        self._app.exec()
    def protocol(self, *_):
        pass

class AnshUI:
    def __init__(self, face_path: str, size=None):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setStyle("Fusion")
        self._win = SmartIslandWindow()
        self._win.show()
        self.root = _RootShim(self._app)
        
        self._log_sig = pyqtSignal(str)
        self._content_sig = pyqtSignal(str, str)
        self._reconfig_sig = pyqtSignal()
        self._camera_sig = pyqtSignal(bytes)

    @property
    def muted(self) -> bool: return self._win._muted

    @muted.setter
    def muted(self, v: bool):
        if v != self._win._muted: self._win._toggle_mute()

    @property
    def current_file(self) -> str | None: return None

    @property
    def on_text_command(self): return self._win.on_text_command

    @on_text_command.setter
    def on_text_command(self, cb): self._win.on_text_command = cb

    @property
    def on_remote_clicked(self): return self._win.on_remote_clicked

    @on_remote_clicked.setter
    def on_remote_clicked(self, cb): self._win.on_remote_clicked = cb

    @property
    def on_interrupt(self): return self._win.on_interrupt

    @on_interrupt.setter
    def on_interrupt(self, cb): self._win.on_interrupt = cb

    def notify_phone_connected(self) -> None: pass

    def set_state(self, state: str):
        self._win.state_signal.emit(state)

    def write_log(self, text: str):
        if text.startswith("ANSH:") or text.startswith("Ansh:"):
            msg = text.split(":", 1)[1].strip()
            self._win.subtitle_signal.emit(msg)

    def wait_for_api_key(self):
        config = _read_full_config()
        if not config.get("api_key"):
            from PyQt6.QtWidgets import QInputDialog, QMessageBox
            text, ok = QInputDialog.getText(None, "Welcome to ANSH", "First time setup: Enter your Gemini API Key:", QLineEdit.EchoMode.Password)
            if ok and text:
                config["api_key"] = text.strip()
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                API_FILE.write_text(json.dumps(config, indent=4), encoding="utf-8")
            else:
                QMessageBox.critical(None, "Error", "API Key is required to run ANSH.")
                sys.exit(0)

    def show_content(self, title: str, text: str): pass
    def prompt_reconfig(self): pass
    def show_camera_frame(self, img_bytes: bytes): pass
    def start_camera_stream(self) -> None: pass
    def stop_camera_stream(self) -> None: pass

    @property
    def assistant_name(self) -> str: return self._win._assistant_name

    def start_speaking(self): self.set_state("SPEAKING")
    def stop_speaking(self):
        if not self.muted: self.set_state("LISTENING")
