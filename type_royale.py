# importing required library
from collections import defaultdict
import math
from os import path
from random import Random
from typing import Callable
import pygame
from pygame import Color
from lib.mathlib import calc_elo_delta, clamp01, lerp, signed
from lib.ui.button import Button
from lib.ui.pokemon_display import PokemonDisplay
from lib.ui.ui_base import Anchor, ColorBlock, Drawable, Element, Pivot, Sprite, TextElement, rect_zero

from pokemon import Pokemon, read_config, read_pokemon
from lib.royalelib import *
from session.session import Session

def color_from_sign(value: float | int, alpha = 255) -> Color:
    return (
        (150,150,150,alpha) if value == 0 else
        (0  ,255,0  ,alpha) if value >  0 else
        (255,0  ,0  ,alpha)
    )

# activate the pygame library .
pygame.init()
X = 1200
Y = 800
IMG_SIZE = 300
IMG_MARGIN = 50
BTN_BORDER_RADIUS = 8
BTN_BASELINE = Y - 100
BTN_SPACING = 10
BTN_SIZE = 80
PROMO_BTN_WIDTH = 150

DISPLAY_CENTER_OFFSET = PROMO_BTN_WIDTH / 2 + IMG_MARGIN

ELO_DELTA_DISPLAY_TIME = 2.5
 
# create the display surface object
# of specific dimension..e(X, Y).
scrn = pygame.display.set_mode((X, Y))
root = Element("Root", (0,0,X,Y))
 
# set the pygame window name
pygame.display.set_caption('Pokemon Royale')

font = pygame.font.Font('fonts/rubik/static/Rubik-Regular.ttf', 32)
large_font = pygame.font.Font('fonts/rubik/static/Rubik-Regular.ttf', 56)

buttons: list[Button] = []
screens: dict[str, Element] = {}
screens["royale"] = Element("Royale Screen", rect_zero(), Anchor.expand(), root)
screens["leaderboard"] = Element("Leaderboard Screen", rect_zero(), Anchor.expand(), root)

for s in screens.values():
    s.enable_render = False

current_screen = "royale"
def set_screen(screen_name):
    global current_screen
    screens[current_screen].enable_render = False
    current_screen = screen_name
    screens[current_screen].enable_render = True
set_screen(current_screen)

TAB_MARGINS = 3
TAB_SIZE = 200
scr_btn_x = TAB_MARGINS
tab_selector = Element("Tab Selector", (0,0,0,IMG_MARGIN), Anchor((0,0),(1,0),Pivot((0.5,0))),root)
tab_colorblock = ColorBlock((255,255,255),(200,200,200),(175,175,175))
for screen_name, screen in screens.items():
    btn = Button(f"{screen_name} Screen Selector", (scr_btn_x,0,TAB_SIZE,-2*TAB_MARGINS), Anchor((0,0),(0,1),Pivot((0,0.5))), colors=tab_colorblock, border_radius=5, parent=tab_selector)
    btn.add_text(screen_name.capitalize(), font)
    btn.on_click.append(lambda screen_name=screen_name: set_screen(screen_name))
    buttons.append(btn)
    scr_btn_x += TAB_SIZE + TAB_MARGINS * 2

weights = defaultdict(float)
config = read_config()

pokemon_list = read_pokemon()
eligible_list = filter_eligible(pokemon_list)
matchups : dict[int, set[int]] = defaultdict(set)

id_to_index = dict()
for event,p in enumerate(eligible_list):
    id_to_index[p.id] = event

DEFAULT_ELO = 500
DEFAULT_K_VALUE = 400
elo = [DEFAULT_ELO for p in eligible_list]
l_rate = [DEFAULT_K_VALUE for p in eligible_list]
L_RATE_DECAY = 0.95
L_RATE_MIN = 50
ELO_MIN = 100

session: Session = Session().load()

if savefile_exists(session.savefile):
    elo, l_rate = load(session.savefile)
else:
    save(session.savefile, elo, l_rate)

original_elo = elo.copy()

rng = Random()

MAX_ELO_DELTA_FOR_MATCHMAKING = 400
def match_weight_by_elo_delta(elo_delta: float) -> int:
    linear_p = max(0, (MAX_ELO_DELTA_FOR_MATCHMAKING - abs(elo_delta)) / MAX_ELO_DELTA_FOR_MATCHMAKING)
    nonlinear_p = pow(linear_p, 1.25)
    return int(500 * nonlinear_p)

