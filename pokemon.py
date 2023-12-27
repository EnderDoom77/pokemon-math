from collections import defaultdict
import json
from os import path
from typing import Literal, TypeAlias
import re

from lib.mathlib import parse_gradient

PokeType = Literal["normal", "fire", "water", "grass", "electric", "ice", "rock", "fairy", "dragon", "steel", "fighting", "poison", "flying", "psychic", "ground", "bug", "ghost", "dark"]
PokeStat = Literal["hp", "atk", "def", "spa", "spd", "spe"]

def normalize_name(name : str):
    return "".join([c for c in name.lower() if c.isalnum()])

regions = {"alola", "galar", "paldea", "hisui"}

class Pokemon:
    def __init__(self, 
        id:str, num:int, name:str, types:list[str],
        baseStats: dict[PokeStat, float], abilities: dict[str,str] = {},
        heightm: float = -1, weightkg: float = -1, color: str = "", gender = "", forme = "",
        evos: list[str] = [], prevo: str = "", evoType: str = "level", evoCondition = "", evoLevel: int = -1, 
        eggGroups: list[str] = [], tier: str = "",
        **kwargs):
        
        # A normalized name containing only alphanumeric
        self.id = id 
        # The numeric Pokedex id of the pokemon
        self.num = num
        # The stylized English name of the pokemon
        self.name = name
        # The type(s) of the pokemon
        self.types : list[PokeType] = [normalize_name(t) for t in types]
        # Dictionary linking stat names to their base value
        self.base_stats : defaultdict[PokeStat, int] = defaultdict(int)
        for k,v in baseStats.items(): self.base_stats[k] = v
        # Strings normalized by `normalize_name` of the starting ability values
        self.abilities = [normalize_name(s) for s in abilities.values()]
        # The height in meters
        self.height = heightm
        # The weight in kilograms
        self.weight = weightkg
        # A descriptive single color for the pokemon
        self.color: color 
        # Any other pokemon that this pokemon can evolve into
        self.evolutions = evos
        # A pokemon (if any) that this pokenon evolves from
        self.preevolution = prevo
        # The type of evolution that this pokemon has (e.g. level, levelFriendship, useItem, trade, other...)
        self.evolution_type = evoType
        # The condition (if any) for this pokemon to evolve
        self.evolution_condition = evoCondition
        # The level required for this pokemon to evolve. -1 if unknown or no level is required
        self.evolution_level = evoLevel
        # The specific gender of this pokemon, if forced to be one (M,F) or is genderless (N), otherwise this is empty
        self.gender = gender
        # The egg groups that this pokemon falls into
        self.egg_groups = eggGroups
        # Competitive tier of the pokemon
        self.tier = tier
        # Any special forms that apply to this variant
        self.formes = [f.lower() for f in forme.split("-") if f]

        # Postprocessing variables
        self.is_regional = False
        for r in regions:
            if r in self.formes:
                self.region = r
                self.is_regional = True
                break
        # self.starter = "starter" in self.formes
        self.is_mega = "mega" in self.formes
        self.is_gmax = "gmax" in self.formes
        self.is_totem = "totem" in self.formes
        self.is_base = (self.formes == []) and (self.num > 0)

        self.alt_types = False
        self.misc_variant = not (self.is_base or self.is_regional or self.is_mega or self.is_gmax or self.is_totem)

        self.image : str | None = None
        img_path = f"img/{str(self.num).rjust(4,'0')}_{self.id}.png"
        if path.exists(img_path):
            self.image = img_path
        
        self.misc : dict[str, any] = {}
        for k,v in kwargs.items():
            self.misc[k] = v

    def from_dict(pokemon_id, data : dict[str, any]) -> "Pokemon":
        return Pokemon(pokemon_id, **data)
    
    def __lt__(self, other : "Pokemon"):
        return self.num < other.num
    def __le__(self, other : "Pokemon"):
        return self.num <= other.num
    def __gt__(self, other : "Pokemon"):
        return self.num > other.num
    def __ge__(self, other : "Pokemon"):
        return self.num >= other.num

    def __repr__(self):
        return f"{self.id} - {self.types}"

class Config:
    def __init__(self, 
        types : list[PokeType],
        type_colors : dict[PokeType, str], 
        type_effectiveness : list[list[float]],
        stats : list[PokeStat],
        elo_gradient: dict[str,str],    
        **kwargs):
        
        self.types = types
        self.type_colors = type_colors
        self.type_effectiveness = type_effectiveness
        self.stats = stats
        self.elo_gradient = parse_gradient(elo_gradient)

        self.misc : dict[str, any] = dict()
        for k,v in kwargs.items():
            self.misc[k] = v

    def from_dict(data : dict[str, any]) -> "Config":
        return Config(**data)

def postprocess_pokemon(pokemon_list: list[Pokemon]):
    current_num = 0
    current_types = ""
    for p in pokemon_list:
        if p.num != current_num:
            current_num = p.num
            current_types = "_".join(p.types)
            p.misc_variant = False
            continue
        if "_".join(p.types) != current_types:
            p.alt_types = True

def read_config() -> Config:
    with open("data/config.json") as f:
        data = json.load(f)
        return Config.from_dict(data)
    
def read_pokemon() -> list[Pokemon]:
    with open("data/pokedex.json") as f:
        pokedex : dict[str,dict] = json.load(f)
        basic = [Pokemon.from_dict(entry, p_dict) for entry,p_dict in pokedex.items()]
        postprocess_pokemon(basic)
        return basic