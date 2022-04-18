from collections import OrderedDict
import random, sys
from memcache_app.total_size import total_size

class Memcache:
	
	def __init__(self, capacity=100, rpolicy=1):
		self.cache = OrderedDict()
		self.capacity = 1024 * 1024 * capacity
		self.rpolicy = rpolicy 
		self.hit = 0
		self.miss = 0

	def get(self, key: str):
		if key not in self.cache:
			self.miss += 1
			return -1
		else:
			self.cache.move_to_end(key)
			self.hit += 1
			return self.cache[key]

	def put(self, key: str, value) -> None:
		if key in self.cache:
			del self.cache[key]
		ret = self.replacement(self.capacity - sys.getsizeof(value))
		if not ret:
			return False
		self.cache[key] = value
		self.cache.move_to_end(key)
		return True
	
	def replacement(self, threshold) -> None:
		if threshold < 400: # need more space
			return False
		if self.rpolicy:
			self.lru_replacement(threshold)
		else:
			self.random_replacement(threshold)
		return True # replace successfully	

	def lru_replacement(self, threshold) -> None:
		while self.total_size() > threshold:
			self.cache.popitem(last=False)
	
	def random_replacement(self, threshold) -> None:
		while self.total_size() > threshold:
			random_key = random.choice(list(self.cache.keys()))
			del self.cache[random_key]
    
	def config(self, capacity=None, rpolicy=None) -> tuple:
		if capacity != None:
			self.capacity = 1024 * 1024 * capacity 
		if rpolicy != None:
			self.rpolicy = rpolicy
		self.replacement(self.capacity)
		return (self.capacity, self.rpolicy)
	
	def num(self) -> int:
		return len(self.cache)
	
	def keys(self) -> list:
		return list(self.cache.keys())
	
	def statistics(self) -> tuple:
		num = self.num()
		sz = self.total_size()
		requests = self.hit + self.miss
		hit_rate = 100.0 * self.hit / requests if requests else .0
		miss_rate = 100.0 * self.miss / requests if requests else .0
		return (num, sz, requests, hit_rate, miss_rate)
	
	def invalidate(self, key) -> None:
		if key in self.cache:
			del self.cache[key]
	
	def total_size(self):
		return total_size(self.cache)
	
	def clear(self) -> None:
		self.cache.clear()
