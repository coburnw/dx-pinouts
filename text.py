import requests
from io import BytesIO
from PIL import ImageFont

import drawsvg as dw
import pinoutOverview as Overview


class FontCache():
    _font_face = None  # a css font-face string with url to font data
    _font_data = None  # a BytesIO data stream of cached font data

    def __init__(self, style):
        self.style = style

        font_face = self.get_font_face()
        if font_face is None:
            font_face = self.get_google_font_face(self.style['font_family'])
            self.set_font_face(font_face)

        font_data = self.get_font_data()
        if font_data is None:
            font_data = self.get_google_font_data(font_face)
            self.set_font_data(font_data)

        self._font_size = self.style['font_size']
        self._font = ImageFont.truetype(font_data, self.font_size)

        return

    @property
    def font(self):
        return self._font

    @property
    def css_font(self):
        font_face = self.get_font_face()
        prefix, url_open, suffix = font_face.partition('url(')
        junk, url_close, suffix = suffix.partition(')')

        bin_font_data = self.get_font_data().getvalue()
        mime = 'application/octet-stream'
        font_data = dw.url_encode.bytes_as_data_uri(bin_font_data, strip_chars='', mime=mime)

        loaded = prefix + url_open + font_data + url_close + suffix

        return loaded

    @property
    def font_size(self):
        return self._font_size

    @classmethod
    def set_font_face(cls, font_face):
        cls._font_face = font_face
        return

    @classmethod
    def get_font_face(cls, loaded=False):
        return cls._font_face

    @classmethod
    def set_font_data(cls, font_data):
        cls._font_data = font_data
        return cls._font_data

    @classmethod
    def get_font_data(cls):
        try:
            cls._font_data.seek(0)
            return cls._font_data
        except:
            return None

    def get_google_font_face(self, family_name, kwargs=dict()):
        google_url = "https://fonts.googleapis.com/css2"
        kwargs.update(dict(family=family_name))
        req = requests.get(google_url, params=kwargs)
        print('downloaded {}'.format(req.url))
        return req.text

    def get_google_font_data(self, font_face):
        text = font_face
        start = text.rfind('url(')
        line = text[start + 4:]
        end = line.find(')')
        font_url = line[:end]

        req = requests.get(font_url)
        print('downloaded {}'.format(req.url))
        font_data = BytesIO(req.content)

        return font_data


class Text:
    def __init__(self, value):
        self.value = str(value)

        self.offset = 0
        self.vert_offset = 0
        self.disabled = False

        self.style = dict(
            font_size=12,
            text_anchor='middle',
            dominant_baseline='middle',
            fill="black",
            font_weight='bold',
            font_family='Roboto Mono'
        )

        return

    @property
    def line_spacing(self):
        return self.style['font_size'] * 1.2

    @property
    def width(self):
        # a simplistic to the point of being bogus value
        return self.style['font_size'] + len(self.value)

    @property
    def height(self):
        return self.line_spacing

    def generate(self, x=0, y=0):
        text = self.value
        if self.disabled:
            text = ''

        style = dict(self.style)
        if 'font_size' in style:
            del style['font_size']

        x += self.offset
        y += self.vert_offset

        return dw.Text(text, self.style['font_size'], x, y, **style)


class TextBlock(Overview.Region):
    def __init__(self, text, id=None, width=0, height=0):
        super().__init__(width, height)

        #self.id = id
        self.text = text
        self.width = width
        self.height = height

        self.style = dict(
            font_size=12,
            text_anchor='middle',
            dominant_baseline='middle',
            fill="black",
            font_weight='bold',
            font_family='Roboto Mono'
        )

        # print(self.text.style['font_family'], self.text.style['font_size'], width, height)

        return

    @property
    def font(self):
        return self.cache.font

    @property
    def font_size(self):
        return self.cache.font_size

    def wrap_string(self, string, width):
        words = string.split(' ')

        lines = []
        line = ''
        line_length = self.font.getlength(line)
        for word in words:
            word = word.strip()
            word_length = self.font.getlength(word)
            if (line_length + word_length) < width:
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '

            line_length = self.font.getlength(line)

        lines.append(line)
        height = len(lines) * self.font_size + self.font_size / 2

        return lines, height

    def generate(self, width):
        self.width = width
        self.cache = FontCache(self.style)

        style = dict(self.style)
        if 'font_size' in style:
            del style['font_size']

        x = 0
        y = 0
        for string in self.text:
            lines, height = self.wrap_string(string, self.width)
            self.append(dw.Text(lines, self.font_size, x=x, y=y, **style))
            y += height

        self.height = y - self.font_size

        return

    def place(self, x, y):
        self.x = x
        self.y = y

        return dw.Use(self, x=self.x, y=self.y)

