import os
import pygame
from abc import abstractmethod, ABCMeta
from pygame import Rect, Color, Surface
from typing import Callable, TypeAlias, Literal
from enum import Enum

from lib.mathlib import TupleMath

def rect_zero() -> Rect:
    return (0,0,0,0)
def rect_margin(top: float = 0, right: float = 0, bottom : float = 0, left: float = 0) -> Rect:
    return (left, top, -left-right, -top-bottom)

def default_font() -> pygame.font.Font:
    return pygame.font.SysFont("Arial", 16, False)

class ElementStatus(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2

Size: TypeAlias = tuple[int,int]
Point: TypeAlias = tuple[int,int]
RelativePoint: TypeAlias = tuple[float,float]

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
    def __init__(self, pivot_point: Point):
        self.point = pivot_point

    @property
    def x(self):
        return self.point[0]
    @x.setter
    def x(self, value: float):
        self.point[0] = value
    @property
    def y(self):
        return self.point[1]
    @y.setter
    def y(self, value: float):
        self.point[1] = value

    @staticmethod
    def from_alignment(alignment: FullAlignment):
        x_align, y_align = FullAlignment.split_axes(alignment)
        return Pivot((x_align / 2, y_align / 2))
    def align_in_rect(self, container: Rect, size: Size) -> Rect:
        bx, by, cx, cy = container
        sx, sy = size
        px, py = self.point

        pad_x = (cx - sx) * px
        pad_y = (cy - sy) * py

        return (bx + pad_x, by + pad_y, sx, sy)
    
    def backwards_align_in_rect(self, container: Rect, size: Size) -> Rect:
        bx, by, cx, cy = container
        sx, sy = size
        px, py = self.point

        pad_x = (cx - sx) * px
        pad_y = (cy - sy) * py

        return (bx - pad_x, by - pad_y, sx, sy)

    def grow(self, point: Point, size: Size) -> Rect:
        px, py = point
        sx, sy = size
        return (px - sx * self.x, py - sy * self.y, sx, sy)
    
    def backwards_grow(self, rect: Rect) -> Rect:
        px, py, sx, sy = rect
        return (px + sx * self.x, py + sy * self.y, sx, sy)
    
    def point_in_rect(self, rect: Rect) -> Point:
        px, py, sx, sy = rect
        return (px + sx * self.x, py + sy * self.y)
    
    def __repr__(self) -> str:
        return f"Pivot({self.x:.0%},{self.y:.0%})"

class Drawable(metaclass=ABCMeta):
    @abstractmethod
    def render(self, surface: Surface):
        raise NotImplementedError

class Anchor:
    def __init__(self, min_anchor: RelativePoint = (0,0), max_anchor: RelativePoint = (0,0), pivot: Pivot = Pivot((0,0))):
        self.min_anchor = min_anchor
        self.max_anchor = max_anchor
        self.pivot = pivot

    def relative_size(self):
        return TupleMath.sub(self.max_anchor, self.min_anchor)
    def size(self, container_size: Size):
        return TupleMath.mult(self.relative_size(), container_size)
    def anchor_rect(self, container: Rect) -> Rect:
        x,y,sx,sy = container
        pos = (x,y)
        sz = (sx,sy)
        return (*TupleMath.add(pos, TupleMath.mult(sz, self.min_anchor)), *self.size(sz))

    @staticmethod
    def expand() -> "Anchor":
        return Anchor((0,0), (1,1), Pivot((0.5, 0.5)))
    @staticmethod
    def from_pivot(pivot: Pivot) -> "Anchor":
        return Anchor(pivot.point, pivot.point, pivot)
    @staticmethod
    def from_relative_point(x_rel,y_rel):
        rel_point = (x_rel,y_rel)
        return Anchor(rel_point,rel_point,Pivot(rel_point))

    def get_rect(self, container: Rect, local_rect: Rect = (0,0,0,0)):
        x_offset, y_offset, sx, sy = local_rect
        _, _, csx, csy = container

        final_size = TupleMath.add((sx,sy), self.size((csx,csy)))
        global_pivot_point = TupleMath.add((x_offset, y_offset), self.pivot.point_in_rect(self.anchor_rect(container)))

        return self.pivot.grow(global_pivot_point, final_size)
    
    def backwards_fit(self, container: Rect, global_rect: Rect):
        unpivoted_rect = self.pivot.backwards_grow(global_rect)

        x, y, sx, sy = unpivoted_rect
        _, _, csx, csy = container

        local_size = TupleMath.sub((sx,sy), self.size((csx,csy)))
        local_offset = TupleMath.sub((x,y), self.pivot.point_in_rect(self.anchor_rect(container)))

        return (*local_size, *local_offset)
    
    def __repr__(self):
        return f"Anchor(X:{self.min_anchor[0]:.0%}-{self.max_anchor[0]:.0%},Y:{self.min_anchor[1]:.0%}-{self.max_anchor[1]:.0%};{self.pivot})"

@Drawable.register
class Element():
    def __init__(self, name: str = "Unnamed Element", local_rect: Rect = (0,0,0,0), anchor: Anchor = Anchor(), parent: "Element | None" = None):
        self._local_rect = local_rect
        self._rect = local_rect
        self.name = name
        self.anchor = anchor
        self.parent = parent
        if parent: parent.add_child(self)
        self.enable_render = True
        self.enable_culling = True
        self._children: list[Element] = []
        self.set_rect_dirty()

    def add_child(self, child: "Element"):
        self._children.append(child)
        child.rect_dirty = True
        child.parent = self

    def add_children(self, children: "list[Element]"):
        for c in children:
            self.add_child(c)

    def remove_child(self, child: "Element"):
        self._children.remove(child)
        child.rect_dirty = True

    def remove_all_children(self):
        self._children.clear()
        
    def get_children(self) -> "list[Element]":
        return self._children
    
    def get_child_by_name(self, name) -> "Element | None":
        for c in self._children:
            if c.name == name:
                return c
        return None
    
    def set_rect_dirty(self):
        self.rect_dirty = True
        for c in self.get_children():
            c.set_rect_dirty()

    def send_to_back(self):
        if not self.parent: return
        self.parent.remove_child(self)
        self.parent._children.insert(0, self)
    
    def send_to_front(self):
        if not self.parent: return
        self.parent.remove_child(self)
        self.parent.add_child(self)

    def translate(self, delta_x, delta_y):
        x,y,sx,sy = self.local_rect
        self.local_rect = (x+delta_x, y+delta_y, sx, sy)

    def rendered(self):
        if not self.enable_render: return False
        if self.parent and not self.parent.rendered(): return False
        return True

    @property
    def local_rect(self):
        return self._local_rect
    @local_rect.setter
    def local_rect(self, value: Rect):
        self._local_rect = value
        self.set_rect_dirty()

    @property
    def rect(self):
        if self.rect_dirty:
            self.recalculate()
        return self._rect
    @rect.setter
    def rect(self, value: Rect):
        if self.parent:
            self._local_rect = self.anchor.backwards_fit(self.parent.rect, value)
        else:
            self._local_rect = value
        self.set_rect_dirty()

    def recalculate(self):
        self.rect_dirty = False
        if self.parent:
            self._rect = self.anchor.get_rect(self.parent.rect, self.local_rect)
        else: 
            self._rect = self.local_rect

    def render(self, screen: Surface):
        pass

    def render_as_root(self, screen: Surface):
        if not self.enable_render: return
        if self.enable_culling and not Rect(self.rect).colliderect(screen.get_rect()): return
        self.render(screen)
        for c in self._children:
            c.render_as_root(screen)

    def path_to_object(self) -> str:
        if self.parent:
            return f"{self.parent.path_to_object()} > {self.name}"
        return self.name

    def __repr__(self):
        return f"{self.name} [{self.__class__.__name__}]"

class TextElement(Element):
    def __init__(self, name: str, rect: Rect, text: str, color: Color = (255,255,255), font: pygame.font.Font | None = None, text_pivot: Pivot = Pivot((0.5,0.5)), anchor: Anchor = Anchor.expand(), parent: Element | None = None):
        super().__init__(name, rect, anchor, parent)
        self._text = text
        self._color = color
        self._font = font or default_font()
        self.text_pivot = text_pivot
        self.text_dirty = True

    def recompute_render(self):
        color = Color(self.color)
        self.text_img = self.font.render(self.text, True, self.color)
        self.text_img.set_alpha(color.a)
        self.text_dirty = False

    @property
    def text(self):
        return self._text
        
    @text.setter
    def text(self, value: str):
        self._text = value
        self.text_dirty = True

    @property
    def color(self):
        return self._color
        
    @color.setter
    def color(self, value: Color):
        self._color = value
        self.text_dirty = True
        
    @property
    def font(self):
        return self._font
        
    @font.setter
    def font(self, value: pygame.font.Font):
        self._font = value
        self.text_dirty = True

    def render(self, surface: Surface):
        if self.text_dirty:
            self.recompute_render()
        size = self.text_img.get_size()
        text_rect = self.text_pivot.grow(self.text_pivot.point_in_rect(self.rect), size)
        surface.blit(self.text_img, text_rect)

class RectElement(Element):
    def __init__(self, name: str, rect: Rect, anchor: Anchor = Anchor(), color: Color | None = None, border_radius: int = -1, text: TextElement | None = None, parent: Element | None = None):
        super().__init__(name, rect, anchor, parent)
        self.status = ElementStatus.NORMAL
        self.color = color
        self.border_radius = border_radius
        self.text = text
        if text: self.add_child(text)

    def hovered(self, mouse_pos: Point):
        x,y,sx,sy = self.rect
        mx,my = mouse_pos

        return mx > x and my > y and mx <= x + sx and my <= y + sy

    def add_text(self, text: str, font: pygame.font.Font, color: Color = (0,0,0), pivot: Pivot = Pivot((0.5,0.5))):
        self.text = TextElement("Text", rect_zero(), text, color, font, pivot, parent=self)

    def render(self, surface: Surface):
        if self.color: pygame.draw.rect(surface, self.color, self.rect, border_radius=self.border_radius)

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
    def __init__(self, name: str, rect: Rect, anchor: Anchor = Anchor(), colors: ColorBlock | None = None, border_radius: int = -1, text: TextElement | None = None, parent: Element | None = None):
        super().__init__(name, rect, anchor, None, border_radius, text, parent)
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
        if not self.rendered(): return

        intersects = self.hovered(mouse_pos)
        if not intersects: return

        self.status = ElementStatus.PRESSED
        for f in self.on_press: f()

    def onmouseup(self, mouse_pos: tuple[float, float]):
        if not self.enabled: return
        if not self.rendered(): return

        intersects = self.hovered(mouse_pos)
        if not intersects:
            self.status = ElementStatus.NORMAL
        elif self.status == ElementStatus.PRESSED:
            for f in self.on_click: f()
            for f in self.on_unpress: f()
            self.status = ElementStatus.HOVER

class Sprite(RectElement):
    def __init__(self, name: str, rect: Rect, img_path: str, anchor: Anchor = Anchor(), parent: Element | None = None):
        super().__init__(name, rect, anchor, parent = parent)
        self._img_path = img_path
        self.sprite_dirty = True
        self.img = None

    def reload_img(self):
        self.sprite_dirty = False
        if not os.path.exists(self.img_path):
            self.img = None
            return
        img = pygame.image.load(self.img_path).convert()
        x,y, *size = self.rect
        self.img = pygame.transform.scale(img, size)

    @property
    def img_path(self):
        return self._img_path
    @img_path.setter
    def img_path(self, value: str):
        self._img_path = value
        self.sprite_dirty = True

    @property
    def rect(self):
        return super().rect
    @rect.setter
    def rect(self, value: Rect):
        super().rect = value
        self.sprite_dirty = True

    def render(self, surface: Surface):
        if self.sprite_dirty:
            self.reload_img()
        if self.img: surface.blit(self.img, self.rect)