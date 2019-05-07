
import random as rd
import numpy as np
import keras

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from math import exp
from constants import *


# Organisms
#	age - age
#
#	max_health - dependent on age as a parabloic + function
#	health - instantaneous health
#	hunger - hunger
#	strength - ability to attack other creatures ---FUTURE FEAT---
#
#		Age increases every 1 minute
#		
#		MaxHealth = -0.016*(age-50)^2 + 50 for age<100. age>100 => max = 10
#		MaxHunger = -0.008*(age-50)^2 + 30 for age<100. age>100 => max = 10
#
#		Health dependent on hunger and other attacks. If hunger < 50%, health -= decreases. 50%<=hunger<=70%, no effect. hunger>70%, health += 0.1*hunger
#		health = max_health * (1 - exp(-0.5 * hunger))
#		Hunger increases(numerically decreases) periodically. hunger = max_hunger * exp(-0.2 * time)
#		Strength determines attack strength of organism. ---FUTURE FEAT---


class Organism:

	count = 0

	def __init__(self, t, weights = None):

		self.age = 0

		self.max_health = 10
		self.max_hunger = 10

		self.health   = 10
		self.hunger   = 10
		self.food     = 0

		# self.strength = 10
		self.size = 3

		self.initTime = t
		self.time = t
		self.dead = False

		self.x = rd.randint(FRAME, ARENA_WIDTH - FRAME)
		self.y = rd.randint(FRAME, ARENA_HEIGHT - FRAME)

		self.f_dist = -ARENA_WIDTH
		self.f_near = (-1, -1)

		self.direction = rd.choice(MOTIONS)

		self.brain(weights)

		Organism.count += 1

	def __del__(self):
		if self.food:
			print("Born: {0}, Lifetime: {1}, Food: {2} , Age: {3}".format(round(self.initTime, 3), round(self.time - self.initTime, 3), self.food, self.age))
		Organism.count -= 1

	def bday(self):
		self.age += 1

		if self.age<=100:
			self.max_health = 50 - 0.016 * (self.age - 50) ** 2
			self.max_hunger = 30 - 0.008 * (self.age - 50) ** 2

	def starve(self, cur_time):
		self.hunger = self.max_hunger * exp(-0.2 * (cur_time - self.time - self.food))

		if self.hunger >= self.max_hunger:
			self.hunger = self.max_hunger

		self.health = self.max_health * (1 - exp(-0.5 * self.hunger))
		# print("Org {0}, health:{1}, age:{2}".format(self.initTime, self.health, self.age))

		if self.health <= 1:
			self.time = cur_time
			self.dead = True
			# print("Set to die, age:{0}, time:{1}, food:{2}".format(self.age,  self.time-self.initTime, self.food))

	def feed(self, refill):
		self.food += refill
		self.f_dist = -1
		# print("Organism ate {0}".format(refill))

	def reset_f_dist(self):
		self.f_dist = -ARENA_WIDTH

	def move(self, direction=None):
		# if direction is None:
		# 	direction = self.direction
		# else:
		# 	self.direction = direction

		direction = self.direction
		if 'N' in direction:
			self.y -= 1
		if 'S' in direction:
			self.y += 1
		if 'E' in direction:
			self.x += 1
		if 'W' in direction:
			self.x -= 1

		if self.x < FRAME:
			self.x = FRAME
		elif self.x > (ARENA_WIDTH - FRAME):
			self.x = (ARENA_WIDTH - FRAME)
		if self.y < FRAME:
			self.y = FRAME
		elif self.y > (ARENA_HEIGHT - FRAME):
			self.y = (ARENA_HEIGHT - FRAME)

	def brain(self, weights):
		self.model = Sequential()
		self.model.add(Dense(output_dim = 4, input_dim = 2))
		self.model.add(Activation("elu"))
		self.model.add(Dense(output_dim = 4))
		self.model.add(Activation('softmax'))
		# self.model.add(Dense(output_dim = 8))
		# self.model.add(Activation("sigmoid"))

		if weights is not None:
			self.model.set_weights(weights)

	def think(self):
		dx = self.f_near[0] - self.x
		dy = self.f_near[1] - self.y
		input_var = np.atleast_2d((dx, dy))
		out = np.argmax(self.model.predict(input_var))
		self.direction = MOTIONS[out]
		self.move()

	def procreate(self, organism = None):
		w1 = self.model.get_weights()
		w2 = organism.model.get_weights()

		w_child1 = w1
		w_child2 = w2

		w_child1[0] = w2[0]
		w_child2[0] = w1[0]

		for layer in range(len(w_child1)):
			for weight in range(len(w_child1[layer])):
				if rd.random() >= 0.9:
					w_child1[layer][weight] += rd.uniform(-0.2, 0.2)
					w_child2[layer][weight] += rd.uniform(-0.2, 0.2)

		return [w_child1, w_child2]


