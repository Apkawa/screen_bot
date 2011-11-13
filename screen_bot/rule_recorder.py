# -*- coding: utf-8 -*-
import sys
import pymouse
import logging
from time import sleep
import yaml

logging.basicConfig()
log = logging.getLogger('screen_bot:recorder')
log.setLevel(logging.INFO)


class Recorder(pymouse.PyMouseEvent):
    pause = False

    def __init__(self, filename=None, screen=None):
        from bot import Screen
        self.screen = screen or Screen.init_screen()
        self.records = []
        self.filename = filename
        super(Recorder, self).__init__()

    def is_in_screen(self, x, y):
        return (
                self.screen.x <= x <= self.screen.x + self.screen.width
                and self.screen.y <= y <= self.screen.y + self.screen.height
                )

    def record(self, x, y, button, press):
        x, y = self.screen.coordinate_to_relative(x, y)
        log.info("CLICK x:%s y:%s, button:%s, press: %s", x, y, button, press)
        r = {
                'x': x,
                'y': y,
                'button': button,
                'press': press,
                'press_type': press and 'press' or 'release',
                }
        self.records.append(r)
        if self.filename:
            open(self.filename, 'w').write(yaml.dump(self.records))

    def get_color(self, x, y):
        x, y = self.screen.coordinate_to_relative(x, y)
        color = {'x': x, 'y': y, 'rgb': self.screen.get_color_by_point(x, y)}
        log.info("COLOR: %s", color)

    def click(self, x, y, button, press):
        """Subclass this method with your click event handler"""

        if self.is_in_screen(x, y) and not self.pause:
            self.get_color(x, y)
            self.record(x, y, button, press)

    def move(self, x, y):
        """Subclass this method with your move event handler"""

        #log.info("MOVE x:%s y:%s", x, y)

    def waiter(self):
        while True:
            cmd = raw_input(" >")
            log.info("CMD: %s", cmd)
            if cmd == 'p':
                log.info('PAUSE')
                self.pause = not self.pause


if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = None
    rec = Recorder(filename=filename)
    rec.start()
    try:
        rec.waiter()
    except KeyboardInterrupt:
        rec.stop()
        log.info("FINISH")