def get_pokemon_matchup_weight(pokemon: Pokemon) -> int:
    idx = id_to_index[pokemon.id]

    p_elo = elo[idx]
    p_k_value = l_rate[idx]
    exponent = 1.4 # default elo weight exponent
    if p_k_value >= DEFAULT_K_VALUE: # never competed
        exponent = 2.5 # we really want to show this pokemon!
    if p_elo <= ELO_MIN:
        exponent = 0.8 # This pokemon has a very bad track record, we should not show it
    
    return int(math.pow(p_elo, exponent) * (p_k_value / DEFAULT_K_VALUE))

def fetch_pokemon_pair() -> tuple[Pokemon, Pokemon]:
    main = rng.sample(eligible_list, 1, counts=[get_pokemon_matchup_weight(p) for p in eligible_list])[0]
    main_index = id_to_index[main.id]
    main_elo = elo[main_index]
    counts = [0 if i == main_index or i in matchups[main_index]
        else match_weight_by_elo_delta(elo_val - main_elo) for i,elo_val in enumerate(elo)
    ]
    if sum(counts) == 0:
        return fetch_pokemon_pair()
    alt = rng.sample(eligible_list, 1, counts = counts)[0]
    return main, alt
    
left_pokemon, right_pokemon = fetch_pokemon_pair()
left_elo_delta, right_elo_delta = 0,0
elo_delta_timer = 0

POKE_DISPLAY_BG_COLOR = Color(10,10,10)
left_display = PokemonDisplay("Left Display", (-DISPLAY_CENTER_OFFSET, IMG_MARGIN, 2 * IMG_MARGIN + IMG_SIZE, IMG_SIZE + 5 * IMG_MARGIN), Anchor((0.5,0),(0.5,0),pivot=Pivot((1,0))), left_pokemon, POKE_DISPLAY_BG_COLOR, border_radius=IMG_MARGIN, font=font, config=config, parent=screens["royale"])
right_display = PokemonDisplay("Right Display", (DISPLAY_CENTER_OFFSET, IMG_MARGIN, 2 * IMG_MARGIN + IMG_SIZE, IMG_SIZE + 5 * IMG_MARGIN), Anchor((0.5,0),(0.5,0),pivot=Pivot((0,0))), right_pokemon, POKE_DISPLAY_BG_COLOR, border_radius=IMG_MARGIN, font=font, config=config, parent=screens["royale"])

texts: list[TextElement] = []
for display in [left_display, right_display]:
    display.add_image_display((0,IMG_MARGIN,IMG_SIZE,IMG_SIZE), Anchor((0.5,0),(0.5,0),Pivot((0.5,0))))
    info_anchor = Anchor((0,1),(1,1),Pivot((0.5,1)))
    display.add_name_display((0,-2.5 * IMG_MARGIN,0,IMG_MARGIN), info_anchor, text_color=(255,255,255))
    display.add_type_display((0,-1.5 * IMG_MARGIN,0,IMG_MARGIN), info_anchor)
    texts.append(TextElement("Elo Display", (0,-0.5 * IMG_MARGIN,0,IMG_MARGIN), "", color=(255,255,255), anchor=Anchor((0,1),(1,1),Pivot((0.5,1))), font=font, parent=display))
left_elo_text = texts[0]
right_elo_text = texts[1]
left_elo_delta_text = TextElement("Left Elo Delta" , ( 25,-25,0,0), "(0)", (150,150,150,0), large_font, Pivot((0,1)), Anchor.from_relative_point(0,1),screens["royale"])
right_elo_delta_text = TextElement("Right Elo Delta", (-25,-25,0,0), "(0)", (150,150,150,0), large_font, Pivot((1,1)), Anchor.from_relative_point(1,1),screens["royale"])
left_elo_delta_text.enable_culling = False
right_elo_delta_text.enable_culling = False

def set_pokemon_pair(p1: Pokemon, p2: Pokemon):
    left_display.pokemon = p1
    right_display.pokemon = p2
    elo_left = elo[id_to_index[p1.id]]
    left_elo_text.text = f"{elo_left}"
    left_elo_text.color = config.elo_gradient.eval(elo_left)
    elo_right = elo[id_to_index[p2.id]]
    right_elo_text.text = f"{elo_right}"
    right_elo_text.color = config.elo_gradient.eval(elo_right)

    idx1 = id_to_index[p1.id]
    idx2 = id_to_index[p2.id]
    matchups[idx1].add(idx2)
    matchups[idx2].add(idx1)

