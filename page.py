import math
import os

import drawsvg as dw
import pinoutOverview as Overview
from text import Text, TextBlock, FontCache


# class Margin(Overview.Region):
#     def __init__(self, location):
#         self.location = location  # left, right, top, or bottom
#         self.context = 'outside'  # inside or outside
#         self.items = []
#         return


class Border(Overview.Region):
    def place(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation

        self.append(dw.Rectangle(-self.width/2, -self.height/2, self.width, self.height,
                                 stroke="black", stroke_width=2, fill="white"))
        return self

class Title(Text):
    def __init__(self, value):
        super().__init__(value)
        self.style['font_size'] = 40
        return


class Subtitle(Text):
    def __init__(self, value):
        super().__init__(value)
        self.style['font_size'] = 20
        return

class Header(Overview.Region):
    def __init__(self, header_data):
        super().__init__(width=0, height=0)

        self.items = []

        for key, value in header_data.items():
            if key == 'title':
                self.append(Title(value))
            else:
                self.append(Subtitle(value))
        return

    def append(self, item):
        self.height += item.line_spacing
        if item.width > self.width:
            self.width = item.width

        self.items.append(item)
        return

    def place(self, x, y):
        self.x = x
        self.y = y

        for item in self.items:
            super().append(item.generate(x, y))
            y += item.height

        return self


class Note(TextBlock):
    def __init__(self, text):
        super().__init__(text)
        self.style['font_size'] = 25
        self.style['text_anchor'] = 'start'
        self.style['dominant_baseline'] = 'middle'
        self.style['font_weight'] = ''
        self.style['font_family'] = 'Roboto'
        return

    @property
    def margin(self):
        return self.style['font_size'] * 3


class Page():
    def __init__(self, page_config, pinout, legend):
        #self.page_config = page_config

        self.canvas_height = page_config.get('height', 1000)
        self.canvas_width = page_config.get('width', 1000)

        self.header = Header(page_config['header'])
        self.footer = Header(page_config['footer'])
        self.notes = page_config['notes']

        self.pinout = pinout
        self.legend = legend

        self.package_x_offset = 0
        self.package_y_offset = 0

        # start with a page
        #   drawsvg's original coordinates are top left corner.
        #   we move zero zero to center of page
        self.dw_page = dw.Drawing(self.canvas_width, self.canvas_height, origin='center')

        self.dw_page.embed_google_font('Roboto Mono')
        # self.dw_page.embed_google_font('Roboto')

        return

    @property
    def leftward(self):  # leftward?
        # svg coordinates: +x to the right, +y to the bottom
        return -1

    @property
    def rightward(self):
        return 1

    @property
    def upward(self):
        return -1

    @property
    def downward(self):
        return 1

    def generate(self):
        print(self.canvas_width, "  ", self.canvas_height)

        # add a Border
        border = Border(self.canvas_width, self.canvas_height)
        self.dw_page.append(border.place(0, 0))

        # Attach Header
        x = 0
        y = border.top + self.header.height
        self.dw_page.append(self.header.place(x, y))

        # Attach Footer
        x = 0
        y = border.bottom - self.footer.height
        self.dw_page.append(self.footer.place(x, y))

        # attach pinout
        self.dw_page.append(self.pinout.place(0, 0))

        # attach notes
        index = 0
        for string in self.notes:
            note = Note(string)
            if index in [0, 2]:
                x = border.left - note.margin * self.leftward
                width = x - (self.pinout.width / 2 + note.margin) * self.leftward
            else:
                x = (self.pinout.width / 2 + note.margin) * self.rightward
                width = (border.right - note.margin) - x

            note.generate(abs(width))

            if index in [0, 1]:
                # y = self.header.bottom + self.pinout.height / 2
                y = self.pinout.top + (note.margin + note.height) * self.upward
            else:
                y = self.pinout.bottom + note.margin * self.downward

            index += 1
            self.dw_page.append(note.place(x, y))

        x = border.left - note.margin * self.leftward
        y = self.header.top + self.legend.height
        self.dw_page.append(self.legend.place(x, y))

        self.embed_fonts()

        return

    def embed_fonts(self):
        style = dict()
        style['font_size'] = 25
        style['text_anchor'] = 'start'
        style['dominant_baseline'] = 'middle'
        style['font_weight'] = ''
        style['font_family'] = 'Roboto'

        cache = FontCache(style)
        self.dw_page.append_css(cache.css_font)

        return

    def save(self, name):
        self.generate()

        basename = os.path.basename(name)
        name, suffix = os.path.splitext(basename)
        name = '{}.svg'.format(name)

        self.dw_page.save_svg(name)

