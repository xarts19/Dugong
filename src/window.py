#!/usr/bin/env python

"""Game window

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:23:45.187597 "

import sys
import os
import logging
import colorer

try:
    import pygame
    import pygame.locals as pl
except ImportError as ex:
    #LOGGER.exception("%s Failed to load module." % __file__)
    sys.exit("%s Failed to load module. %s" % (__file__, ex))

if not pygame.font: LOGGER.warning('Fonts disabled')
if not pygame.mixer: LOGGER.warning('Sound disabled')

import gamemap
import units

LOGGER = logging.getLogger('main.window')

class Window(object):

    def __init__(self):
        """Called when the the GameWindow object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools."""

        LOGGER.debug('Initializing window')

        # load and set up pygame
        pygame.init()

        # create our window

        # initial window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'

        screen_size = (800, 800)

        self.window = pygame.display.set_mode(screen_size, pl.DOUBLEBUF)

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("Ancient Empires")

        # disable mouse
        pygame.mouse.set_visible(1)

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        pygame.event.set_allowed([pl.QUIT, pl.KEYDOWN])

        self._init_game()

    def _init_game(self):
        LOGGER.debug('Initializing game map')
        self.map = gamemap.GameMap()
        self.map_image = self.map.get_image()
        self.units = [units.Unit()]
        self.allsprites = pygame.sprite.RenderUpdates(self.units)

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        LOGGER.debug('Game started')

        running = True
        # run until something tells us to stop
        while running:

            # tick pygame clock
            # you can limit the fps by passing the desired frames per second to tick()
            self.clock.tick(60)

            # update the title bar with our frames per second
            pygame.display.set_caption('Ancient Empires, %d fps' % self.clock.get_fps())

            # draw map
            self.window.fill((255, 225, 255))
            self.window.blit(self.map_image, (0, 0))
            self.allsprites.draw(self.window)

            # render the screen, even though we don't have anything going on right now
            pygame.display.flip()

            # handle pygame events -- if user closes game, stop running
            running = self.handleEvents()

        LOGGER.debug('Game finished')

    def handleEvents(self):
        """Poll for PyGame events and behave accordingly. Return false to stop
        the event loop and end the game."""

        # poll for pygame events
        for event in pygame.event.get():
            if event.type == pl.QUIT:
                return False

            # handle user input
            elif event.type == pl.KEYDOWN:
                # if the user presses escape, quit the event loop.
                if event.key == pl.K_ESCAPE:
                    return False
        return True

