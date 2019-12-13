__version__ = "$Id:$"
__docformat__ = "reStructuredText"

# Python imports
import random

# Library imports
import pygame
from pygame.key import *
from pygame.locals import *
from pygame.color import *

# pymunk imports
import pymunk
import pymunk.pygame_util
import pymunk.autogeometry
from pymunk import Vec2d

from ball import Ball
from table import Table

from constants import *


class PoolGame(object):
    """
    This class implements the setup for a game of pool.
    """

    def __init__(self):
        # Space
        self._space = pymunk.Space()
        self._space.gravity = (0.0, -981.0)

        # Physics
        # Time step
        self._dt = 1.0 / 60.0
        # Number of physics steps per screen frame
        self._physics_steps_per_frame = 1

        # pygame
        pygame.init()

        self._screen = pygame.display.set_mode((WINDOW_LENGTH, WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()

        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)

        # Static barrier walls (lines) that the balls bounce off of
        self._add_static_scenery()

        # Balls that exist in the world
        self._balls = []

        # Execution control and time until the next ball spawns
        self._running = True
        self._ticks_to_next_ball = 10

    def run(self):
        """
        The main loop of the game.
        :return: None
        """

        # Main loop
        while self._running:
            # Progress time forward
            for _ in range(self._physics_steps_per_frame):
                self._space.step(self._dt)
            self._process_events()
            self._update_balls()
            self._draw_objects()
            self._clear_screen()
            self._draw_balls()
            pygame.display.flip()
            # Delay fixed time between frames
            self._clock.tick(50)
            pygame.display.set_caption("fps: " + str(self._clock.get_fps()))

    def _add_static_scenery(self):
        """
        Create the static bodies.
        :return: None
        """
        space = self._space

        logo_img = pygame.image.load("table_outline.png")
        logo_bb = pymunk.BB(0, 0, logo_img.get_width(), logo_img.get_height())

        def sample_func(point):
            try:
                p = pymunk.pygame_util.to_pygame(point, logo_img)
                color = logo_img.get_at(p)

                return color.hsla[2]
            except:
                return 0

        line_set = pymunk.autogeometry.PolylineSet()

        def segment_func(v0, v1):
            line_set.collect_segment(v0, v1)

        logo_img.lock()
        pymunk.autogeometry.march_soft(
            logo_bb,
            logo_img.get_width(), logo_img.get_height(),
            99,
            segment_func,
            sample_func)
        logo_img.unlock()

        r = 10

        for line in line_set:
            line = pymunk.autogeometry.simplify_curves(line, .7)

            max_x = 0
            min_x = 1000
            max_y = 0
            min_y = 1000
            for l in line:
                max_x = max(max_x, l.x)
                min_x = min(min_x, l.x)
                max_y = max(max_y, l.y)
                min_y = min(min_y, l.y)

            r += 30
            if r > 255:
                r = 0

            if True:
                for i in range(len(line)-1):
                    shape = pymunk.Segment(
                        space.static_body, line[i], line[i+1], 1)
                    shape.friction = 0.9
                    shape.elasticity = 0.95
                    shape.color = (0, 0, 0)
                    space.add(shape)

    def _process_events(self):
        """
        Handle game and events like keyboard input. Call once per frame only.
        :return: None
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self._running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self._running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(self._screen, "bouncing_balls.png")
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                y = WINDOW_HEIGHT - y
                self._add_ball(Ball(x, y))

    def _update_balls(self):
        """
        Create/remove balls as necessary. Call once per frame only.
        :return: None
        """
        # Remove balls that fall below 100 vertically
        balls_to_remove = [
            ball for ball in self._balls if ball.body.position.y < -100]
        for ball in balls_to_remove:
            self._space.remove(ball, ball.body)
            self._balls.remove(ball)

    def _add_ball(self, ball):
        """
        Add a ball to the space
        :return: None
        """
        self._space.add(ball.body, ball.shape)
        self._balls.append(ball.shape)

    def _clear_screen(self):
        """
        Clears the screen.
        :return: None
        """
        self._screen.fill(TABLE_COLOUR)
        background_image = pygame.image.load("table.png")
        self._screen.blit(background_image, [0, 0])

    def _draw_objects(self):
        """
        Draw the objects.
        :return: None
        """
        self._space.debug_draw(self._draw_options)

    def _draw_balls(self):
        for ball_shape in self._balls:
            origin = ball_shape.body.position
            radius = int(BASE_RADIUS * SCALE_FACTOR)
            width = radius*2
            colour = THECOLORS['pink']
            circle = pygame.Surface([radius*2,radius*2]).convert_alpha()
            circle.fill([0,0,0,0])
            pygame.draw.circle(circle, colour, [circle.get_width()//2, circle.get_height()//2], radius+(width//2))
            self._screen.blit(circle, [origin[0] - (circle.get_width()/2), WINDOW_HEIGHT - origin[1] - (circle.get_height()/2)])


if __name__ == '__main__':
    game = PoolGame()
    game.run()
