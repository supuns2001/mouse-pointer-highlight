import sys
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QAction
from PyQt6.QtCore import Qt

from config import ConfigManager
from overlay import MouseHighlighterOverlay
from settings_dialog import SettingsDialog

def create_tray_icon() -> QIcon:
    """Generates a clean programmatic icon for the Windows system tray."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    # Outer glow ring
    painter.setBrush(QBrush(QColor(255, 215, 0, 160)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)

    # Inner core dot
    painter.setBrush(QBrush(QColor(255, 140, 0, 240)))
    painter.drawEllipse(10, 10, 12, 12)
    painter.end()
    return QIcon(pixmap)


class MouseHighlighterApp:
    def __init__(self):
        self.config = ConfigManager()
        self.overlay = MouseHighlighterOverlay(self.config)
        self.settings_dialog = None

        self.setup_tray()

    def on_config_updated(self):
        """Called whenever settings change in real-time."""
        self.overlay.update_dimensions()
        self.overlay.update()

    def open_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.config, self.on_config_updated)
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()

    def toggle_highlighter(self):
        self.overlay.toggle()
        is_on = self.overlay.isVisible()
        self.toggle_action.setChecked(is_on)
        self.tray_icon.setToolTip(f"Mouse Pointer Highlighter: {'ON' if is_on else 'OFF'}")

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(create_tray_icon())
        self.tray_icon.setToolTip("Mouse Pointer Highlighter (Running)")

        tray_menu = QMenu()

        self.toggle_action = QAction("Highlight Active", checkable=True)
        self.toggle_action.setChecked(self.config.get("enabled", True))
        self.toggle_action.triggered.connect(self.toggle_highlighter)
        tray_menu.addAction(self.toggle_action)

        settings_action = QAction("Settings (Customize)...")
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        quit_action = QAction("Exit")
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        # Double click tray icon opens Settings
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_settings()


def main():
    app = QApplication(sys.argv)
    # Ensure app stays alive even if settings dialog is closed
    app.setQuitOnLastWindowClosed(False)

    highlighter = MouseHighlighterApp()
    
    # Open settings on first launch so user can see & customize right away
    highlighter.open_settings()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
