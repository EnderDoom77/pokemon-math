from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

from pokemon import read_config, read_pokemon
from pokemon_utils import get_type_bar_chart

pokemon = read_pokemon()

weights = {
    "equal": [1,1],
    "primary": [1,0],
    "halfSecondary": [1,0.5],
    "secondary": [0,1]
}
fig, axs = plt.subplots(2, 2, squeeze=True)
axs = axs.flatten()

for (weight_names, weight), ax in zip(weights.items(), axs): 
    get_type_bar_chart(pokemon, weight, ax)
    ax.set_title(f"{weight_names} Weights")

plt.tight_layout()
plt.show()