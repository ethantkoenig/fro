from fro._implementation.location import Location


class ChompState(object):
    """
    Represents a position during parsing/chomping
    """
    def __init__(self, lines, column=0):
        """
        :param lines: Stream<str>
        :param column: index at which to start
        """
        self._lines = lines
        self._column = column

        if self._lines.index() == -1 and self._lines.has_next():
            next(self._lines)

    def advance_to(self, column):
        self._assert_valid_col(column)
        if column < self._column:
            msg = "Cannot advance column from {0} to {1}".format(self._column, column)
            raise ValueError(msg)
        while column == len(self._lines.current()) and self._lines.has_next():
            next(self._lines)
            column = 0  # "recurse" onto start of next line
        self._column = column

    def at_end(self):
        return self._column == len(self._lines.current()) and not self._lines.has_next()

    def column(self):
        return self._column

    def current(self):
        return self._lines.current()

    def line(self):
        return self._lines.index()

    def location(self):
        return Location(self.line(), self.column(), self.current())

    def reset_to(self, column):
        self._assert_valid_col(column)
        if column > self._column:
            msg = "Cannot reset column from {0} to {1}".format(self._column, column)
            raise ValueError(msg)
        self._column = column

    def _assert_valid_col(self, column):
        if column < 0:
            raise ValueError("column ({0}) must be non-negative".format(column))
        elif column > len(self._lines.current()):
            msg = "column ({0}) is greater than line length ({1})".format(
                column, len(self._lines.current()))
            raise ValueError(msg)
