"""
Styled button component with color management.
"""
from PyQt6.QtWidgets import QPushButton
from config.constants import BUTTON_COLORS


class StyledButton(QPushButton):
    """Custom styled button with automatic color assignment"""
    
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        # If no color is provided, get the next available color
        if color is None:
            if hasattr(parent, 'get_next_color'):
                self.color = parent.get_next_color()
            else:
                self.color = "#4CAF50"  # Default color
        else:
            self.color = color
        self.setFixedSize(120, 35)
        self.setStyleSheet(self.get_button_style())
        
    def get_button_style(self):
        """Generate CSS style for the button"""
        return f"""
        QPushButton {{
            background-color: {self.color};
            border: 2px solid {self.adjust_color(self.color, -40)};
            border-radius: 8px;
            color: white;
            font-weight: bold;
            font-size: 8px;
            padding: 5px;
            box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
        }}
        QPushButton:hover {{
            background-color: {self.adjust_color(self.color, 20)};
            border: 2px solid {self.adjust_color(self.color, -20)};
            box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.4);
        }}
        QPushButton:pressed {{
            background-color: {self.adjust_color(self.color, -20)};
            border: 2px solid {self.adjust_color(self.color, -60)};
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
        }}
        """
    
    def adjust_color(self, color, amount):
        """Adjust color brightness by amount"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"