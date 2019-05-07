import pygame
import time
import sys
import random as rd

from constants     import *
from food          import *
from organism      import *
from math 		   import *
from pygame.locals import *


def spawn(population, food_store, dead_fridge):

	lc = get_time()

	if len(dead_fridge) >= GEN_LIMIT:

		global gen
		gen += 1
		print("Creating new Gen: {0}".format(gen))

		k = 0
		for i in range(int(GEN_LIMIT)):
			if population[k].food > dead_fridge[i].food:
				dead_fridge[i] = population[k]
				k+=1


		# population.clear()

		for i in range(int(GEN_LIMIT/2)):
			idx = rd.sample(range(int(GEN_LIMIT)), 2)
			child_brains = dead_fridge[idx[0]].procreate(dead_fridge[idx[1]])
			population.append(Organism(get_time(), child_brains[0]))
			population.append(Organism(get_time(), child_brains[1]))

		for dead_org in dead_fridge[:5]:
			population.append(Organism(get_time(), dead_org.model.get_weights()))

		dead_fridge.clear()
		global hold
		hold = 0

	if rd.random() > 0.98 and Organism.count < MAX_ORGS:
		population.append(Organism(get_time()))
	if rd.random() > 0.9 and Food.count < MAX_FOOD:
		food_store.append(Food(get_time()))

	global lag_compensator
	lag_compensator += get_time() - lc

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
pygame.display.set_caption("Life")

dead_fridge = list()
population  = list()
food_store  = list()

last_age = time.clock()
lag_compensator = 0
gen = 0
# player = Organism(0.01)
hold = 0

t1 = get_time()

while True:

	pygame.time.delay(10)
	for event in pygame.event.get():

		if event.type == QUIT:
			pygame.quit()
			sys.exit()

	##Spawn new organisms and food
	spawn(population, food_store, dead_fridge)

	##Find the nearest food source - ideally removed later on
	t1 = get_time()
	for organism in population:
		organism.reset_f_dist()
		for food in  food_store:
			if dist(organism, food) < abs(organism.f_dist):
				organism.f_dist = dist(organism, food)
				organism.f_near = (food.x, food.y)
	if(get_time() - t1 > 1):
		print("f_dist, f_near updates")

	##Random movement to be replace by neural net of each org
	t1 = get_time()
	for organism in population:
		organism.think()
	if(get_time() - t1 > 1):
		print("thinking")
		# if rd.random() > 0.98:
		# 	organism.move(rd.choice(MOTIONS))
		# else:
		# 	organism.move()
		# organism.move('N')

	###################################
	# Player Controls
	keys = pygame.key.get_pressed()
	if keys[pygame.K_DELETE]:
		pygame.quit()
		sys.exit()

	# if keys[pygame.K_LEFT]:
	# 	player.move('W')

	# if keys[pygame.K_RIGHT]:
	# 	player.move('E')

	# if keys[pygame.K_UP]:
	# 	player.move('N')

	# if keys[pygame.K_DOWN]:
	# 	player.move('S')
	###################################

	##Draw organism and food

	t1 = get_time()
	DISP.fill((0, 0, 0))
	for organism in population[1:]:
		pygame.draw.circle(DISP, (0, 127, 127), (organism.x, organism.y), organism.size)
		pygame.draw.aaline(DISP, (127, 0, 127), (organism.x, organism.y), organism.f_near)
	if len(population):
		pygame.draw.circle(DISP, (255, 0, 0), (population[0].x, population[0].y),  population[0].size)
		pygame.draw.aaline(DISP, (127, 0, 127), (population[0].x, population[0].y), population[0].f_near)
	for food in food_store:
		pygame.draw.circle(DISP, (0, 0, 255), (food.x, food.y), int(0.2*food.size))
	# pygame.draw.circle(DISP, (255, 255, 0), (player.x, player.y), 4)
	if(get_time() - t1 > 1):
		print("drawing")


	##Collision of org with food
	# for organism in population+[player]:

	t1 = get_time()
	for organism in population:
		for food in food_store:
			if checkCollision(organism, food):
				organism.feed(food.size)
				food.consumed()
	if(get_time() - t1 > 1):
		print("eating")

	##Starve organisms decay food
	t1 = get_time()
	for organism in population:
		organism.starve(get_time())
	for food in food_store:
		food.decay(get_time())
	if(get_time() - t1 > 1):
		print("deacy n death")

	##Age up
	t1 = get_time()
	age_up(population, get_time())
	if(get_time() - t1 > 1):
		print("thinking")

	##Clean up dead
	t1 = get_time()
	dead_fridge.extend([organism for organism in population if organism.dead and organism.food])
	population = [organism for organism in population if not organism.dead]
	food_store = [food     for food     in food_store if not food.dead]

	dead_fridge.sort(key = lambda x: x.food, reverse = True)
	population .sort(key = lambda x: x.food, reverse = True)

	if len(dead_fridge) > hold:
		hold = len(dead_fridge)
		print(len(dead_fridge))
	if(get_time() - t1 > 1):
		print("clean up")


	t1 = get_time()
	pygame.display.update()
	if(get_time() - t1 > 1):
		print("update")


