# importing required library
from collections import defaultdict
import math
from os import path
from random import Random
import pygame
import json

from pokemon import Pokemon, read_pokemon
 
# activate the pygame library .
pygame.init()
X = 800
Y = 500
IMG_SIZE = 300
IMG_MARGIN = 50
 
# create the display surface object
# of specific dimension..e(X, Y).
scrn = pygame.display.set_mode((X, Y))
 
# set the pygame window name
pygame.display.set_caption('image')
 
weights = defaultdict(float)

pokemon_list = read_pokemon()
eligible_list = [p for p in pokemon_list if p.image and (p.is_base or (p.is_regional and not (p.is_totem or p.is_gmax or p.is_mega or p.num <= 0)))]

id_to_index = dict()
for i,p in enumerate(eligible_list):
    id_to_index[p.id] = i

elo = [500 for p in eligible_list]
l_rate = [400 for p in eligible_list]

def load(path):
    global elo
    global l_rate
    with open(path) as f:
        data = json.load(f)
        elo = data["elo"]
        l_rate = data["l_rate"]

def save(path):
    with open(path, "w") as f:
        data = {"elo": elo, "l_rate": l_rate}
        json.dump(data, f)

SAVEFILE = input("save file name: ")
SAVEFILE = f"saves/{SAVEFILE}.json"

if path.exists(SAVEFILE):
    load(SAVEFILE)
else:
    save(SAVEFILE)

rng = Random()

def fetch_pokemon_pair() -> tuple[Pokemon, Pokemon]:
    c1,c2 = tuple(rng.sample(eligible_list, 2, counts=elo))
    if c1.id == c2.id:
        c1,c2 = fetch_pokemon_pair()
    return c1, c2
    

left_pokemon, right_pokemon = fetch_pokemon_pair()
l_rate_decay = 0.95
l_rate_min = 50
elo_min = 100

def choose(p1: Pokemon, p2: Pokemon, score):
    id_w = id_to_index[p1.id]
    id_l = id_to_index[p2.id]
    
    elo_w = elo[id_w]
    elo_l = elo[id_l]
    k_w = l_rate[id_w]
    k_l = l_rate[id_l]
    q_w = math.pow(10, elo_w/400)
    q_l = math.pow(10, elo_l/400)
    
    expected_score = q_w/(q_w + q_l)
    delta_w = k_w * (score - expected_score)
    delta_l = k_l * (expected_score - score)

    elo[id_w] = max(elo_min, elo_w + int(delta_w))
    elo[id_l] = max(elo_min, elo_l + int(delta_l))
    l_rate[id_w] = max(l_rate_min, int(k_w * l_rate_decay))
    l_rate[id_l] = max(l_rate_min, int(k_l * l_rate_decay))
    save(SAVEFILE)

    global left_pokemon
    global right_pokemon
    left_pokemon, right_pokemon = fetch_pokemon_pair()    

def choose_left():
    choose(left_pokemon, right_pokemon)

def choose_right():
    choose(right_pokemon, left_pokemon)

def show_stats():
    tagged_scores = [(score, p.name) for score, p in zip(elo, eligible_list)]
    print(sorted(tagged_scores, reverse=True))

font = pygame.font.Font('fonts/rubik/static/Rubik-Regular.ttf', 32)

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

while (status):
    # iterate over the list of Event objects
    # that was returned by pygame.event.get() method.
    scrn.fill((0,0,0))
 
    for i in pygame.event.get():
 
        # if event object type is QUIT
        # then quitting the pygame
        # and program both.
        if i.type == pygame.QUIT:
            status = False
        if i.type == pygame.KEYDOWN:
            for k, s in scores.items():
                if i.key == k:
                    choose(left_pokemon, right_pokemon, 1 - s)
            if i.key == pygame.K_s:
                show_stats()

    for left, pokemon in [(IMG_MARGIN, left_pokemon), (3 * IMG_MARGIN + IMG_SIZE, right_pokemon)]:
        # create a surface object, image is drawn on it.
        img  = pygame.image.load(pokemon.image).convert()
        img  = pygame.transform.scale(img , (IMG_SIZE, IMG_SIZE))
 
        # Using blit to copy content from one surface to other
        scrn.blit(img, (left, IMG_MARGIN), img.get_rect())

        name = font.render(pokemon.name, True, (255,255,255))
        elo_text  = font.render(str(elo[id_to_index[pokemon.id]]), True, (255,255,255))

        scrn.blit(name, (left, IMG_MARGIN * 2 + IMG_SIZE))
        scrn.blit(elo_text, (left, IMG_MARGIN * 3 + IMG_SIZE))

    pygame.display.update()

    
 
# deactivates the pygame library
pygame.quit()