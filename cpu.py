import random
import pygame
import time
from memory import Memory

class CPU:
	def __init__(self, mem: Memory):
		#####################################
		#      V0 - VE: Data registers      #
		#           VF: Flag register       #
		#####################################
		self._DATA_REGISTERS_AMOUNT = 0x10
		self.V = [0] * self._DATA_REGISTERS_AMOUNT

		#####################################
		#          Address register         #
		#####################################
		self.I  = 0x0

		#####################################
		# Program Counter and Stack Pointer #
		#####################################
		self.PC = 0x200

		#####################################
		#              Timers               #
		#####################################
		self.delay = 0x0
		self.sound = 0x0
		self.cycle_start_time = 0
		self.cycle_end_time = 0

		#####################################
		#         Memory and screen         #
		#####################################
		self.mem = mem
		self.stack = []
		self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0, 
                        0x20, 0x60, 0x20, 0x20, 0x70, 
                        0xF0, 0x10, 0xF0, 0x80, 0xF0, 
                        0xF0, 0x10, 0xF0, 0x10, 0xF0, 
                        0x90, 0x90, 0xF0, 0x10, 0x10, 
                        0xF0, 0x80, 0xF0, 0x10, 0xF0,
                        0xF0, 0x80, 0xF0, 0x90, 0xF0, 
                        0xF0, 0x10, 0x20, 0x40, 0x40, 
                        0xF0, 0x90, 0xF0, 0x90, 0xF0, 
                        0xF0, 0x90, 0xF0, 0x10, 0xF0, 
                        0xF0, 0x90, 0xF0, 0x90, 0x90, 
                        0xE0, 0x90, 0xE0, 0x90, 0xE0, 
                        0xF0, 0x80, 0x80, 0x80, 0xF0, 
                        0xE0, 0x90, 0x90, 0x90, 0xE0,
                        0xF0, 0x80, 0xF0, 0x80, 0xF0, 
                        0xF0, 0x80, 0xF0, 0x80, 0x80]
		self.SCREEN_WIDTH = 512
		self.SCREEN_HEIGHT = 256
		self.CHIP_SCREEN_WIDTH = 64
		self.CHIP_SCREEN_HEIGHT = 32
		self.RESOLUTION_RATIO = 8
		self.update_screen_flag = 0
		self.screen = pygame.PixelArray(pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)))

		#####################################
		#               Sound               #
		#####################################
		pygame.mixer.init()
		self.BEEP_SOUND = pygame.mixer.Sound('sound/beep.wav')

		#####################################
		#             Keyboard              #
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
		self.keys_pressed = [0] * 16

	def load_rom(self, rom: bytes):
		for i in range(80):
			self.mem[i] = self.fontset[i]
		start_address = 0x200
		i = 0
		for byte in rom:
			self.mem[start_address+i] = byte
			i += 1

	def cycle(self):
		ins = self.fetch_instruction()
		self.execute_instruction(ins)

		self.cycle_end_time = time.time()

		if self.cycle_end_time - self.cycle_start_time >= 1/60:
			self.decrement_clocks()
			self.cycle_start_time = self.cycle_end_time


	def decrement_clocks(self):
		if self.delay > 0:
			self.delay -= 1
		if self.sound > 0:
			self.BEEP_SOUND.play()
			self.sound -= 1

	def fetch_instruction(self):
		ins = self.mem[self.PC]
		ins <<= 8
		ins |= self.mem[self.PC+1]
		self.PC += 2
		return ins

	def execute_instruction(self, ins: int):
		ins_type = ins & 0xF000
		vx = (ins & 0x0F00) >> 8
		vy = (ins & 0x00F0) >> 4
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
			value = ins & 0x00FF
			self.ins_se(vx, value)
		elif ins_type == 0x4000:
			value = ins & 0x00FF
			self.ins_sne(vx, value)
		elif ins_type == 0x5000:
			self.ins_se_reg(vx, vy)
		elif ins_type == 0x6000:
			value = ins & 0x00FF
			self.ins_ld(vx, value)
		elif ins_type == 0x7000:
			value = ins & 0x00FF
			self.ins_add(vx, value)
		elif ins_type == 0x8000:
			ins_subtype = ins & 0x000F
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
			elif ins_subtype == 0xE:
				self.ins_shl(vx, vy)
		elif ins_type == 0x9000:
			self.ins_sne_reg(vx, vy)
		elif ins_type == 0xA000:
			addr = ins & 0x0FFF
			self.ins_ld_addr(addr)
		elif ins_type == 0xB000:
			addr = ins & 0x0FFF
			self.ins_jp_addr(addr)
		elif ins_type == 0xC000:
			value = ins & 0x00FF
			self.ins_rnd(vx, value)
		elif ins_type == 0xD000:
			n = ins & 0x000F
			self.ins_drw(vx, vy, n)
		elif ins_type == 0xE000:
			ins_subtype = ins & 0x00FF
			if ins_subtype == 0x009E:
				self.ins_skp(vx)
			elif ins_subtype == 0x00A1:
				self.ins_sknp(vx)
		elif ins_type == 0xF000:
			ins_subtype = ins & 0x00FF
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
		for y in range(0, self.SCREEN_HEIGHT):
			for x in range(0, self.SCREEN_WIDTH):
				self.screen[x][y] = 0x000000
		self.update_screen_flag = 1

	def ins_ret(self):
		self.PC = self.stack.pop()

	def ins_jp(self, addr: int):
		self.PC = addr

	def ins_call(self, addr: int):
		self.stack.append(self.PC)
		self.PC = addr

	def ins_se(self, vx: int, value: int):
		if self.V[vx] == value:
			self.PC += 2

	def ins_sne(self, vx: int, value: int):
		if self.V[vx] != value:
			self.PC += 2

	def ins_se_reg(self, vx: int, vy: int):
		if self.V[vx] == self.V[vy]:
			self.PC += 2

	def ins_ld(self, vx: int, value: int):
		self.V[vx] = value

	def ins_add(self, vx: int, value: int):
		self.V[vx] += value
		self.V[vx] &= 0xFF

	def ins_ld_reg(self, vx: int, vy: int):
		self.V[vx] = self.V[vy]

	def ins_or(self, vx: int, vy: int):
		self.V[vx] |= self.V[vy]

	def ins_and(self, vx: int, vy: int):
		self.V[vx] &= self.V[vy]

	def ins_xor(self, vx: int, vy: int):
		self.V[vx] ^= self.V[vy]

	def ins_add_carry(self, vx: int, vy: int):
		self.V[vx] += self.V[vy]
		self.V[0xF] = 1 if self.V[vx] > 0xFF else 0
		self.V[vx] &= 0xFF

	def ins_sub_carry(self, vx: int, vy: int):
		if self.V[vx] < self.V[vy]:
			self.V[0xF] = 0x0
		else:
			self.V[0xF] = 0x1
		self.V[vx] -= self.V[vy]
		self.V[vx] &= 0xFF

	def ins_shr(self, vx: int, vy: int):
		if self.V[vy] == 1:
			self.V[0xF] = self.V[vy] & 0x1
			self.V[vx] = self.V[vy] >> 1
		else:
			self.V[0xF] = self.V[vx] & 0x1
			self.V[vx] = self.V[vx] >> 1

	def ins_subn_carry(self, vx: int, vy: int):
		if self.V[vy] < self.V[vx]:
			self.V[0xF] = 0x0
		else:
			self.V[0xF] = 0x1
		self.V[vx] = self.V[vy] - self.V[vx]
		self.V[vx] &= 0xFF

	def ins_shl(self, vx: int, vy: int):
		if self.V[vy] == 1:
			self.V[0xF] = self.V[vy] & 0x80
			self.V[vx] = self.V[vy] << 1
		else:
			self.V[0xF] = self.V[vx] & 0x80
			self.V[vx] = self.V[vx] << 1
		self.V[vx] &= 0xFF

	def ins_sne_reg(self, vx: int, vy: int):
		if self.V[vx] != self.V[vy]:
			self.PC += 2

	def ins_ld_addr(self, addr: int):
		self.I = addr

	def ins_jp_addr(self, addr: int):
		self.PC = addr + self.V[0x0]

	def ins_rnd(self, vx: int, value: int):
		self.V[vx] = random.randint(0x0, 0xFF) & value

	def ins_drw(self, vx: int, vy: int, n: int):
		self.V[0xF] = 0
		bits = 8
		for y in range(0, n):
			currY = (self.V[vy] + y) % self.CHIP_SCREEN_HEIGHT * self.RESOLUTION_RATIO
			data = self.mem[self.I + y]
			for x in range(0, bits):
				if data & (0x80 >> x) != 0:
					currX = (self.V[vx] + x) % self.CHIP_SCREEN_WIDTH * self.RESOLUTION_RATIO
					if self.screen[currX][currY] == 0xFFFFFF:
						self.V[0xF] = 1
					for y_offset in range(0, self.RESOLUTION_RATIO):
						for x_offset in range(0,self.RESOLUTION_RATIO):
							self.screen[currX+x_offset][currY+y_offset] ^= 0xFFFFFF
			self.update_screen_flag = 1

	def ins_skp(self, vx: int):
		key_code = self.V[vx]
		if self.keys_pressed[key_code] == 1:
			self.PC += 2

	def ins_sknp(self, vx: int):
		key_code = self.V[vx]
		if self.keys_pressed[key_code] == 0:
			self.PC += 2
		
	def ins_ld_delay(self, vx: int):
		self.V[vx] = self.delay

	def ins_ld_key(self, vx: int):
		self.PC -= 2
		for key_code, pressed in enumerate(self.keys_pressed):
			if pressed == 1:
				self.V[vx] = key_code
				self.PC += 2
				break

	def ins_ld_delay_to_reg(self, vx: int):
		self.delay = self.V[vx]

	def ins_ld_sound(self, vx: int):
		self.sound = self.V[vx]

	def ins_add_addr(self, vx: int):
		self.I += self.V[vx]

	def ins_ld_sprite_loc(self, vx: int):
		self.I = self.V[vx] * 5

	def ins_ld_bcd(self, vx: int):
		self.mem[self.I] = self.V[vx] // 100
		self.mem[self.I + 1] = (self.V[vx] % 100) // 10
		self.mem[self.I + 2] = (self.V[vx] % 100) % 10

	def ins_ld_reg_dump(self, vx: int):
		for reg_num in range(vx+1):
			self.mem[self.I + reg_num] = self.V[vx] 
		self.I += vx+1

	def ins_ld_reg_load(self, vx: int):
		for reg_num in range(vx+1):
			self.V[reg_num] = self.mem[self.I + reg_num]
			self.V[reg_num] &= 0xFF
		self.I += vx+1