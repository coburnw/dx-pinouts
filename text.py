# text.py - text and font related utilities.
#
# Copyright (c) 2023 Coburn Wightman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
from io import BytesIO
from PIL import ImageFont

import drawsvg as dw
import pinoutOverview as Overview


class GoogleFontCache():
    __font_cache = dict()

    def __init__(self, font_style=None):
        self._font_style = font_style
        self._font = None

        if self._font_style is not None:
            font_name = self._font_style['font_family']
            try:
                self._font = self._font_cache[font_name]
            except KeyError:
                font_face = self._download_google_font_face(font_name)
                font_data = self._download_google_font_data(font_face)
                font = dict(face=font_face, data=font_data)

                self._font_cache[font_name] = font
                self._font = font

        return

    def __iter__(self):
        font_style = dict()
        for font_name in self._get_font_cache():
            font_style['font_family'] = font_name
            yield GoogleFont(font_style)

        return

    @property
    def font_face(self):
        return self._font['face']

    @property
    def font_data(self):
        return self._font['data']

    @property
    def _font_cache(self):
        return self._get_font_cache()

    @classmethod
    def _get_font_cache(cls):
        return cls.__font_cache

    def _download_google_font_face(self, family_name):  # , kwargs=dict()
        google_url = "https://fonts.googleapis.com/css2"
        # kwargs.update(dict(family=family_name))
        kwargs = dict(family=family_name)
        req = requests.get(google_url, params=kwargs)

        print('downloading {}'.format(req.url))
        return req.text

    def _download_google_font_data(self, font_face):
        text = font_face
        start = text.rfind('url(')
        line = text[start + 4:]
        end = line.find(')')
        font_url = line[:end]

        req = requests.get(font_url)
        font_data = req.content

        #print('downloaded {}'.format(req.url))
        return font_data


class GoogleFont():
    def __init__(self, font_style):
        """

        Args:
            font_style (dict): font style including font_family attribute.
        """
        self.style = font_style
        self._cache = GoogleFontCache(font_style)

        self._font_data_stream = None
        return

    @property
    def font_size(self):
        return self.style['font_size']

    @property
    def font_face(self):
        return self._cache.font_face

    @property
    def font_data(self):
        return self._cache.font_data

    @property
    def font_data_stream(self):
        if self._font_data_stream is None:
            self._font_data_stream = BytesIO(self.font_data)

        self._font_data_stream.seek(0)
        return self._font_data_stream

    @property
    def image_font(self):
        return ImageFont.truetype(self.font_data_stream, self.font_size)

    @property
    def css_font(self):
        prefix, url_open, suffix = self.font_face.partition('url(')
        junk, url_close, suffix = suffix.partition(')')

        mime = 'application/octet-stream'
        encoded_data = dw.url_encode.bytes_as_data_uri(self.font_data, strip_chars='', mime=mime)
        loaded = prefix + url_open + encoded_data + url_close + suffix

        return loaded


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

        self.font = None
        return

    @property
    def line_spacing(self):
        return self.style['font_size'] * 1.2

    @property
    def width(self):
        if self.font is not None:
            # use ImageFont length calculation for 'high precision'
            length = self.font.image_font.getlength(self.value)
        else:
            # else return a rough approximation
            length = self.style['font_size'] * len(self.value)

        return length

    @property
    def height(self):
        # hmm. a text can have newlines, right?
        return self.line_spacing

    def generate(self, x=0, y=0):
        self.font = GoogleFont(self.style)

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

        self.cache = None
        return

    @property
    def font(self):
        return self.cache.image_font

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
        self.cache = GoogleFont(self.style)

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

