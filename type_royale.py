# importing required library
from collections import defaultdict
import math
from os import path
from random import Random
import pygame
from lib.mathlib import lerp
from lib.ui.button import Button
from lib.ui.ui_base import ColorBlock, Drawable, Sprite, TextElement

from pokemon import Pokemon, read_config, read_pokemon
from lib.royalelib import *
from session.session import Session
 
# activate the pygame library .
pygame.init()
X = 1200
Y = 650
IMG_SIZE = 300
IMG_MARGIN = 50
BTN_BORDER_RADIUS = 8
BTN_BASELINE = 550
BTN_SPACING = 10
BTN_SIZE = 80

LEFT_IMG_X = X/2 - IMG_MARGIN * 2- IMG_SIZE
RIGHT_IMG_X = X/2 + IMG_MARGIN * 2
 
# create the display surface object
# of specific dimension..e(X, Y).
scrn = pygame.display.set_mode((X, Y))
 
# set the pygame window name
pygame.display.set_caption('Pokemon Royale')

font = pygame.font.Font('fonts/rubik/static/Rubik-Regular.ttf', 32)

buttons: list[Button] = []
renderables: list[Drawable] = []
 
weights = defaultdict(float)
config = read_config()

pokemon_list = read_pokemon()
eligible_list = filter_eligible(pokemon_list)
matchups : dict[int, set[int]] = defaultdict(set)

id_to_index = dict()
for i,p in enumerate(eligible_list):
    id_to_index[p.id] = i

elo = [500 for p in eligible_list]
l_rate = [400 for p in eligible_list]

session: Session = Session().load()

if savefile_exists(session.savefile):
    elo, l_rate = load(session.savefile)
else:
    save(session.savefile, elo, l_rate)

rng = Random()

MAX_ELO_DELTA_FOR_MATCHMAKING = 400
def match_weight_by_elo_delta(elo_delta: float) -> int:
    linear_p = max(0, (MAX_ELO_DELTA_FOR_MATCHMAKING - abs(elo_delta)) / MAX_ELO_DELTA_FOR_MATCHMAKING)
    nonlinear_p = pow(linear_p, 1.25)
    return int(500 * nonlinear_p)

def fetch_pokemon_pair() -> tuple[Pokemon, Pokemon]:
    main = rng.sample(eligible_list, 1, counts=elo)[0]
    main_index = eligible_list.index(main)
    main_elo = elo[main_index]
    counts = [0 if i == main_index or i in matchups[main_index]
        else match_weight_by_elo_delta(elo_val - main_elo) for i,elo_val in enumerate(elo)
    ]
    if sum(counts) == 0:
        return fetch_pokemon_pair()
    alt = rng.sample(eligible_list, 1, counts = counts)[0]
    return main, alt
    
left_pokemon, right_pokemon = fetch_pokemon_pair()

left_sprite = Sprite((LEFT_IMG_X, IMG_MARGIN, IMG_SIZE, IMG_SIZE), left_pokemon.image)
right_sprite = Sprite((RIGHT_IMG_X, IMG_MARGIN, IMG_SIZE, IMG_SIZE), right_pokemon.image)
left_name = TextElement((LEFT_IMG_X, IMG_MARGIN * 2 + IMG_SIZE, IMG_SIZE, IMG_MARGIN), "", (255,255,255), font)
right_name = TextElement((RIGHT_IMG_X, IMG_MARGIN * 2 + IMG_SIZE, IMG_SIZE, IMG_MARGIN), "", (255,255,255), font)
left_elo = TextElement((LEFT_IMG_X, IMG_MARGIN * 3 + IMG_SIZE, IMG_SIZE, IMG_MARGIN), "", (255,255,255), font)
right_elo = TextElement((RIGHT_IMG_X, IMG_MARGIN * 3 + IMG_SIZE, IMG_SIZE, IMG_MARGIN), "", (255,255,255), font)

def set_pokemon_pair(p1: Pokemon, p2: Pokemon):
    left_sprite.img_path = p1.image
    right_sprite.img_path = p2.image
    left_name.text = p1.name
    right_name.text = p2.name
    elo_left = elo[id_to_index[p1.id]]
    left_elo.text = f"{elo_left}"
    left_elo.color = config.elo_gradient.eval(elo_left)
    elo_right = elo[id_to_index[p2.id]]
    right_elo.text = f"{elo_right}"
    right_elo.color = config.elo_gradient.eval(elo_right)

    idx1 = id_to_index[p1.id]
    idx2 = id_to_index[p2.id]
    matchups[idx1].add(idx2)
    matchups[idx2].add(idx1)

def fetch_and_set_pokemon_pair():
    global left_pokemon
    global right_pokemon
    left_pokemon, right_pokemon = fetch_pokemon_pair()
    set_pokemon_pair(left_pokemon, right_pokemon)

l_rate_decay = 0.95
l_rate_min = 50
elo_min = 100