def fetch_and_set_pokemon_pair():
    global left_pokemon
    global right_pokemon
    left_pokemon, right_pokemon = fetch_pokemon_pair()
    set_pokemon_pair(left_pokemon, right_pokemon)
    global elo_delta_timer
    elo_delta_timer = ELO_DELTA_DISPLAY_TIME

def evaluate_matchup(score: float):
    print(f"Evaluating {left_pokemon.name} vs {right_pokemon.name} [S={score:.2f}]")
    choose(left_pokemon, right_pokemon, score)

def choose(p1: Pokemon, p2: Pokemon, score):
    idx_left = id_to_index[p1.id]
    idx_right = id_to_index[p2.id]
    
    elo_left = elo[idx_left]
    elo_right = elo[idx_right]
    k_left = l_rate[idx_left]
    k_right = l_rate[idx_right]
    
    global left_elo_delta
    global right_elo_delta
    left_elo_delta = calc_elo_delta(elo_left, elo_right, k_left, score)
    right_elo_delta = calc_elo_delta(elo_right, elo_left, k_right, 1-score)

    elo[idx_left] = max(ELO_MIN, elo_left + left_elo_delta)
    elo[idx_right] = max(ELO_MIN, elo_right + right_elo_delta)
    l_rate[idx_left] = max(L_RATE_MIN, int(k_left * L_RATE_DECAY))
    l_rate[idx_right] = max(L_RATE_MIN, int(k_right * L_RATE_DECAY))
    save(session.savefile, elo, l_rate)
    fetch_and_set_pokemon_pair()

def modify_both(p1: Pokemon, p2: Pokemon, result: float):
    idx_w = id_to_index[p1.id]
    idx_l = id_to_index[p2.id]

    deltas = []
    for idx in (idx_w, idx_l):
        k = l_rate[idx]
        delta = calc_elo_delta(elo[idx], DEFAULT_ELO, k, result)
        deltas.append(delta)
        elo[idx] = max(ELO_MIN, elo[idx] + delta)
        l_rate[idx] = max(L_RATE_MIN, int(l_rate[idx] * L_RATE_DECAY))

    global left_elo_delta
    global right_elo_delta
    left_elo_delta, right_elo_delta = tuple(deltas)

    save(session.savefile, elo, l_rate)
    fetch_and_set_pokemon_pair()

def boost_both():
    modify_both(left_pokemon, right_pokemon, 1)
def penalize_both():
    modify_both(left_pokemon, right_pokemon, 0)

def show_stats():
    tagged_scores = [(score, p.name) for score, p in zip(elo, eligible_list)]
    print(sorted(tagged_scores, reverse=True))

