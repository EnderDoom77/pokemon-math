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
    .container {{
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
    """

def to_html(pokemon: Pokemon, config : Config | None = None):
    if not config:
        config = read_config()
    return f"""
    <div class='pokemon {'' if pokemon.image else 'error'}'>
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
            <style>
                {css_types(config)}
                {base_css(config)}
            </style>
        </head>
        <body>
            <div class='container'>
            {''.join(to_html(p, config) for p in pokemon_list)}
            </div>
        </body>
    </html>
    """)
