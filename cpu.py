import numpy as np
import random
import pygame
from memory import Memory

class CPU:
	def __init__(self, mem: Memory):
		#####################################
		#      V0 - VE: Data registers      #
		#           VF: Flag register       #
		#####################################
		self._DATA_REGISTERS_AMOUNT = 0x10
		self.V = np.zeros(self._DATA_REGISTERS_AMOUNT, dtype='uint8')

		#####################################
		#          Address register         #
		#####################################
		self.I  = np.uint16(0x0)

		#####################################
		# Program Counter and Stack Pointer #
		#####################################
		self.PC = np.uint16(0x200)
		self.SP = np.uint16(0x0)

		#####################################
		#              Timers               #
		#####################################
		self.delay = np.uint8(60)
		self.sound = np.uint8(60)

		#####################################
		#         Memory and screen         #
		#####################################
		self.mem = mem
		self.stack = np.zeros(16, dtype='uint16')
		self._SCREEN_BEGIN_ADDR = 0xFF0
		self._SCREEN_END_ADDR = 0xFFF
		self._SCREEN_WIDTH = 64
		self._SCREEN_HEIGHT = 32
		self.screen = self.mem[self._SCREEN_BEGIN_ADDR]

		#####################################
		#           Keyboard map            #
		#####################################
		self.k_map = {
			pygame.K_x: 0x0,
			pygame.K_1: 0x1,
			pygame.K_2: 0x2,
			pygame.K_3: 0x3,
			pygame.K_q: 0x4,
			pygame.K_w: 0x5,
			pygame.K_e: 0x6,
			pygame.K_a: 0x7,
			pygame.K_s: 0x8,
			pygame.K_d: 0x9,
			pygame.K_z: 0xA,
			pygame.K_c: 0xB,
			pygame.K_4: 0xC,
			pygame.K_r: 0xD,
			pygame.K_f: 0xE,
			pygame.K_v: 0xF
		}

	def decrement_clocks(self):
		self.delay = self.delay - 1 if self.delay > 0 else 60
		self.sound = self.sound - 1 if self.sound > 0 else 60

	def load_rom(self, rom: bytes):
		start_address = 0x200
		i = 0
		for byte in rom:
			self.mem[start_address+i] = byte
			i += 1

	def fetch_instruction(self):
		ins = self.mem[self.PC]
		ins <<= 8
		ins |= self.mem[self.PC+1]
		self.PC += 2
		return ins

	def execute_instruction(self, ins: np.uint16):
		ins_type = ins & 0xF000
		if ins == 0x00E0:
			self.ins_cls()
		elif ins == 0x00EE:
			self.ins_ret()
		elif ins_type == 0x1000:
			addr = ins & 0x0FFF
			self.ins_jp(addr)
		elif ins_type == 0x2000:
			addr = ins & 0x0FFF
			self.ins_call(addr)
		elif ins_type == 0x3000:
			vx = (ins & 0x0F00) >> 8
			value = ins & 0x00FF
			self.ins_se(vx, value)
		elif ins_type == 0x4000:
			vx = (ins & 0x0F00) >> 8
			value = ins & 0x00FF
			self.ins_sne(vx, value)
		elif ins_type == 0x5000:
			vx = (ins & 0x0F00) >> 8
			vy = (ins & 0x00F0) >> 4
			self.ins_se_reg(vx, vy)
		elif ins_type == 0x6000:
			vx = (ins & 0x0F00) >> 8
			value = ins & 0x00FF
			self.ins_ld(vx, value)
		elif ins_type == 0x7000:
			vx = (ins & 0x0F00) >> 8
			value = ins & 0x00FF
			self.ins_add(vx, value)
		elif ins_type == 0x8000:
			ins_subtype = ins & 0x000F
			vx = (ins & 0x0F00) >> 8
			vy = (ins & 0x00F0) >> 4
			if ins_subtype == 0x0:
				self.ins_ld_reg(vx, vy)
			elif ins_subtype == 0x1:
				self.ins_or(vx, vy)
			elif ins_subtype == 0x2:
				self.ins_and(vx, vy)
			elif ins_subtype == 0x3:
				self.ins_xor(vx, vy)
			elif ins_subtype == 0x4:
				self.ins_add_carry(vx, vy)
			elif ins_subtype == 0x5:
				self.ins_sub_carry(vx, vy)
			elif ins_subtype == 0x6:
				self.ins_shr(vx, vy)
			elif ins_subtype == 0x7:
				self.ins_subn_carry(vx, vy)
			elif ins_subtype == 0x8:
				self.ins_shl(vx, vy)
		elif ins_type == 0x9000:
			vx = (ins & 0x0F00) >> 8
			vy = (ins & 0x00F0) >> 4
			self.ins_sne_reg(vx, vy)
		elif ins_type == 0xA000:
			addr = ins & 0x0FFF
			self.ins_ld_addr(addr)
		elif ins_type == 0xB000:
			addr = ins & 0x0FFF
			self.ins_jp_addr(addr)
		elif ins_type == 0xC000:
			vx = (ins & 0x0F00) >> 8
			value = ins & 0x00FF
			self.ins_rnd(vx, value)
		elif ins_type == 0xD000:
			vx = (ins & 0x0F00) >> 8
			vy = (ins & 0x00F0) >> 4
			n = ins & 0x000F
			self.drw(vx, vy, n)
		elif ins_type == 0xE000:
			ins_subtype = ins & 0x00FF
			vx = (ins & 0x0F00) >> 8
			if ins_subtype == 0x00A1:
				self.ins_sknp(vx)
			elif ins_subtype == 0x009E:
				self.ins_skp(vx)
		elif ins_type == 0xF000:
			ins_subtype = ins & 0x00FF
			vx = (ins & 0x0F00) >> 8
			if ins_subtype == 0x0007:
				self.ins_ld_delay(vx)
			if ins_subtype == 0x000A:
				self.ins_ld_key(vx)
			if ins_subtype == 0x0015:
				self.ins_ld_delay_to_reg(vx)
			if ins_subtype == 0x0018:
				self.ins_ld_sound(vx)
			if ins_subtype == 0x001E:
				self.ins_add_addr(vx)
			if ins_subtype == 0x0029:
				self.ins_ld_sprite_loc(vx)
			if ins_subtype == 0x0033:
				self.ins_ld_bcd(vx)
			if ins_subtype == 0x0055:
				self.ins_ld_reg_dump(vx)
			if ins_subtype == 0x0065:
				self.ins_ld_reg_load(vx)
			
	#####################################
	#           Instructions            #
	#####################################
	def ins_cls(self):
		for addr in range(self._SCREEN_BEGIN_ADDR, self._SCREEN_END_ADDR+1):
			self.mem[addr] = 0x0

	def ins_ret(self):
		self.SP -= 1
		self.PC = self.stack[self.SP]

	def ins_jp(self, addr: np.uint16):
		self.PC = addr

	def ins_call(self, addr: np.uint16):
		self.stack[self.SP] = self.PC
		self.SP += 1
		self.PC = addr

	def ins_se(self, vx: np.uint8, value: np.uint8):
		if self.V[vx] == value:
			self.PC += 2

	def ins_sne(self, vx: np.uint8, value: np.uint8):
		if self.V[vx] != value:
			self.PC += 2

	def ins_se_reg(self, vx: np.uint8, vy: np.uint8):
		if self.V[vx] == self.V[vy]:
			self.PC += 2

	def ins_ld(self, vx: np.uint8, value: np.uint8):
		self.V[vx] = value

	def ins_add(self, vx: np.uint8, value: np.uint8):
		self.V[vx] += value

	def ins_ld_reg(self, vx: np.uint8, vy: np.uint8):
		self.V[vx] = self.V[vy]

	def ins_or(self, vx: np.uint8, vy: np.uint8):
		self.V[vx] |= self.V[vy]

	def ins_and(self, vx: np.uint8, vy: np.uint8):
		self.V[vx] &= self.V[vy]

	def ins_xor(self, vx: np.uint8, vy: np.uint8):
		self.V[vx] ^= self.V[vy]

	def ins_add_carry(self, vx: np.uint8, vy: np.uint8):
		if 0x100 - self.V[vx] < self.V[vy]:
			self.V[vx] = self.V[vy] - (0x100 - self.V[vx])
			self.V[0xF] = 0x1
		else:
			self.V[vx] += self.V[vy]
			self.V[0xF] = 0x0

	def ins_sub_carry(self, vx: np.uint8, vy: np.uint8):
		if self.V[vx] < self.V[vy]:
			self.V[vx] = 0x100 - (self.V[vy] - self.V[vx])
			self.V[0xF] = 0x1
		else:
			self.V[vx] -= self.V[vy]
			self.V[0xF] = 0x0

	def ins_shr(self, vx: np.uint8):
		self.V[0xF] = 0x1 if self.V[vx] & 0x1 == 0x1 else 0x0
		self.V[vx] >>= 1

	def ins_subn_carry(self, vx: np.uint8, vy: np.uint8):
		if self.V[vy] < self.V[vx]:
			self.V[vx] = 0x100 - (self.V[vx] - self.V[vy])
			self.V[0xF] = 0x1
		else:
			self.V[vx] = self.V[vy] - self.V[vx]
			self.V[0xF] = 0x0

	def ins_shl(self, vx: np.uint8):
		self.V[0xF] = 0x1 if self.V[vx] & 0x7F == 0x7F else 0x0
		self.V[vx] <<= 1

	def ins_sne_reg(self, vx: np.uint8, vy: np.uint8):
		if self.V[vx] != self.V[vy]:
			self.PC += 2

	def ins_ld_addr(self, addr: np.uint16):
		self.I = addr

	def ins_jp_addr(self, addr: np.uint16):
		self.PC = addr + self.V[0x0]

	def ins_rnd(self, vx: np.uint8, value: np.uint8):
		self.V[vx] = random.randint(0x0, 0xFF) & value

	def ins_drw(self, vx: np.uint8, vy: np.uint8, n: np.uint8):
		bits = 8
		for y in range(0, n):
			currY = (self.V[vy] + y) % self._SCREEN_HEIGHT
			data = self.mem[self.I + y]
			for x in range(0, bits):
				if data & (0x80 >> x) != 0:
					currX = (self.V[vx] + x) % self._SCREEN_WIDTH
					if self.mem[bits*y + x] == 1:
						self.V[0xF] = 1
					self.mem[bits*y + x] ^= 1

	def ins_skp(self, vx: np.uint8):
		keys_pressed = pygame.key.get_pressed()
		for real_key, chip_key in self.k_map.items():
			if chip_key == self.V[vx] and keys_pressed[real_key]:
				self.PC += 2
				break

	def ins_sknp(self, vx: np.uint8):
		keys_pressed = pygame.key.get_pressed()
		for real_key, chip_key in self.k_map.items():
			if chip_key == self.V[vx] and not keys_pressed[real_key]:
				self.PC += 2
				break

	def ins_ld_delay(self, vx: np.uint8):
		self.V[vx] = self.delay

	def ins_ld_key(self, vx: np.uint8):
		key_pressed = False
		while not key_pressed:
			keys_pressed = pygame.key.get_pressed()
			for real_key, chip_key in self.k_map.items():
				if keys_pressed[real_key]:
					self.V[vx] = chip_key
					key_pressed = True
					break

	def ins_ld_delay_to_reg(self, vx: np.uint8):
		self.delay = self.V[vx]

	def ins_ld_sound(self, vx: np.uint8):
		self.sound = self.V[vx]

	def ins_add_addr(self, vx: np.uint8):
		self.I += self.V[vx]

	def ins_ld_sprite_loc(self, vx: np.uint8):
		self.I = self.V[vx]

	def ins_ld_bcd(self, vx: np.uint8):
		self.mem[self.I] = self.V[vx] / 0x64
		self.mem[self.I + 1] = (self.V[vx] / 0xA) % 0xA
		self.mem[self.I + 2] = self.V[vx] % 0xA

	def ins_ld_reg_dump(self, vx: np.uint8):
		for reg_num in range(0x0, vx+1):
			self.mem[self.I + reg_num] = self.V[vx] 

	def ins_ld_reg_load(self, vx: np.uint8):
		for reg_num in range(0x0, vx+1):
			self.V[reg_num] = self.mem[self.I + reg_num]