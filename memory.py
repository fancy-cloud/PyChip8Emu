import numpy as np

class Memory:
	def __init__(self):
		self._MAX_MEM = 0x1000
		self.mem = np.zeros(self._MAX_MEM, dtype='uint8')