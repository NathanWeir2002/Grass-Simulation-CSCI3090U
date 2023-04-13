import pygame, sys
import matplotlib.pyplot as plt
import numpy as np

import sim as Simulation
import util

win_width = 1000
win_height = 200

def main():
    title = 'Grass Simulation'

    pygame.init()
    clock = pygame.time.Clock()

    text = util.MyText(util.BLACK)

    grass_left = -200
    grass_right = 200
    amount_grass = 200  # a good amount is total length / 2
    grass_joints = 3    # 2 joints for no bend, anything over for more fluidity
    wind_power = 50     # a good amount is between 10 for low winds - 100 for very strong winds

    circles = []

    # Spawn location, height, radius, power
    wind1 = [grass_left - 50, 50, 40, wind_power]
    circles.append(wind1)

    # Depending on the total length of the grass, two wind sources may be used
    if abs(grass_left) + grass_right >= 400:
        wind2 = [0, 50, 40, wind_power]
        circles.append(wind2)
    

    # "Layers" of grass, adding more will slow down the program significantly
    top_layer = util.Grass(grass_left, grass_right, amount_grass, grass_joints)
    
    # Drawn rectangles for the x and y axis
    x_axis = util.Rectangle(color=util.BLACK, width=win_width-50, height=1, object="Square")
    y_axis = util.Rectangle(color=util.BLACK, width=1, height=win_height-50, object="Square") 
    
    axis = pygame.sprite.Group([x_axis, y_axis])

    # Holds all the joints - or BladeNodes - for the blades
    sprites = pygame.sprite.Group([])
    for blade in top_layer.blades:
        for node in blade.nodes:
            sprites.add(node)

    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption(title)

    # setting up simulation
    sim = Simulation.Simulation(title, sprites)

    sim.set_time(0.0)
    sim.set_dt(0.033)

    print ('--------------------------------')
    print ('Usage:')
    print ('Press (r) to start/resume simulation')
    print ('Press (p) to pause simulation')
    print ('Press (q) to quit')
    print ('--------------------------------')

    x_axis.set_pos(util.to_screen(0, 0, win_width, win_height))
    y_axis.set_pos(util.to_screen(0, 0, win_width, win_height))

    while True:
        clock.tick(30)

        # Update sprite location based on simulation
        for sprite in sprites:
            sprite.set_pos(util.to_screen(sprite.pos[0], sprite.pos[1], win_width, win_height))

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            sim.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sim.resume()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            break
        else:
            pass

        # Update simulation
        if not sim.paused:
            sim.step(circles) 

            # Moves the wind around the screen
            for wind in circles:
                wind[0] += 10
                if wind[0] >= grass_right + 50:
                    wind[0] = grass_left - 50
            pass
        else:
            pass

        # Clear the background
        screen.fill(util.WHITE)

        # Draws lines between each joint, creating the blades of grass
        for sprite in sprites:
            if sprite.prev is not None:
                spritepos = util.to_screen(sprite.pos[0], sprite.pos[1], win_width, win_height)
                prevpos = util.to_screen(sprite.prev.pos[0], sprite.prev.pos[1], win_width, win_height)
                pygame.draw.line(screen, sprite.color, spritepos, prevpos, width=2)

        # Uncomment for debug node locations
        """
        sprites.draw(screen) 
        """
        
        # Draws axis and text
        axis.draw(screen)
        text.draw("Time = %f" % sim.cur_time, screen, (10,10))

        # Uncomment for wind visualization
        """
        if showwind:
            for wind in circles:
                pygame.draw.circle(screen, [0, 0, 255, 255], 
                       util.to_screen(wind[0], wind[1], win_width, win_height),
                       wind[2])
        """

        pygame.display.flip()
    
    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()