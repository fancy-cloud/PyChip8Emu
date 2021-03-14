import numpy as np

class Memory:
	def __init__(self):
		self._MAX_MEM = 0x1000
		self.mem = np.zeros(self._MAX_MEM, dtype='uint8')

	def __setitem__(self, addr: np.uint16, value: np.uint8):
		self.mem[addr] = value

	def __getitem__(self, addr: np.uint16):
		return self.mem[addr]