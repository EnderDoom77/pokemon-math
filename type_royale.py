# importing required library
from collections import defaultdict
from random import Random
import pygame

from pokemon import Pokemon, read_pokemon
 
# activate the pygame library .
pygame.init()
X = 600
Y = 600
 
# create the display surface object
# of specific dimension..e(X, Y).
scrn = pygame.display.set_mode((X, Y))
 
# set the pygame window name
pygame.display.set_caption('image')
 
# create a surface object, image is drawn on it.
imp = pygame.image.load("C:\\Users\\DELL\\Downloads\\gfg.png").convert()
 
# Using blit to copy content from one surface to other
scrn.blit(imp, (0, 0))

weights = defaultdict(float)

pokemon_list = read_pokemon()
eligible_list = [p for p in pokemon_list if p.image]

rng = Random()

def fetch_pokemon_pair() -> tuple[Pokemon, Pokemon]:
    return rng.sample()

left_pokemon = None
right_pokemon = None

def choose_left():
    pass

def choose_right():
    pass

def show_stats():
    pass

# paint screen one time
pygame.display.flip()
status = True
while (status):
 
  # iterate over the list of Event objects
  # that was returned by pygame.event.get() method.
    for i in pygame.event.get():
 
        # if event object type is QUIT
        # then quitting the pygame
        # and program both.
        if i.type == pygame.QUIT:
            status = False
        if i.type == pygame.KEYDOWN:
            match i.key:
                case pygame.K_a | pygame.K_LEFT:
                    choose_left()
                case pygame.K_d | pygame.K_RIGHT:
                    choose_right()
 
# deactivates the pygame library
pygame.quit()