LEADERBOARD_ITEM_MARGIN = 5
LEADERBOARD_ITEM_HEIGHT = 120
LEADERBOARD_POKE_IMG_SIZE = LEADERBOARD_ITEM_HEIGHT - 6
NAME_AND_TYPE_WIDTH = 450
ELO_AND_DELTA_WIDTH = 150
LEADERBOARD_ITEM_BG_COLOR = (20,20,20)
class LeaderboardItem():
    def __init__(self, index: int, pokemon: Pokemon, parent: Element | None = None):
        self.poke_display = PokemonDisplay(f"Leaderboard Item #{index}", 
            (0,LEADERBOARD_ITEM_MARGIN + index * (LEADERBOARD_ITEM_HEIGHT + LEADERBOARD_ITEM_MARGIN), -2 * LEADERBOARD_ITEM_MARGIN, LEADERBOARD_ITEM_HEIGHT), 
            Anchor((0,0),(1,0),Pivot((0.5,0))), pokemon, LEADERBOARD_ITEM_BG_COLOR, LEADERBOARD_ITEM_MARGIN, font, config, parent
        )
        self.rank_display = TextElement("Rank Display", (25,0,100,0), f"#{index}", (255,255,255), font, Pivot((0,0.5)), Anchor((0,0),(0,1),Pivot((0,0.5))), self.poke_display)
        left = 135
        self.poke_display.add_image_display((left, 0, LEADERBOARD_POKE_IMG_SIZE, LEADERBOARD_POKE_IMG_SIZE), Anchor.from_relative_point(0,0.5))
        left += LEADERBOARD_POKE_IMG_SIZE
        self.poke_display.add_name_display((left, 0, NAME_AND_TYPE_WIDTH, 0), Anchor((0,0),(0,0.5),Pivot((0,0.5))), Pivot((0,0.5)),(255,255,255))
        self.poke_display.add_type_display((left, 0, NAME_AND_TYPE_WIDTH, 45), Anchor((0,0.75),(0,0.75),Pivot((0,0.5))))
        left += NAME_AND_TYPE_WIDTH + 10
        self.elo_display = TextElement("Elo Display", (left, 0, ELO_AND_DELTA_WIDTH, 0), "-1", (255,255,255), font, Pivot((0.5,0.5)), Anchor((0,0),(0,0.5),Pivot((0,0.5))), parent=self.poke_display)
        self.elo_delta_display = TextElement("Elo Delta Display", (left, 0, ELO_AND_DELTA_WIDTH, 0), "(0)", (255,255,255), font, Pivot((0.5,0.5)), Anchor((0,0.5),(0,1),Pivot((0,0.5))),parent=self.poke_display)
    
    def get_elo_and_delta(self) -> tuple[int, int]:
        idx = id_to_index[self.poke_display.pokemon.id]
        elo_val = elo[idx]
        elo_delta = elo_val - original_elo[idx]
        return (elo_val, elo_delta)

    def set_pokemon(self, pokemon: Pokemon, index: int):
        self.poke_display.pokemon = pokemon
        self.rank_display.text = f"#{index+1}"
        idx = id_to_index[pokemon.id]
        elo_v, elo_d = self.get_elo_and_delta()
        elo_color = config.elo_gradient.eval(elo_v)
        self.elo_display.text = f"ELO: {elo[idx]}"
        self.elo_display.color = elo_color
        self.elo_delta_display.text = f"({signed(elo_d)})"
        self.elo_delta_display.color = color_from_sign(elo_d)

leaderboard_items: list[LeaderboardItem] = []    
leaderboard_container = Element("Leaderboard", (10, IMG_MARGIN * 2, -210, 0), Anchor((0,0),(1,0),Pivot((0,0))), screens["leaderboard"])
leaderboard_container.enable_culling = False
def set_leaderboard(pokemons: list[Pokemon]):
    for i,p in enumerate(pokemons):
        if i >= len(leaderboard_items):
            leaderboard_items.append(LeaderboardItem(i, p, leaderboard_container))
        leaderboard_items[i].set_pokemon(p, i)
            
set_leaderboard(eligible_list)
leaderboard_buttons: list[Button] = []
leaderboard_controls = Element("Leaderboard Selector", (0, 1.5 * IMG_MARGIN, -2 * TAB_MARGINS, IMG_MARGIN - 2 * TAB_MARGINS), Anchor((0,0),(1,0),Pivot((0.5,0.5))),parent=screens["leaderboard"])
left_x = TAB_MARGINS
def sort_leaderboard(key: Callable[[Pokemon],any], reverse: bool = False):
    new_list = sorted(eligible_list, key=key, reverse=reverse)
    set_leaderboard(new_list)

def abs_elo_delta_from_original(p: Pokemon):
    idx = id_to_index[p.id]
    return abs(elo[idx] - original_elo[idx])

left = 0
for btn_name, func in [
    ("Pokedex #", lambda p:p.num),
    ("Name", lambda p:p.name),
    ("Elo", lambda p:-elo[id_to_index[p.id]]),
    ("Elo Delta", lambda p: -abs_elo_delta_from_original(p))
]:
    btn = Button(f"Leaderboard Sort By {btn_name} Button", (left, 0, TAB_SIZE, 0), Anchor((0,0),(0,1),Pivot((0,0.5))), tab_colorblock, TAB_MARGINS, parent=leaderboard_controls)
    btn.add_text(btn_name, font)
    btn.on_click.append(lambda f=func: sort_leaderboard(f))
    left += TAB_SIZE + TAB_MARGINS
    leaderboard_buttons.append(btn)

buttons.extend(leaderboard_buttons)

# paint screen one time
pygame.display.flip()
status = True

