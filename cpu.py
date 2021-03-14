import numpy as np
import random
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
		self.SP = np.uint16(0xFA0)

		#####################################
		#              Timers               #
		#####################################
		self.delay = np.uint8(0x0)
		self.sound = np.uint8(0x0)

		#####################################
		#              Memory               #
		#####################################
		self.mem = mem

		#####################################
		#          Instruction set          #
		#####################################
		self._opcodes = {
			0x0: {
				0xE0: self.ins_cls,
				0xEE: self.ins_ret
			},
			0x1: self.ins_jp,
			0x2: self.ins_call,
			0x3: self.ins_se,
			0x4: self.ins_sne,
			0x5: self.ins_se_reg,
			0x6: self.ins_ld
			0x7: self.ins_add,
			0x8: {
				0x0: self.ins_ld_reg,
				0x1: self.ins_or,
				0x2: self.ins_and,
				0x3: self.ins_xor,
				0x4: self.ins_add_carry,
				0x5: self.ins_sub_carry,
				0x6: self.ins_shr,
				0x7: self.ins_subn_carry,
				0x8: self.ins_shl
			},
			0x9: self.ins_sne_reg,
			0xA: self.ins_ld_addr,
			0xB: self.ins_jp_addr,
			0xC: self.ins_rnd,
			0xD: self.ins_drw,
			0xE: {
				0x1: self.ins_skp
				0xE: self.ins_sknp,
			},
			0XF: {
				0x07: self.ins_ld_delay,
				0x0A: self.ins_ld_key,
				0x15: self.ins_ld_delay_to_reg,
				0x18: self.ins_ld_sound,
				0x1E: self.ins_add_addr,
				0x29: self.ins_ld_sprite_loc,
				0x33: self.ins_ld_bcd,
				0x55: self.ins_ld_reg_dump,
				0x65: self.ins_ld_reg_load
			}
		}


		#####################################
		#           Instructions            #
		#####################################
		def ins_cls():
			pass

		def ins_ret():
			self.PC = self.mem[self.SP]
			self.SP -= 1

		def ins_jp(addr: np.uint16):
			self.PC = addr

		def ins_call(addr: np.uint16):
			self.SP += 1
			self.mem[self.SP] = self.PC
			self.PC = addr

		def ins_se(vx: np.uint8, value: np.uint8):
			if self.V[vx] == value:
				self.PC += 2

		def ins_sne(vx: np.uint8, value: np.uint8):
			if self.V[vx] != value:
				self.PC += 2

		def ins_se_reg(vx: np.uint8, vy: np.uint8):
			if self.V[vx] == self.V[vy]:
				self.PC += 2

		def ins_ld(vx: np.uint8, value: np.uint8):
			self.V[vx] = value

		def ins_add(vx: np.uint8, value: np.uint8):
			self.V[vx] += value

		def ins_ld_reg(vx: np.uint8, vy: np.uint8):
			self.V[vx] = self.V[vy]

		def ins_or(vx: np.uint8, vy: np.uint8):
			self.V[vx] |= self.V[vy]

		def ins_and(vx: np.uint8, vy: np.uint8):
			self.V[vx] &= self.V[vy]

		def ins_xor(vx: np.uint8, vy: np.uint8):
			self.V[vx] ^= self.V[vy]

		def ins_add_carry(vx: np.uint8, vy: np.uint8):
			if 0x100 - self.V[vx] < self.V[vy]:
				self.V[vx] = self.V[vy] - (0x100 - self.V[vx])
				self.V[0xF] = 0x1
			else:
				self.V[vx] += self.V[vy]
				self.V[0xF] = 0x0

		def ins_sub_carry(vx: np.uint8, vy: np.uint8):
			if self.V[vx] < self.V[vy]:
				self.V[vx] = 0x100 - (self.V[vy] - self.V[vx])
				self.V[0xF] = 0x1
			else:
				self.V[vx] -= self.V[vy]
				self.V[0xF] = 0x0

		def ins_shr(vx: np.uint8):
			self.V[0xF] = 0x1 if self.V[vx] & 0x1 == 0x1 else 0x0
			self.V[vx] >>= 1

		def ins_subn_carry(vx: np.uint8, vy: np.uint8):
			if self.V[vy] < self.V[vx]:
				self.V[vx] = 0x100 - (self.V[vx] - self.V[vy])
				self.V[0xF] = 0x1
			else:
				self.V[vx] = self.V[vy] - self.V[vx]
				self.V[0xF] = 0x0

		def ins_shl(vx: np.uint8):
			self.V[0xF] = 0x1 if self.V[vx] & 0x7F == 0x7F else 0x0
			self.V[vx] <<= 1

		def ins_sne_reg(vx: np.uint8, vy: np.uint8):
			if self.V[vx] != self.V[vy]:
				self.PC += 2

		def ins_ld_addr(addr: np.uint16):
			self.I = addr

		def ins_jp_addr(addr: np.uint16):
			self.PC = addr + self.V[0x0]

		def ins_rnd(vx: np.uint8, value: np.uint8):
			self.V[vx] = random.randint(0x0, 0xFF) & value

		def ins_drw():

		def ins_skp(vx: np.uint8):
			# pseudo-code
			if key[vx] is pressed:
				self.PC += 2

		def ins_sknp():
			# pseudo-code
			if key[vx] is not pressed:
				self.PC += 2

		def ins_ld_delay(vx: np.uint8):
			self.V[vx] = self.delay

		def ins_ld_key(vx: np.uint8, key: np.uint8):
			self.V[vx] = key

		def ins_ld_delay_to_reg(vx: np.uint8):
			self.delay = self.V[vx]

		def ins_ld_sound(vx: np.uint8):
			self.sound = self.V[vx]

		def ins_add_addr(vx: np.uint8):
			self.I += self.V[vx]

		def ins_ld_sprite_loc(vx: np.uint8):
			self.I = self.V[vx]

		def ins_ld_bcd():
			pass

		def ins_ld_reg_dump(vx: np.uint8):
			for reg_num in range(0x0, vx+1):
				self.mem[self.I + reg_num] = self.V[vx] 

		def ins_ld_reg_load(vx: np.uint8):
			for reg_num in range(0x0, vx+1):
				self.V[reg_num] = self.mem[self.I + reg_num]