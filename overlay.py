from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QBrush, QPen, QCursor
from config import ConfigManager

class MouseHighlighterOverlay(QWidget):
    """
    Transparent, click-through overlay window that tracks and highlights
    the mouse cursor smoothly in real-time.
    """
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config

        # Set necessary window flags for seamless click-through overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Setup tracking timer (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        
        self.update_dimensions()
        self.start()

    def update_dimensions(self):
        """Resizes the overlay canvas based on radius + padding."""
        radius = self.config.get("radius", 35)
        border_width = self.config.get("border_width", 5)
        # Extra padding to prevent clipping anti-aliased edges
        padding = border_width + 10
        size = (radius * 2) + padding
        self.resize(size, size)
        self.update()

    def start(self):
        fps = self.config.get("fps", 60)
        interval = max(10, 1000 // fps)
        self.timer.start(interval)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def toggle(self):
        if self.isVisible():
            self.stop()
            self.config.set("enabled", False)
        else:
            self.start()
            self.config.set("enabled", True)

    def update_position(self):
        """Smoothly follow the current system cursor coordinates."""
        if not self.config.get("enabled", True):
            if self.isVisible():
                self.hide()
            return

        cursor_pos = QCursor.pos()
        # Center the window around cursor tip
        target_x = cursor_pos.x() - (self.width() // 2)
        target_y = cursor_pos.y() - (self.height() // 2)

        # Only move if position actually changed to save draw cycles
        if self.x() != target_x or self.y() != target_y:
            self.move(target_x, target_y)

    def paintEvent(self, event):
        """Renders the selected highlight shape (Circle, Band, Dot & Ring)."""
        if not self.config.get("enabled", True):
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        shape = self.config.get("shape", "circle")
        fill_color = self.config.get_qcolor()
        border_color = self.config.get_border_qcolor()
        radius = self.config.get("radius", 35)
        border_width = self.config.get("border_width", 5)

        center = QPoint(self.width() // 2, self.height() // 2)

        if shape == "circle":
            # Semi-transparent solid circle with soft border
            painter.setBrush(QBrush(fill_color))
            pen = QPen(border_color, 1.5)
            painter.setPen(pen)
            painter.drawEllipse(center, radius, radius)

        elif shape == "band":
            # Hollow ring / band
            pen = QPen(fill_color, border_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            draw_radius = max(2, radius - (border_width // 2))
            painter.drawEllipse(center, draw_radius, draw_radius)

        elif shape == "dot_ring":
            # Outer ring + pinpoint center dot
            pen = QPen(fill_color, max(2, border_width // 2))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius, radius)

            # Center dot
            painter.setBrush(QBrush(border_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, 4, 4)

        painter.end()