scores = {
    pygame.K_1: 0,
    pygame.K_2: 0.1,
    pygame.K_3: 0.25,
    pygame.K_4: 0.4,
    pygame.K_5: 0.5,
    pygame.K_6: 0.6,
    pygame.K_7: 0.75,
    pygame.K_8: 0.9,
    pygame.K_9: 1
}
score_values = sorted(scores.values())

def value_to_colorblock(v:float) -> ColorBlock:
    return ColorBlock(
        lerp((255,150,150),(150,150,255), v), 
        lerp((255,100,100),(100,100,255), v), 
        lerp((200,0,0), (0,0,200), v)
    )
def update_deltas(text: TextElement, elo_delta: int, elo_delta_timer: float):
    new_str = f"({signed(elo_delta)})"
    alpha = math.floor(clamp01(elo_delta_timer / 0.5) * 255)
    text.text = new_str
    text.color = color_from_sign(elo_delta, alpha)
btn_cnt = len(scores)
btns_size_x = btn_cnt * BTN_SIZE + (btn_cnt - 1) * BTN_SPACING
for event, v in enumerate(score_values):
    new_rect = ((X + BTN_SPACING - btns_size_x) / 2 + (event * btns_size_x / btn_cnt), BTN_BASELINE - BTN_SIZE / 2, BTN_SIZE, BTN_SIZE)
    btn = Button(f"Button {v}", new_rect, colors=value_to_colorblock(v), border_radius=BTN_BORDER_RADIUS, parent=screens["royale"])
    display_value = v * 2 - 1
    btn.add_text(f"{'+' if display_value > 0 else ''}{display_value:.1f}", font)
    score_delta = 1 - v
    btn.on_click.append(lambda delta=score_delta: evaluate_matchup(delta))
    buttons.append(btn)
up_btn = Button("Promote Button", (X / 2 - PROMO_BTN_WIDTH / 2, IMG_MARGIN * 2, PROMO_BTN_WIDTH, BTN_SIZE), colors=ColorBlock((200,200,200),(180,180,180),(150,150,150)), border_radius=BTN_BORDER_RADIUS, parent=screens["royale"])
up_btn.add_text("Promote", font, (0,0,0))
up_btn.on_click.append(boost_both)
down_btn = Button("Demote Button", (X / 2 - PROMO_BTN_WIDTH / 2, IMG_SIZE, PROMO_BTN_WIDTH, BTN_SIZE), colors=ColorBlock((55,55,55),(75,75,75),(105,105,105)), border_radius=BTN_BORDER_RADIUS, parent=screens["royale"])
down_btn.add_text("Demote", font, (255,255,255))
down_btn.on_click.append(penalize_both)
buttons.extend([up_btn,down_btn])

set_pokemon_pair(left_pokemon, right_pokemon)

MOUSE_SENSITIVITY = 20
def scroll(delta_y):
    leaderboard_container.translate(0,delta_y * MOUSE_SENSITIVITY)

tab_selector.send_to_front()

clock = pygame.time.Clock()
while (status):
    # iterate over the list of Event objects
    # that was returned by pygame.event.get() method.
    scrn.fill((0,0,0))
    delta_time = clock.tick() / 1000
 
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        btn.onmousemoved(mouse_pos)
    for event in pygame.event.get():
        # if event object type is QUIT
        # then quitting the pygame
        # and program both.
        if event.type == pygame.QUIT:
            status = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                btn.onmousedown(mouse_pos)
        if event.type == pygame.MOUSEBUTTONUP:
            for btn in buttons:
                btn.onmouseup(mouse_pos)
        if event.type == pygame.MOUSEWHEEL:
            scroll(event.y)
        if event.type == pygame.KEYDOWN:
            for k, s in scores.items():
                if event.key == k:
                    choose(left_pokemon, right_pokemon, 1 - s)
            if event.key == pygame.K_UP:
                boost_both()
            if event.key == pygame.K_DOWN:
                penalize_both()
            if event.key == pygame.K_r:
                change_savefile(session)
                elo, l_rate = load()
                fetch_and_set_pokemon_pair()
            if event.key == pygame.K_s:
                show_stats()

    if elo_delta_timer > 0:
        elo_delta_timer -= delta_time
        update_deltas(left_elo_delta_text, left_elo_delta, elo_delta_timer)
        update_deltas(right_elo_delta_text, right_elo_delta, elo_delta_timer)

    root.render_as_root(scrn)

    pygame.display.update()
 
# deactivates the pygame library
pygame.quit()