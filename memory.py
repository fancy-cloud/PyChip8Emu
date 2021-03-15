class Memory:
	def __init__(self):
		self._MAX_MEM = 0x1000
		self.mem =[0] * self._MAX_MEM

	def __setitem__(self, addr: int, value: int):
		self.mem[addr] = value

	def __getitem__(self, addr: int):
		return self.mem[addr]