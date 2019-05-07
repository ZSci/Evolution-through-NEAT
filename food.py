
import random as rd
import time
from constants import *

class Food:

	count = 0

	def __init__(self, t):

		# self.size = rd.randint(1, MAX_FOOD_SIZE)
		self.size = 12
		self.timeout = rd.randint(3, 5)

		self.initTime = t

		self.x = rd.randint(FRAME, ARENA_WIDTH - FRAME)
		self.y = rd.randint(FRAME, ARENA_HEIGHT - FRAME)

		self.dead = False

		Food.count += 1

	def __del__(self):
		Food.count -= 1

	def decay(self, cur_time):
		if self.timeout < cur_time - self.initTime:
			self.dead = True

	def consumed(self):
		self.dead = True

