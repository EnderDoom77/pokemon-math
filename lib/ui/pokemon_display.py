import pygame
from pygame import Rect, Color
from lib.ui.ui_base import *
from pokemon import PokeType, Pokemon, Config, read_config
from lib.mathlib import str_to_color, max_contrast

class TypeDisplay(RectElement):
    def __init__(self, type: PokeType, rect: Rect, anchor: Anchor = Anchor.from_pivot(Pivot((0.5,0.5))), border_radius: int = -1, font: pygame.font.Font = None, config: Config | None = None, parent: Element | None = None):
        if not config:
            config = read_config()
        type_color = str_to_color(config.type_colors[type])
        super().__init__(f"Type Display [{type}]" , rect, anchor, type_color, border_radius, None, parent)
        self.font = font
        text_color = max_contrast(type_color, tint=0.2)
        self.add_text(type.upper(), font, text_color)

@Drawable.register
class PokemonDisplay(RectElement):
    def __init__(self, name: str, rect: Rect, anchor: Anchor, pokemon: Pokemon, color: Color | None = None, border_radius: int = -1, font: pygame.font.Font | None = None, config: Config | None = None, parent: Element | None = None):
        super().__init__(name, rect, anchor, color, border_radius, parent=parent)
        self._pokemon = pokemon
        self.config = config or read_config()
        self.font = font
        self.image_display: Sprite | None = None
        self.name_display: TextElement | None = None
        self.type_display: Element | None = None

    @property
    def pokemon(self):
        return self._pokemon
    @pokemon.setter
    def pokemon(self, value: Pokemon):
        self._pokemon = value
        self.update_values()

    def update_values(self):
        if self.image_display: self.image_display.img_path = self.pokemon.image
        if self.name_display: self.name_display.text = self.pokemon.name
        if self.type_display: self.create_type_display()

    def create_type_display(self):
        self.type_display.remove_all_children()
        x_start = 0.75 - 0.25 * len(self.pokemon.types)
        x, y, sx, sy = self.rect
        border_radius = sy // 4
        for t in self.pokemon.types:
            _ = TypeDisplay(t, (0,0,-20,0), Anchor((x_start-0.25,0),(x_start+0.25,1),Pivot((0.5,0.5))), border_radius, font=self.font, config=self.config, parent=self.type_display)
            x_start += 0.5
        
    def add_image_display(self, local_rect: Rect, anchor: Anchor):
        self.image_display = Sprite("Pokemon Sprite", local_rect, self.pokemon.image, anchor, self)
    
    def add_name_display(self, local_rect: Rect, anchor: Anchor, text_pivot: Pivot = Pivot((0.5,0.5)), text_color: Color | None = None):
        if not text_color:
            text_color = (255,255,255)
        self.name_display = TextElement("Name Display", local_rect, self.pokemon.name, text_color, self.font, text_pivot, anchor, self)

    def add_type_display(self, local_rect: Rect, anchor: Anchor):
        self.type_display = Element("Type Display Container", local_rect, anchor, self)
        self.create_type_display()

