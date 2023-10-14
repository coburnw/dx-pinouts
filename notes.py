import drawsvg as dw

from text import TextBlock, GoogleFont
from v_palette import get_colors

palette = 'flat'

class Note(TextBlock):
    def __init__(self, text):
        super().__init__(text)
        self.style['font_size'] = 25
        self.style['text_anchor'] = 'start'
        self.style['dominant_baseline'] = 'middle'
        self.style['font_weight'] = ''
        self.style['font_family'] = 'Roboto'

        self.cache = GoogleFont(self.style)
        return

    @property
    def margin(self):
        return self.style['font_size'] * 3


class Footnote():
    _next_id = 0

    def __init__(self, footnote):
        self._id = 0
        self._footnote = footnote

        return

    @property
    def is_used(self):
        return self._id > 0

    @property
    def id(self):
        if self._id == 0:
            self._id = self.next_id()

        return self._id

    @property
    def selector(self):
        return self._footnote['selector']

    @property
    def key(self):
        return self._footnote['key']

    @property
    def text(self):
        return self._footnote['text']

    @classmethod
    def next_id(cls):
        cls._next_id += 1
        return cls._next_id


class Footnotes(Note):
    def __init__(self, footnotes=None):
        super().__init__('')

        self.footnotes = []
        if footnotes is not None:
            self.append(footnotes)

        return

    def __iter__(self):
        for footnote in self.footnotes:
            yield(footnote)

    def append(self, footnotes):
        for footnote in footnotes:
            self.footnotes.append(Footnote(footnote))

        return

    def sort(self):
        """
        In-place sort of footnotes by footnote id

        Returns:
            Nothing
        """
        self.footnotes.sort(key=lambda footnote: footnote._id)
        return

    def generate(self, width):
        self.width = width

        style = dict(self.style)
        if 'font_size' in style:
            del style['font_size']

        x = 0
        y = 0
        self.sort()
        for footnote in self.footnotes:
            if footnote.is_used:
                text = '{}. {}'.format(footnote.id, footnote.text)
                lines, height = self.wrap_string(text, self.width)
                super().append(dw.Text(lines, self.font_size, x=x, y=y, **style))
                y += height

        self.height = y - self.font_size

        return

