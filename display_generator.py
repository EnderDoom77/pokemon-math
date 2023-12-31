from pokemon import Config, Pokemon, read_config, read_pokemon
from lib.htmllib import *

pokemon_list = read_pokemon()
with open("web/pokedisplay.html", "w") as f:
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
