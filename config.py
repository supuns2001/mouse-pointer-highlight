import json
import os
from PyQt6.QtGui import QColor

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "enabled": True,
    "shape": "circle",        # "circle" | "band" | "dot_ring"
    "color": "#FFD700",       # Gold / Yellow
    "opacity": 140,           # 0 to 255
    "radius": 35,             # Radius in pixels
    "border_width": 5,        # Thickness for band/ring shape
    "border_color": "#FF8C00",# Optional border color
    "fps": 60                 # Polling rate (~16ms)
}

class ConfigManager:
    """Handles loading and saving highlighter configuration to config.json."""
    
    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Warning] Failed to load config.json: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[Error] Failed to save config.json: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_qcolor(self) -> QColor:
        color = QColor(self.data["color"])
        color.setAlpha(int(self.data["opacity"]))
        return color

    def get_border_qcolor(self) -> QColor:
        color = QColor(self.data.get("border_color", self.data["color"]))
        color.setAlpha(min(255, int(self.data["opacity"]) + 40))
        return color
