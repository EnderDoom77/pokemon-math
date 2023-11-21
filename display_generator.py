from pokemon import Config, Pokemon, read_config, read_pokemon

def html_type_display(type: str, config: Config | None = None):
    if not config:
        config = read_config()
    return f"""
        <div class='poke-type {type}'> 
            {type.upper()}
        </div>
    """

def css_types(config: Config | None):
    styles = [f"""
    .poke-type {{
        border: 2px solid white;
        border-radius: 1em;
        color: white;
        text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;
        padding: 3px 5px;
        margin: 0.5em;
        width: 6em;
    }}
    .type-display {{
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        width: 100%;
    }}
    """.strip()]
    for typename in config.types:
        styles.append(f"""
        .{typename} {{
            background-color: {config.type_colors[typename]};
        }}""".strip())
    return "\n".join(styles)

def base_css(config : Config | None = None):
    if not config:
        config = read_config()
    return f"""
    @font-face {{
        font-family: rubik;
        src: url(fonts/rubik/Rubik-VariableFont_wght.tff);
    }}
    body, button {{
        font-family: rubik, Verdana, sans-serif;
    }}

    .header {{
        position: fixed;
        top: 0;
        width: 100%;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: space-evenly;
        align-items: center;
        background-color: #ffaaaa;
        z-index: 10;
    }}

    .header button {{
        font-weight: bold;
        padding: 0.25em;
        font-size: 1.4em;
        border-radius: 2em;
        margin: 0.5em;
        border: 1px solid black;
        background-color: #ffffff;
    }}

    .header button:hover {{
        background-color: #cccccc;
        color: #880000;
    }}
    
    .container {{
        margin-top: 5em;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
        padding: 1em;
    }}
    
    .pokemon {{
        background-color: #88888830;
        border: 3px solid #444444;
        border-radius: 2em;
        margin: 1em;
        width: 15%;
        text-align: center;
        padding: 1em;
        position: relative;
    }}

    .pokemon > img {{
        min-height: 80px;
        max-height: 120px;
        image-rendering: pixelated;
    }}

    .pokemon > .name {{
        font-weight: bold;
    }}

    .pokemon > .num {{
        position: absolute;
        left: 1em;
        top: 0.5em;
        font-weight: bold;
    }}

    .error {{
        background-color: #ff5555;
    }}

    .hidden {{
        display: none;
    }}
    """

all_tags = [
    "pokemon",
    "base",
    "regional",
    "alola",
    "hisui",
    "paldea",
    "galar",
    "gmax",
    "mega",
    "totem",
    "alt-types",
    "misc"
]
def get_tags(pokemon: Pokemon):
    tags = set()
    if pokemon.is_base:
        tags.add("base")
    if pokemon.is_regional:
        tags.add("regional")
    if pokemon.alt_types:
        tags.add("alt-types")
    if pokemon.misc_variant:
        tags.add("misc")
    tags.update(pokemon.formes)
    return tags

def to_html(pokemon: Pokemon, config : Config | None = None):
    if not config:
        config = read_config()
    return f"""
    <div class='pokemon {'' if pokemon.image else 'error'} {' '.join(get_tags(pokemon))}'>
        <img src='{pokemon.image}' alt='{pokemon.name} icon'>
        <p class='name'>{pokemon.name}</p>
        <p class='num'>#{pokemon.num}</p>
        <div class='type-display'>
        {''.join(html_type_display(t, config) for t in pokemon.types)}
        </div>
    </div>
    """

pokemon_list = read_pokemon()
with open("pokedisplay.html", "w") as f:
    config = read_config()
    f.write(f"""
    <html>
        <head>
            <title>Pokemon Display</title>
            <script rel="text/javascript" src="pokedisplay.js"></script>
            <style>
                {css_types(config)}
                {base_css(config)}
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
            {''.join(to_html(p, config) for p in pokemon_list)}
            </div>
        </body>
    </html>
    """)
