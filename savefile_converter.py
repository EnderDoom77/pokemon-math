import json
from pokemon import read_config, read_pokemon, Pokemon, Config
from lib.royalelib import filter_eligible, load

savefile_name = input("Enter the name of your savefile: ")
eligible = filter_eligible(read_pokemon())

saved_elo, saved_k = load(savefile_name)

data = {}
data["eligible_pokemon"] = []
data["elo_info"] = {}
for i, pokemon in enumerate(eligible):
    data["eligible_pokemon"].append(pokemon.id)
    data["elo_info"][pokemon.id] = {
        "elo": saved_elo[i],
        "k": saved_k[i]
    }

with open(f"saves/{savefile_name}_godot.json", "w") as f:
    json.dump(data, f)
