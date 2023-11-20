from urllib.request import urlretrieve, urlopen
from os import path

from pokemon import read_pokemon

pokemon_info = read_pokemon()

forms = {
    "alola" : "-a",
    "galar" : "-g",
    "paldea": "-p",
    "midnight" : "-m",
    "dusk": "-d"
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

    path, message = urlretrieve(f"https://www.serebii.net/pokedex-sv/icon/new/{str(pokemon.num).rjust(3,'0')}{s}.png", filename)