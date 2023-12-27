from pygame import Rect, Color
from lib.ui.ui_base import *
from typing import Callable

class Button(InteractiveElement):
    def __init__(self, rect: Rect, colors: ColorBlock | None = None, border_radius: int = -1, text: TextElement | None = None):
        super().__init__(rect, colors, border_radius, text)

