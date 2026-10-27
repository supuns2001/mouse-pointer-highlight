from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QRadioButton, QButtonGroup, QPushButton, QColorDialog,
    QFrame, QWidget
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from config import ConfigManager

class ShapePreviewWidget(QWidget):
    """Mini preview box inside Settings showing live highlight appearance."""
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config
        self.setFixedSize(140, 140)
        self.setStyleSheet("background: #1e1e24; border: 1px solid #33333e; border-radius: 8px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        shape = self.config.get("shape", "circle")
        fill_color = self.config.get_qcolor()
        border_color = self.config.get_border_qcolor()
        radius = min(50, self.config.get("radius", 35))
        border_width = self.config.get("border_width", 5)

        center = QPoint(self.width() // 2, self.height() // 2)

        if shape == "circle":
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 1.5))
            painter.drawEllipse(center, radius, radius)
        elif shape == "band":
            pen = QPen(fill_color, border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            draw_radius = max(2, radius - (border_width // 2))
            painter.drawEllipse(center, draw_radius, draw_radius)
        elif shape == "dot_ring":
            pen = QPen(fill_color, max(2, border_width // 2))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius, radius)

            painter.setBrush(QBrush(border_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, 4, 4)

        painter.end()


class SettingsDialog(QDialog):
    """
    Modern Settings Window allowing real-time adjustment of pointer colors,
    shapes, sizes, opacity, and band thickness.
    """
    def __init__(self, config: ConfigManager, on_change_callback):
        super().__init__()
        self.config = config
        self.on_change = on_change_callback

        self.setWindowTitle("Mouse Pointer Highlighter — Settings")
        self.setFixedSize(480, 560)
        self.setStyleSheet("""
            QDialog {
                background-color: #121216;
                color: #FFFFFF;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }
            QLabel {
                color: #D1D5DB;
                font-size: 13px;
                font-weight: 500;
            }
            QRadioButton {
                color: #FFFFFF;
                font-size: 13px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #4B5563;
                background-color: #1F2937;
            }
            QRadioButton::indicator:checked {
                background-color: #3B82F6;
                border-color: #60A5FA;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #2D3748;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3B82F6;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 2px solid #3B82F6;
                width: 16px;
                margin-top: -6px;
                margin-bottom: -6px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header with Live Preview
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title_label = QLabel("Highlight Customization")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        subtitle_label = QLabel("Adjust shape, colors, and sizes in real-time.")
        subtitle_label.setStyleSheet("font-size: 12px; color: #9CA3AF;")
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_text.addStretch()

        self.preview_widget = ShapePreviewWidget(self.config)
        header_layout.addLayout(header_text)
        header_layout.addWidget(self.preview_widget)
        main_layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #2D3748;")
        main_layout.addWidget(line)

        # Shape selection
        shape_label = QLabel("Highlighter Shape:")
        main_layout.addWidget(shape_label)

        shape_layout = QHBoxLayout()
        self.shape_group = QButtonGroup(self)

        self.rb_circle = QRadioButton("Circle (Filled)")
        self.rb_band = QRadioButton("Band / Ring")
        self.rb_dot_ring = QRadioButton("Dot & Ring")

        current_shape = self.config.get("shape", "circle")
        if current_shape == "band":
            self.rb_band.setChecked(True)
        elif current_shape == "dot_ring":
            self.rb_dot_ring.setChecked(True)
        else:
            self.rb_circle.setChecked(True)

        self.shape_group.addButton(self.rb_circle, 1)
        self.shape_group.addButton(self.rb_band, 2)
        self.shape_group.addButton(self.rb_dot_ring, 3)

        shape_layout.addWidget(self.rb_circle)
        shape_layout.addWidget(self.rb_band)
        shape_layout.addWidget(self.rb_dot_ring)
        main_layout.addLayout(shape_layout)

        self.rb_circle.toggled.connect(self.on_shape_changed)
        self.rb_band.toggled.connect(self.on_shape_changed)
        self.rb_dot_ring.toggled.connect(self.on_shape_changed)

        # Color palette & custom button
        color_layout = QHBoxLayout()
        color_label = QLabel("Color Preset:")
        color_layout.addWidget(color_label)

        presets = ["#FFD700", "#00FF66", "#00D4FF", "#FF3366", "#FF9900", "#A855F7"]
        for hex_code in presets:
            btn = QPushButton()
            btn.setFixedSize(26, 26)
            btn.setStyleSheet(f"background-color: {hex_code}; border-radius: 13px; border: 2px solid #374151;")
            btn.clicked.connect(lambda _, c=hex_code: self.set_color(c))
            color_layout.addWidget(btn)

        self.custom_color_btn = QPushButton("Pick Color...")
        self.custom_color_btn.setStyleSheet("""
            QPushButton {
                background: #374151;
                color: #F3F4F6;
                padding: 4px 10px;
                font-size: 11px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #4B5563; }
        """)
        self.custom_color_btn.clicked.connect(self.open_color_picker)
        color_layout.addWidget(self.custom_color_btn)
        main_layout.addLayout(color_layout)

        # Radius / Size Slider
        radius_layout = QHBoxLayout()
        self.radius_label = QLabel(f"Size (Radius): {self.config.get('radius')} px")
        radius_layout.addWidget(self.radius_label)
        main_layout.addLayout(radius_layout)

        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(15, 100)
        self.radius_slider.setValue(self.config.get("radius", 35))
        self.radius_slider.valueChanged.connect(self.on_radius_changed)
        main_layout.addWidget(self.radius_slider)

        # Band Thickness Slider
        band_layout = QHBoxLayout()
        self.band_label = QLabel(f"Band Thickness: {self.config.get('border_width')} px")
        band_layout.addWidget(self.band_label)
        main_layout.addLayout(band_layout)

        self.band_slider = QSlider(Qt.Orientation.Horizontal)
        self.band_slider.setRange(2, 25)
        self.band_slider.setValue(self.config.get("border_width", 5))
        self.band_slider.valueChanged.connect(self.on_band_changed)
        main_layout.addWidget(self.band_slider)

        # Opacity Slider
        opacity_layout = QHBoxLayout()
        op_percent = int((self.config.get("opacity", 140) / 255.0) * 100)
        self.opacity_label = QLabel(f"Transparency / Opacity: {op_percent}%")
        opacity_layout.addWidget(self.opacity_label)
        main_layout.addLayout(opacity_layout)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(25, 255)
        self.opacity_slider.setValue(self.config.get("opacity", 140))
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        main_layout.addWidget(self.opacity_slider)

        # Close / Done Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Done")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

    def on_shape_changed(self):
        if self.rb_circle.isChecked():
            self.config.set("shape", "circle")
        elif self.rb_band.isChecked():
            self.config.set("shape", "band")
        elif self.rb_dot_ring.isChecked():
            self.config.set("shape", "dot_ring")
        self.sync_changes()

    def set_color(self, hex_code):
        self.config.set("color", hex_code)
        self.config.set("border_color", hex_code)
        self.sync_changes()

    def open_color_picker(self):
        current_col = QColor(self.config.get("color"))
        picked = QColorDialog.getColor(current_col, self, "Select Highlighter Color")
        if picked.isValid():
            self.set_color(picked.name())

    def on_radius_changed(self, val):
        self.config.set("radius", val)
        self.radius_label.setText(f"Size (Radius): {val} px")
        self.sync_changes()

    def on_band_changed(self, val):
        self.config.set("border_width", val)
        self.band_label.setText(f"Band Thickness: {val} px")
        self.sync_changes()

    def on_opacity_changed(self, val):
        self.config.set("opacity", val)
        op_percent = int((val / 255.0) * 100)
        self.opacity_label.setText(f"Transparency / Opacity: {op_percent}%")
        self.sync_changes()

    def sync_changes(self):
        self.preview_widget.update()
        if self.on_change:
            self.on_change()
