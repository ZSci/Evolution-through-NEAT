import pygame
import time
import sys
import pickle
import random as rd

from constants     import *
from food          import *
from organism      import *
from math 		   import *
from pygame.locals import *

def spawn(food_store):
	if rd.random() > 0.9 and Food.count < MAX_FOOD:
		food_store.append(Food(get_time()))


def dist(c1, c2):
	return sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2)

def checkCollision(organism, food):
	##distance between centres < sum of radii =>    collision
	##distance between centres > sum of radii => no collision
	if not (organism.dead or food.dead):
		if dist(organism, food) <= organism.size + 0.2*food.size:
				return True
	return False

def age_up(population, in_time):
	for organism in population:
		if (in_time - organism.initTime) > (organism.age * AGE_UP):
			organism.bday()

def get_time():
	return(time.clock() - lag_compensator)


pygame.init()
DISP = pygame.display.set_mode((ARENA_WIDTH, ARENA_HEIGHT))
pygame.display.set_caption("Best Life")

population  = list()
food_store  = list()

with open('pop_1.pickle', 'rb') as f:
	population = pickle.load(f)

last_age = time.clock()
lag_compensator = 0
# player = Organism(0.01)

population = [Organism(get_time(), org.model.get_weights()) for org in population]

while True:

	pygame.time.delay(10)
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

	spawn(food_store)

	##Find the nearest food source - ideally removed later on
	for organism in population:
		organism.reset_f_dist()
		for food in  food_store:
			if dist(organism, food) < abs(organism.f_dist):
				organism.f_dist = dist(organism, food)
				organism.f_near = (food.x, food.y)

	##Random movement to be replace by neural net of each org
	for organism in population:
		organism.think()

	##Draw organism and food
	DISP.fill((0, 0, 0))
	if len(population):
		pygame.draw.circle(DISP, (255, 0, 0), (population[0].x, population[0].y),  population[0].size)
		pygame.draw.aaline(DISP, (127, 0, 127), (population[0].x, population[0].y), population[0].f_near)
	for organism in population[1:]:
		pygame.draw.circle(DISP, (0, 127, 127), (organism.x, organism.y), organism.size)
		pygame.draw.aaline(DISP, (127, 0, 127), (organism.x, organism.y), organism.f_near)
	for food in food_store:
		pygame.draw.circle(DISP, (0, 0, 255), (food.x, food.y), int(0.2*food.size))

	##Collision of org with food
	# for organism in population+[player]:

	for organism in population:
		for food in food_store:
			if checkCollision(organism, food):
				organism.feed(food.size)
				food.consumed()

	##Starve organisms decay food
	for organism in population:
		print(organism.age)
		organism.starve(get_time())
	for food in food_store:
		food.decay(get_time())

	##Clean up dead
	population = [organism for organism in population if not organism.dead]
	food_store = [food     for food     in food_store if not food.dead]

	population.sort(key = lambda x: x.food, reverse = True)

	if len(population) is 0:
		break

	##Age up
	age_up(population, get_time())

	pygame.display.update()


