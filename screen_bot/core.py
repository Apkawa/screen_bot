# -*- coding: utf-8 -*-
import Xlib
import Image
from collections import namedtuple
from itertools import izip, repeat
from time import sleep
import logging

import pymouse

from screen import ScreenGrab

logging.basicConfig()
log = logging.getLogger('screen_bot:core')
log.setLevel(logging.INFO)



Point = namedtuple('Point', ['x', 'y'])
RGB = namedtuple('RGB', ['r', 'g', 'b'])


class Color(object):
    RGB_TOLERANCE = 3

    @staticmethod
    def rgb_dist((r0, g0, b0), (r1, g1, b1)):
        """Computes a color-distance between two RGB colors.
        Nothing fancy, just the sum of distances
        in R, G and B coordinates"""
        return abs(r0 - r1) + abs(g0 - g1) + abs(b0 - b1)

    @staticmethod
    def compare(rgb1, rgb2, distance=RGB_TOLERANCE):
        log.debug("Compare %s == %s", rgb1, rgb2)
        return Color.rgb_dist(rgb1, rgb2) < distance

    @staticmethod
    def get_average_color(pix, center_x, center_y, size=5):
        avg_color = [0, 0, 0]
        count = 0
        for x in xrange(center_x - size, center_x + size):
            for y in xrange(center_y - size, center_y + size):
                color = pix[x, y]
                for i in xrange(3):
                    avg_color[i] += color[i]
                count += 1
        for i in xrange(3):
            avg_color[i] /= count

        return avg_color

    @staticmethod
    def match(pix, x, y, rgb_color, distance=3):
        return Color.compare(pix[x, y], rgb_color, distance)

    @staticmethod
    def match_all_color(pix, colors, distance=3):
        '''
        colors is [{'x': x, 'y': y, 'rgb':(r, g, b)},]
        '''
        for c in colors:
            if not Color.match(pix,
                    c['x'], c['y'], c['rgb'], distance=3):
                return None
        return True


class Screenshoter(object):
    def screen(self, x1=None, y1=None, x2=None, y2=None):
        return ScreenGrab().screen(x1, y1, x2, y2)



class Screen(object):

    width = None
    height = None

    x = None
    y = None

    display = None

    _count_get_screen = 0

    def get_screenshot_class(self):
        return Screenshoter

    @property
    def screenshot(self):
        return self.get_screenshot_class()()

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
        self.mouse = pymouse.PyMouse()
        self.display = self.get_display_size()

    def get_display_size(self):
        return Point(*self.mouse.screen_size())

    @classmethod
    def init_screen(cls):
        return cls(*cls().find_screen())

    def coordinate_to_relative(self, x, y):
        return x - self.x, y - self.y

    def coordinate_to_absolute(self, x, y):
        return x + self.x, y + self.y

    def match_screen(self, pix, x, y):
        raise NotImplemented

    def get_match_function(self):
        return self.match_screen

    def find_screen(self, pix=None):
        pix = pix or self.screenshot.screen().load()
        x = 0
        y = 0
        for w in xrange(self.display[0] / 2):
            x = w
            for h in xrange(self.display[1] / 2):
                y = h
                if self.get_match_function()(pix, x, y):
                    log.info("Found screen game: x:%s, y:%s", x, y)
                    return x, y

        raise Exception("Not Found game!")

    def _debug_save(self, screen):
        screen.save('debug/%s.png' % self._count_get_screen)
        self._count_get_screen += 1

    def get_screen_image(self):
        screen = self.screenshot.screen(
                    self.x, self.y,
                    self.x + self.width, self.y + self.height)
        #self._debug_save(screen)
        return screen

    def get_color_by_point(self, x, y, absolute=False):
        display = Xlib.display.Display()
        screen = display.screen()
        if not absolute:
            x, y = self.coordinate_to_absolute(x, y)
        image = screen.root.get_image(x, y, 1, 1, format=Xlib.X.ZPixmap,
                plane_mask=0xffffff)
        return Image.fromstring('RGB', (1, 1), image.data, 'raw', "BGRX"
                                ).load()[0, 0]


class BaseExplorer(object):

    def __init__(self, game_screen):
        self.screen = game_screen
        self.mouse = pymouse.PyMouse()

    def mouse_action(self, action, x, y, **kwargs):
        getattr(self.mouse, action)(self.screen.x + x,
                                self.screen.y + y, **kwargs)

    def click(self, x, y):
        self.mouse_action('click', x, y)

    def human_move(self, to_point, from_point=None, speed=1000):
        if not from_point:
            from_point = Point(*self.mouse.position())

        if from_point.x != to_point.x:
            range_x = xrange(from_point.x, to_point.x,
                            from_point.x > to_point.x and -1 or 1)
        else:
            range_x = repeat(from_point.x)

        if from_point.y != to_point.y:
            range_y = xrange(from_point.y, to_point.y,
                            from_point.y > to_point.y and -1 or 1)
        else:
            range_y = repeat(from_point.y)

        for x, y in izip(range_x, range_y):
            self.move(x, y)
            sleep(30.0 / speed)

    def move(self, x, y):
        self.mouse_action('move', x, y)

    def press(self, x, y):
        self.mouse_action('press', x, y)

    def release(self, x, y):
        self.mouse_action('release', x, y)



class BaseBot(object):
    screen_class = Screen

    def get_screen_class(self):
        return self.screen_class

    def is_init_screen(self):
        return bool(self.get_screen())

    def set_screen(self, screen):
        setattr(self, '__screen', screen)

    def get_screen(self):
        return getattr(self, '__screen', None)

    screen = property(fget=get_screen)

    def is_valid_screen(self):
        return self.screen.is_game()

    def init_screen(self):
        self.set_screen(self.screen_class.init_screen())

