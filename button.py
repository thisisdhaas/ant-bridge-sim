import pygame
from pygame.locals import *

class Button:
	def __init__(self, text, x, y, width, height, action):
		self.text = text
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.action = action
		self.color = (75, 75, 75)
		self.borderColor = (255, 0, 0)
	
	def checkPressed(self, event):
		if event.type == MOUSEBUTTONDOWN:
			(mouseX, mouseY) = pygame.mouse.get_pos()
			if (mouseY >= self.y and mouseY <= self.y+self.height) and (mouseX >= self.x and mouseX <= self.x+self.width):
				self.action(self)

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)
		font = pygame.font.Font(None, 20)
		text = font.render((self.text), 1, (255, 255, 255))
		textpos = text.get_rect(centerx = self.x+self.width/2, centery = self.y+self.height/2)
		screen.blit(text, textpos)
		
		offset = 1
		pygame.draw.line(screen, self.borderColor, (self.x, self.y+offset), (self.x, self.y+offset+self.height))
		pygame.draw.line(screen, self.borderColor, (self.x, self.y+offset+self.height), (self.x+self.width, self.y+offset+self.height))
		pygame.draw.line(screen, self.borderColor, (self.x+self.width, self.y+offset+self.height), (self.x+self.width, self.y+offset))
		pygame.draw.line(screen, self.borderColor, (self.x+self.width, self.y+offset), (self.x, self.y+offset))