import numpy as np
import pygame

class Simulation:
    def __init__(self, title, sprites):
        self.paused = True # starting in paused mode
        self.title = title
        self.cur_time = 0
        self.dt = 0.033
        self.sprites = sprites

    def add_sprite(self, sprite):
        sprite.set_time(self.cur_time)
        self.sprites.add(sprite)

    def set_time(self, cur_time=0):
        self.cur_time = cur_time
        for sprite in self.sprites:
            sprite.set_time(cur_time)

    def set_dt(self, dt=0.033):
        self.dt = dt
        for sprite in self.sprites:
            sprite.set_dt(dt)

    # Calls each node to calculate their next position
    def step(self, circles):
        self.cur_time += self.dt
        for sprite in self.sprites:
            sprite.set_time(self.cur_time)
            sprite.update(circles)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False