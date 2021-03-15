from memory import Memory
from cpu import CPU
from screen import Screen
import pygame
import time
import os

def get_rom_data() -> bytes:
	completed = False
	while not completed:
		rom_name = input("Enter a ROM name: ")
		path_to_rom = os.getcwd() + '/roms/' + rom_name
		try:
			with open(path_to_rom, 'rb') as rom_file:
				rom_data = rom_file.read()
			pygame.display.set_caption(rom_name)
			return rom_data
		except FileNotFoundError:
			pass

def main():
	rom_data = get_rom_data()

	width, height = 512, 256
	screen = Screen(width, height)
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
			screen.draw_frame(cpu)
			pygame.display.update()

		cycles += 1

		if cycles == 10:
			time.sleep(10/1000)
			cycles = 0
			
if __name__ == '__main__':
	main()