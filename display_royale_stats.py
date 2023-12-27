from pokemon import Config, Pokemon, read_config, read_pokemon
from lib.htmllib import *
from lib.royalelib import *

pokemon_list = read_pokemon()
eligible_list = filter_eligible(pokemon_list)
id_to_idx = {p.id: i for i, p in enumerate(eligible_list)}

session = Session().load()
print(f"Loading data from savefile: {session.savefile}")
elo, l_rate = load(session.savefile)

def extra_info(p: Pokemon) -> str:
    return f"<p class='elo-display'> ELO: {elo[id_to_idx[p.id]]} </p>"
def extra_css(config: Config) -> str:
    return """
        .elo-display {
            color: #008800;
        }
    """

with open("web/pokestats.html", "w") as f:
    config = read_config()
    f.write(f"""
    <html>
        <head>
            <title>Pokemon Display</title>
            <script rel="text/javascript" src="pokedisplay.js"></script>
            <style>
                {css_types(config)}
                {base_css(config)}
                {extra_css(config)}
            </style>
        </head>
        <body>
            <div class='header'>
                {
                    ''.join(f'''
                        <button onclick='filterTag(`{tag}`)'>{tag.upper()}</button>
                    ''' for tag in all_tags)
                }
            </div>
            <div class='container'>
            {''.join(to_html(p, config, extra_info(p)) for p in sorted(eligible_list, key=lambda p: -elo[id_to_idx[p.id]]))}
            </div>
        </body>
    </html>
    """)