def evaluate_matchup(score: float):
    print(f"Evaluating {left_pokemon.name} vs {right_pokemon.name} [S={score:.2f}]")
    choose(left_pokemon, right_pokemon, score)

def choose(p1: Pokemon, p2: Pokemon, score):
    idx_w = id_to_index[p1.id]
    idx_l = id_to_index[p2.id]
    
    elo_w = elo[idx_w]
    elo_l = elo[idx_l]
    k_w = l_rate[idx_w]
    k_l = l_rate[idx_l]
    q_w = math.pow(10, elo_w/400)
    q_l = math.pow(10, elo_l/400)
    
    expected_score = q_w/(q_w + q_l)
    delta_w = k_w * (score - expected_score)
    delta_l = k_l * (expected_score - score)

    elo[idx_w] = max(elo_min, elo_w + int(delta_w))
    elo[idx_l] = max(elo_min, elo_l + int(delta_l))
    l_rate[idx_w] = max(l_rate_min, int(k_w * l_rate_decay))
    l_rate[idx_l] = max(l_rate_min, int(k_l * l_rate_decay))
    save(session.savefile, elo, l_rate)
    fetch_and_set_pokemon_pair()

def modify_both(p1: Pokemon, p2: Pokemon, result: float):
    idx_w = id_to_index[p1.id]
    idx_l = id_to_index[p2.id]

    for idx in (idx_w, idx_l):
        delta = result * l_rate[idx] / 2
        elo[idx] = max(elo_min, elo[idx] + int(delta))
        l_rate[idx] = max(l_rate_min, int(l_rate[idx] * l_rate_decay))

    save(session.savefile, elo, l_rate)
    fetch_and_set_pokemon_pair()

def boost_both():
    modify_both(left_pokemon, right_pokemon, 1)
def penalize_both():
    modify_both(left_pokemon, right_pokemon, -1)

def show_stats():
    tagged_scores = [(score, p.name) for score, p in zip(elo, eligible_list)]
    print(sorted(tagged_scores, reverse=True))

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

btn_cnt = len(scores)
btns_size_x = btn_cnt * BTN_SIZE + (btn_cnt - 1) * BTN_SPACING
for i, v in enumerate(score_values):
    new_rect = ((X + BTN_SPACING - btns_size_x) / 2 + (i * btns_size_x / btn_cnt), BTN_BASELINE - BTN_SIZE / 2, BTN_SIZE, BTN_SIZE)
    btn = Button(new_rect, value_to_colorblock(v), BTN_BORDER_RADIUS)
    display_value = v * 2 - 1
    btn.add_text(f"{'+' if display_value > 0 else ''}{display_value:.1f}", font)
    score_delta = 1 - v
    btn.on_click.append(lambda delta=score_delta: evaluate_matchup(delta))
    buttons.append(btn)
PROMO_BTN_WIDTH = 150
up_btn = Button((X / 2 - PROMO_BTN_WIDTH / 2, IMG_MARGIN * 2, PROMO_BTN_WIDTH, BTN_SIZE), ColorBlock((200,200,200),(180,180,180),(150,150,150)), BTN_BORDER_RADIUS)
up_btn.add_text("Promote", font, (0,0,0))
up_btn.on_click.append(boost_both)
down_btn = Button((X / 2 - PROMO_BTN_WIDTH / 2, IMG_SIZE, PROMO_BTN_WIDTH, BTN_SIZE), ColorBlock((55,55,55),(75,75,75),(105,105,105)), BTN_BORDER_RADIUS)
down_btn.add_text("Demote", font, (255,255,255))
down_btn.on_click.append(penalize_both)
buttons.extend([up_btn,down_btn])

renderables.extend(buttons)
renderables.extend([left_sprite, right_sprite, left_name, right_name, left_elo, right_elo])
set_pokemon_pair(left_pokemon, right_pokemon)

while (status):
    # iterate over the list of Event objects
    # that was returned by pygame.event.get() method.
    scrn.fill((0,0,0))
 
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        btn.onmousemoved(mouse_pos)
    for i in pygame.event.get():
        # if event object type is QUIT
        # then quitting the pygame
        # and program both.
        if i.type == pygame.QUIT:
            status = False
        if i.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                btn.onmousedown(mouse_pos)
        if i.type == pygame.MOUSEBUTTONUP:
            for btn in buttons:
                btn.onmouseup(mouse_pos)
        if i.type == pygame.KEYDOWN:
            for k, s in scores.items():
                if i.key == k:
                    choose(left_pokemon, right_pokemon, 1 - s)
            if i.key == pygame.K_UP:
                boost_both()
            if i.key == pygame.K_DOWN:
                penalize_both()
            if i.key == pygame.K_r:
                change_savefile(session)
                elo, l_rate = load()
                fetch_and_set_pokemon_pair()
            if i.key == pygame.K_s:
                show_stats()

    for r in renderables:
        r.render(scrn)

    pygame.display.update()
 
# deactivates the pygame library
pygame.quit()