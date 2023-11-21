from urllib.request import urlretrieve, urlopen
from os import path

from pokemon import read_pokemon

pokemon_info = read_pokemon()

forms = {
    "alola" : "-a",
    "galar" : "-g",
    "paldea": "-p",
    "midnight" : "-m",
    "dusk": "-d",
    "hisui": "-h",
    "paldeacombat": "-p",
    "paldeaaqua": "-a",
    "paldeablaze": "-b",
    "primal": "-p",
    "sandy": "-s",
    "trash": "-t",
    "sunshine": "-s",
    "mega": "-m",
    "megax": "-mx",
    "megay": "-my",
    "gmax": "-gi",
    "spikyeared": "-se",
    "sunny": "-s",
    "snowy": "-i",
    "rainy": "-r",
    "attack": "-a",
    "defense": "-d",
    "speed": "-s",
    "heat": "-h",
    "wash": "-w",
    "frost": "-f",
    "fan": "-s",
    "mow": "-m",
    "origin": "-o",
    "sky": "-s",
    "zen": "-z",
    "galarzen": "-gz",
    "therian": "-t",
    "black": "-b",
    "white": "-w",
    "resolute": "-r",
    "piruette": "-p",
    "ash": "-a",
    "eternal": "-e",
    "f": "-f",
    "10": "-10",
    "complete": "-c",
    "unbound": "-u", 
    "pompom": "-p",
    "pau": "-pau",
    "sensu": "-s",
    "school": "-s",
    "ultra": "-u",
    "duskmane": "-dm",
    "dawnwings": "-dw",
    "lowkey": "-l",
    "crowned": "-c",
    "eternamax": "-e",
    "rapidstrike": "-r",
    "bloodmoon": "-b",
    "ice": "-i",
    "shadow": "-s",
    "hero": "-h"
}
registered : set[tuple[int,str]] = set()

for pokemon in pokemon_info:
    if pokemon.num <= 0: continue
    new_id = pokemon.id
    s = ""
    for suffix,t_suffix in forms.items():
        if not new_id.endswith(suffix): continue
        new_id = new_id[:-len(suffix)]
        s = t_suffix

    key = (pokemon.num, s)
    if key in registered: continue
    registered.add(key)

    filename = f"img/{str(pokemon.num).rjust(4,'0')}_{pokemon.id}.png"
    if path.exists(filename): continue

    url = f"https://www.serebii.net/pokedex-sv/icon/new/{str(pokemon.num).rjust(3,'0')}{s}.png"
    try:
        img_path, message = urlretrieve(url, filename)
    except:
        print(f"Unable to download {pokemon} from url {url}")