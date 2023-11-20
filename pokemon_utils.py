from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import pandas as pd
from pokemon import Pokemon, read_config

def get_type_bar_chart(pokemons: list[Pokemon], type_weights: list[int] = [1,1], ax: Axes = None) -> Axes:
    hist = defaultdict(int)
    config = read_config()
    for p in pokemons:
        for t,w in zip(p.types,type_weights):
            hist[t] += w

    type_data = [(hist[t], t) for t in config.types]
    sorted_type_data = sorted(type_data, reverse=True)

    df = pd.DataFrame({"types": [t for _,t in sorted_type_data], "frequencies": [f for f,_ in sorted_type_data]})

    bar_colors = [config.type_colors[t] for _,t in sorted_type_data]

    if not ax:
        fig, ax = plt.subplots()

    ax.bar(df["types"], df["frequencies"], color=bar_colors)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    return ax
    