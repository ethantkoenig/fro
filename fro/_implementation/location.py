

class Location(object):
    def __init__(self, line, column, text):
        self._line = line
        self._column = column
        self._text = text

    def __eq__(self, other):
        return self._line == other._line and self._column == other._column \
            and self._text == other._text

    def __gt__(self, other):
        return self._line > other._line \
                or (self._line == other._line and self._column > other._column)

    def __lt__(self, other):
        return self._line < other._line \
                or (self._line == other._line and self._column < other._column)

    def __str__(self):
        return "Line {l}, column {c}, text{t}".format(
            l=self._line, c=self._column, t=self._text)

    def column(self):
        return self._column

    def line(self):
        return self._line

    def text(self):
        return self._text


