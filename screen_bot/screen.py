#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import Image


class ScreenGrab:

    def screen(self, x1=None, y1=None, x2=None, y2=None):
        return self.get_screener()(x1, y1, x2, y2)

    def get_screener(self):
        for module, impl in [
                #('gtk', self.get_screen_by_gtk),
                    ('PyQt4', self.get_screen_by_qt),
                    ('wx', self.get_screen_by_wx),
                    ('ImageGrab', self.get_screen_by_imaging)]:
            try:
                __import__(module)
            except ImportError:
                pass
            else:
                return impl

        raise NotImplementedError

    def get_screen_by_gtk(self, x1=None, y1=None, x2=None, y2=None):
        import gtk.gdk
        w = gtk.gdk.get_default_root_window()
        sz = w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
        pb = pb.get_from_drawable(w, w.get_colormap(),
                                            0, 0, 0, 0, sz[0], sz[1])
        if (pb != None):
            return None
        else:
            width = pb.get_width()
            height = pb.get_height()
            return Image.fromstring("RGB", (width, height), pb.get_pixels())

    def get_screen_by_qt(self, x1=None, y1=None, x2=None, y2=None):
        from PyQt4.QtGui import QPixmap, QApplication
        from PyQt4.Qt import QBuffer, QIODevice
        import StringIO

        app = QApplication(sys.argv)
        _buffer = QBuffer()
        _buffer.open(QIODevice.ReadWrite)

        desktop = QApplication.desktop()
        #width = desktop.screenGeometry().width()
        #height = desktop.screenGeometry().height()

        if x1 is None:
            x1 = 0
        if y1 is None:
            y1 = 0
        if x2 is None:
            x2 = -1
        else:
            x2 -= x1
        if y2 is None:
            y2 = -1
        else:
            y2 -= y1

        QPixmap.grabWindow(desktop.winId(), x1, y1, x2, y2) \
                                    .save(_buffer, 'png')
        strio = StringIO.StringIO()
        strio.write(_buffer.data())
        _buffer.close()
        del app
        strio.seek(0)
        return Image.open(strio)

    def get_screen_by_imaging(self, x1=None, y1=None, x2=None, y2=None):
        import ImageGrab
        img = ImageGrab.grab()
        return img

    def get_screen_by_wx(self, x1=None, y1=None, x2=None, y2=None):
        import wx
        app = wx.App()  # Need to create an App instance before doing anything
        screen = wx.ScreenDC()
        size = screen.GetSize()
        bmp = wx.EmptyBitmap(size[0], size[1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
        del mem  # Release bitmap
        #bmp.SaveFile('screenshot.png', wx.BITMAP_TYPE_PNG)
        myWxImage = wx.ImageFromBitmap(bmp)
        PilImage = Image.new('RGB', (myWxImage.GetWidth(),
            myWxImage.GetHeight()))
        PilImage.fromstring(myWxImage.GetData())
        return PilImage


if __name__ == '__main__':
    s = ScreenGrab()
    #screen = s.screen(100, 100, 101, 101)
    screen = s.screen(100, 100, 101, 101)
    #screen.show()
    screen.save('test.png')
