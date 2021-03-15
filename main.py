from memory import Memory
from cpu import CPU
import pygame
import time
import os

def get_rom_data() -> bytes:
	completed = False
	while not completed:
		rom_name = input("Enter a ROM name (WITHOUT EXTENSION): ")
		path_to_rom = os.getcwd() + '/roms/' + rom_name + '.ch8'
		try:
			with open(path_to_rom, 'rb') as rom_file:
				rom_data = rom_file.read()
			pygame.display.set_caption(rom_name)
			return rom_data
		except FileNotFoundError:
			pass

def main():
	#pygame.init()
	#canvas = pygame.display.set_mode(512, 256)
	#canvas.fill(0x000000)
	#pygame.display.update()

	rom_data = get_rom_data()

	mem = Memory()
	cpu = CPU(mem)
	cpu.load_rom(rom_data)

	cycles = 0

	while True:
		cpu.cycle()
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				if event.key in cpu.k_map:
					chip_key = cpu.k_map[event.key]
					if event.type == pygame.KEYDOWN:
						cpu.keys_pressed[chip_key] = 1
					elif event.type == pygame.KEYUP:
						cpu.keys_pressed[chip_key] = 0
			elif event.type == pygame.QUIT:
				quit()

		if cpu.update_screen_flag == 1:
			pygame.display.update()
			cpu.update_screen_flag = 0

		cycles += 1

		if cycles == 10:
			time.sleep(1/1000)
			cycles = 0

if __name__ == '__main__':
	main()