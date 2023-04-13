import pygame
import math
import numpy as np
from scipy.integrate import ode
from random import randint

# set up the colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 0)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)

g = -9.81

# Returns a list of evenly spaced values from start to end
# Does not include a value at end
def evenly_space(start, end, n):
    step = (end-start)/float(n)
    return [(int(round(x*step)) + start) for x in range(n)]

def to_screen(x, y, win_width, win_height):
    return win_width//2 + x, win_height//2 - y

def from_screen(x, y, win_width, win_height):
    return x - win_width//2, win_height//2 - y

# Class that represents a single joint in the blades
# Created as a square sprite for debug purposes
class BladeNode(pygame.sprite.Sprite):
    def __init__(self, color, length, base_angle, angle, base_x, base_y, previous_node):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([5, 5], flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.color = (0, color, 0, 255)
        self.time = 0
        self.dt = 0.033

        self.prev = previous_node # will be None if it is a node resting on the x-axis
        self.base_x = base_x
        self.base_y = base_y

        self.mass = 1
        self.length = length
        self.base_angle = base_angle #resting angle

        # Waits to be set based on initialized angle value
        self.angle = None
        self.pos = [None, None]
        self.set_angle(math.radians(angle))

        self.w = 0
        self.polar = [self.angle, self.w] #Not actual polar coordinates, sets up more like 1D coordinate system

        self.solver = ode(self.f)
        self.solver.set_integrator('dopri5')

        if self.prev is not None:
            self.solver.set_initial_value(self.polar, self.time)

        pygame.draw.rect(self.image, self.color, self.rect)

    def update(self, circles):
        # For the point on the x axis - does not move
        if self.prev is None:
            pass

        # For the points that can move
        else:
            self.solver.set_f_params(circles)
            self.step()

    def f(self, t, polar, circles):
        w = polar[1]

        c = 7.5
        k = 1
        F_spring = -1 * k * (math.degrees(polar[0]) - self.base_angle) - c * polar[1]
        a_gravity = g * math.cos(polar[0])
        
        Force_Angular_Total = F_spring
        a_Angular_Total = a_gravity

        for wind in circles:
            if self.within_circle(wind[0], wind[1], self.pos[0], self.pos[1], wind[2]):
                Force_Angular_Total -= wind[3] * math.sin(polar[0])
            
        a = a_Angular_Total + Force_Angular_Total/self.mass

        return [w, a]
    
    def step(self):
        if self.solver.successful():
            self.solver.integrate(self.time)

            self.polar = np.asarray(self.solver.y)
            self.set_angle(self.polar[0])

    # Sets the position of the sprite for debugging
    def set_pos(self, pos):
        self.rect.x = pos[0] - self.rect.width//2
        self.rect.y = pos[1] - self.rect.height//2

    def set_time(self, time):
        self.time = time

    def set_dt(self, dt):
        self.dt = dt

    # Sets the angle and the position of the node based on the angle inputted
    def set_angle(self, radians):
        if self.prev is not None:
            self.angle = radians # nodes lying on x axis do not have angles
            base_coord = self.prev.pos
        else:
            base_coord = [self.base_x, self.base_y]

        self.pos[0] = base_coord[0] + self.length * math.cos(radians)
        self.pos[1] = base_coord[1] + self.length * math.sin(radians)

    # Checks if point lies within a circle, used for checking if a node is being affected
    # by wind
    def within_circle(self, wind_x, wind_y, pos_x, pos_y, radius):
        dx = abs(pos_x - wind_x)
        dy = abs(pos_y - wind_y)

        if dx > radius:
            return False
        elif dy > radius:
            return False
        elif dx + dy <= radius:
            return True
        elif dx**2 + dy**2 <= radius**2:
            return True 
        
        return False

# Class that contains a certain amount of nodes for each blade
class Blade:
    def __init__(self, height, base_x, base_y, amount_joints):
        self.height = height
        self.base_x = base_x
        self.base_y = base_y
        
        self.color = 200 + randint(-50, 50)

        self.time = None
        self.dt = None

        #Temporary variable that stores the location of the node below it
        self.previous_node = None

        self.nodes = []
        self.node_loc = self.generate_nodes(amount_joints)

    def generate_nodes(self, amount_joints):
        # Length of first node is 0, then uses an equal length for the rest of the nodes
        update_length = 0
        length = (self.height-self.base_y)/float(amount_joints)

        # The bottom nodes are darker, and get lighter as it gets taller, simulating light
        color_mod = -80
        color_step = (-1 * color_mod)/(amount_joints - 1)

        # Begins the simulation at an odd angle to show how it simulates
        start_angle = 45 
        base_angle = 90

        r_values = []
        for i in range(amount_joints):

            if i > 0:
                update_length = length
                base_angle = base_angle + randint(-5, 5)

            # Will add None as the previous node for the base node
            newnode = BladeNode((self.color + color_mod), update_length, base_angle, start_angle, self.base_x, self.base_y, self.previous_node)
            self.nodes.append(newnode)
            self.previous_node = newnode

            color_mod = color_mod + color_step

            r_values.append(update_length)

        self.previous_node = None
        return r_values

    def set_time(self, time):
        self.time = time
        for node in self.nodes:
            node.set_time(time)

    def set_dt(self, dt):
        self.dt = dt
        for node in self.nodes:
            node.set_dt(dt)

class Grass:
    def __init__(self, left_x, right_x, num_blades, amount_joints):

        self.left_x = left_x
        self.right_x = right_x
        self.num_blades = num_blades

        self.blades = []
        self.blade_loc = self.generate_blades(left_x, right_x, num_blades, amount_joints)

        self.time = None
        self.dt = None

    def generate_blades(self, left_x, right_x, num_blades, amount_joints):
        x_values = evenly_space(left_x, right_x, num_blades)
        points = [[x, 0] for x in x_values]

        for point in points:
            self.blades.append(Blade((50 + randint(-25, 25)), point[0], point[1], amount_joints))

        return points
    
    def set_time(self, time):
        self.time = time
        for blade in self.blades:
            blade.set_time(time)
            
    def set_dt(self, dt):
        self.dt = dt
        for blade in self.blades:
            blade.set_dt(dt)

# Used for decoration
class Rectangle(pygame.sprite.Sprite):
    def __init__(self, color, width, height, object="Square"):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height], flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.object = object

        if (self.object == "Circle"):
            cx = self.rect.centerx
            cy = self.rect.centery
            pygame.draw.circle(self.image, color, (width/2, height/2), cx, cy)
        elif (self.object == "Square"):
            pygame.draw.rect(self.image, color, self.rect)
        else:
            print("Either ['Square'] or ['Circle'] must be chosen as objects.")
        
    def set_pos(self, pos):
        self.rect.x = pos[0] - self.rect.width//2
        self.rect.y = pos[1] - self.rect.height//2

class MyText():
    def __init__(self, color, background=WHITE, antialias=True, fontname="comicsansms", fontsize=16):
        pygame.font.init()
        self.font = pygame.font.SysFont(fontname, fontsize)
        self.color = color
        self.background = background
        self.antialias = antialias
    
    def draw(self, str1, screen, pos):
        text = self.font.render(str1, self.antialias, self.color, self.background)
        screen.blit(text, pos)