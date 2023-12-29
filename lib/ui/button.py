from pygame import Rect, Color
from lib.ui.ui_base import *
from typing import Callable

from lib.ui.ui_base import Anchor, ColorBlock, Element, TextElement

class Button(InteractiveElement):
    def __init__(self, name: str, rect: Rect, anchor: Anchor = Anchor(), colors: ColorBlock | None = None, border_radius: int = -1, text: TextElement | None = None, parent: Element | None = None):
        super().__init__(name, rect, anchor, colors, border_radius, text, parent)

