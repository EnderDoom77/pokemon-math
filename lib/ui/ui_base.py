import os
import pygame
import abc
from pygame import Rect, Color, Surface
from typing import Callable, TypeAlias, Literal
from enum import Enum

class ElementStatus(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2

Size: TypeAlias = tuple[int,int]

class AxisAlignment(Enum):
    START = 0
    CENTERED = 1
    END = 2
    
class FullAlignment(Enum):
    TOPLEFT = 0
    TOPCENTER = 1
    TOPRIGHT = 2
    MIDDLELEFT = 4
    MIDDLECENTER = 5
    MIDDLERIGHT = 6
    BOTTOMLEFT = 8
    BOTTOMCENTER = 9
    BOTTOMRIGHT = 10

    @staticmethod
    def split_axes(align: "FullAlignment") -> tuple[AxisAlignment, AxisAlignment]:
        return (align % 4, align // 4)

class Pivot():
    def __init__(self, pivot_point: tuple[float,float]):
        self.pivot = pivot_point
    @staticmethod
    def from_alignment(alignment: FullAlignment):
        x_align, y_align = FullAlignment.split_axes(alignment)
        return Pivot((x_align / 2, y_align / 2))
    def align(self, container: Rect, size: Size) -> Rect:
        bx, by, cx, cy = container
        sx, sy = size
        px, py = self.pivot

        pad_x = (cx - sx) * px
        pad_y = (cy - sy) * py

        return (bx + pad_x, by + pad_y, sx, sy)

class Drawable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, surface: Surface):
        raise NotImplementedError

@Drawable.register
class TextElement:
    def __init__(self, rect: Rect, text: str, color: Color, font: pygame.font.Font, pivot: Pivot = Pivot((0.5,0.5))):
        self.rect = rect
        self._text = text
        self._color = color
        self._font = font
        self.pivot = pivot
        self.dirty = True

    def recompute_render(self):
        self.text_img = self.font.render(self.text, True, self.color)
        self.dirty = False

    @property
    def text(self):
        return self._text
        
    @text.setter
    def text(self, value: str):
        self._text = value
        self.dirty = True

    @property
    def color(self):
        return self._color
        
    @color.setter
    def color(self, value: Color):
        self._color = value
        self.dirty = True
        
    @property
    def font(self):
        return self._font
        
    @font.setter
    def font(self, value: pygame.font.Font):
        self._font = value
        self.dirty = True

    def render(self, surface: Surface):
        if self.dirty:
            self.recompute_render()
        size = self.text_img.get_size()
        rect = self.pivot.align(self.rect, size)
        surface.blit(self.text_img, rect)

@Drawable.register
class RectElement:
    def __init__(self, rect: Rect, color: Color | None = None, border_radius: int = -1, text: TextElement | None = None):
        self._rect = rect
        self.status = ElementStatus.NORMAL
        self.color = color
        self.border_radius = border_radius
        self.text = text

    @property
    def rect(self):
        return self._rect
    @rect.setter
    def rect(self, value: Rect):
        self._rect = value
        if self.text: self.text.rect = value

    def hovered(self, mouse_pos: tuple[float,float]):
        x,y,sx,sy = self.rect
        mx,my = mouse_pos

        return mx > x and my > y and mx <= x + sx and my <= y + sy

    def add_text(self, text: str, font: pygame.font.Font, color: Color = (0,0,0), pivot: Pivot = Pivot((0.5,0.5))):
        self.text = TextElement(self.rect, text, color, font, pivot)

    def render(self, surface: Surface):
        if self.color: pygame.draw.rect(surface, self.color, self.rect)
        if self.text: self.text.render(surface)

class ColorBlock:
    def __init__(self, color_base, color_hover: Color | None = None, color_pressed: Color | None = None):
        self.color_base = color_base
        self.color_hover = color_hover or color_base
        self.color_pressed = color_pressed or color_base

    def get_color(self, status: ElementStatus):
        if status == ElementStatus.NORMAL:
            return self.color_base
        elif status == ElementStatus.HOVER:
            return self.color_hover
        elif status == ElementStatus.PRESSED:
            return self.color_pressed

class InteractiveElement(RectElement):
    def __init__(self, rect: Rect, colors: ColorBlock | None = None, border_radius: int = -1, text: TextElement | None = None):
        super().__init__(rect, None, border_radius, text)
        self.colors = colors
        self.on_press: list[Callable] = []
        self.on_unpress: list[Callable] = []
        self.on_hover: list[Callable] = []
        self.on_unhover: list[Callable] = []
        self.on_click: list[Callable] = []

        self.last_hovered = False
        self.enabled = True
    
    def render(self, surface: Surface):
        if self.colors: pygame.draw.rect(surface, self.colors.get_color(self.status), self.rect, border_radius = self.border_radius)
        if self.text: self.text.render(surface)

    def onmousemoved(self, mouse_pos: tuple[float, float]):
        if not self.enabled: return

        intersects = self.hovered(mouse_pos)
        if not self.status == ElementStatus.PRESSED:
            self.status = ElementStatus.HOVER if intersects else ElementStatus.NORMAL
            
        if self.last_hovered and not intersects:
            for f in self.on_unhover: f()
        elif not self.last_hovered and intersects:
            for f in self.on_hover: f()
        self.last_hovered = intersects

    def onmousedown(self, mouse_pos: tuple[float, float]):
        if not self.enabled: return

        intersects = self.hovered(mouse_pos)
        if not intersects: return

        self.status = ElementStatus.PRESSED
        for f in self.on_press: f()

    def onmouseup(self, mouse_pos: tuple[float, float]):
        if not self.enabled: return

        intersects = self.hovered(mouse_pos)
        if not intersects:
            self.status = ElementStatus.NORMAL
        elif self.status == ElementStatus.PRESSED:
            for f in self.on_click: f()
            for f in self.on_unpress: f()
            self.status = ElementStatus.HOVER

class Sprite(RectElement):
    def __init__(self, rect: Rect, img_path: str, size: Size | None = None, pivot: Pivot = Pivot((0.5,0.5))):
        super().__init__(rect, None, -1, None)
        self._img_path = img_path
        self._size = size
        self.pivot = pivot
        self.dirty = True
        self.img = None

    def reload_img(self):
        if not os.path.exists(self.img_path):
            self.img = None
            return
        img = pygame.image.load(self.img_path).convert()
        self.img = pygame.transform.scale(img, self.size)
        self.dirty = False

    @property
    def img_path(self):
        return self._img_path
    @img_path.setter
    def img_path(self, value: str):
        self._img_path = value
        self.dirty = True

    @property
    def rect(self):
        return self._rect
    @rect.setter
    def rect(self, value: Rect):
        self._rect = value
        self.dirty = True
        if self.text: self.text.rect = value
        
    @property
    def size(self):
        if self._size: return self._size
        x,y,sx,sy = self.rect
        return (sx,sy)
    @size.setter
    def size(self, value: Size):
        self._size = value
        self.dirty = True

    def render(self, surface: Surface):
        if self.dirty:
            self.reload_img()
        if self.img: surface.blit(self.img, self.pivot.align(self.rect, self.size))