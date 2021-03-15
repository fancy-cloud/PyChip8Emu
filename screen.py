import pygame
from cpu import CPU

class Screen:
	def __init__(self, screen_width, screen_height):
		self.canvas = pygame.display.set_mode((screen_width, screen_height))
		self.scale = 8

	def draw_frame(self, cpu: CPU):
		self.canvas.fill(0x000000)
		screen_pos = 0
		for y in range(cpu.SCREEN_HEIGHT):
			for x in range(cpu.SCREEN_WIDTH):
				if cpu.screen_mem[screen_pos] == 1:
					x_scale = x * self.scale
					y_scale = y * self.scale
					pygame.draw.rect(self.canvas, 0xFFFFFF, 
									(x_scale, y_scale, self.scale, self.scale), 0)
				screen_pos += 1
		cpu.update_screen_flag = 0