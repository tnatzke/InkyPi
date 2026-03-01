#!/usr/bin/env python3

import os
import pygame
import time

os.environ['DISPLAY'] = ':0.0'

# Set the SDL video driver to use the framebuffer
os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
os.environ["SDL_VIDEO_DISPLAY"] = "0"

pygame.init()
pygame.display.init()
pygame.mouse.set_visible(False)

# Get screen dimensions and create a fullscreen surface
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

# Load and display the image
image = pygame.image.load("/tmp/tmpus9kbwmy.png")
image = pygame.transform.scale(image, size) # Scale to fit screen
screen.blit(image, (0, 0))
pygame.display.update()

# Keep displayed for 10 seconds
time.sleep(10)
pygame.quit()
