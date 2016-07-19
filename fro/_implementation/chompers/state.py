from fro._implementation.iters import CheckableIterator
from fro._implementation.location import Location


class ChompState(object):
    """
    Represents a position during parsing/chomping
    """
    def __init__(self, lines, column=0):
        """
        :param lines: iterable<str>
        :param column: index at which to start
        """
        self._lines = CheckableIterator(lines)
        self._column = column
        self._line = -1

        if self._lines.has_next():
            self._curr = next(self._lines)
            self._len_curr = len(self._curr)
            self._line += 1

    def advance_to(self, column):
        #self._assert_valid_col(column)
        #if column < self._column:
        #    msg = "Cannot advance column from {0} to {1}".format(self._column, column)
        #    raise ValueError(msg)
        while column == self._len_curr and self._lines.has_next():
            self._curr = next(self._lines)
            self._len_curr = len(self._curr)
            self._line += 1
            column = 0  # "recurse" onto start of next line
        self._column = column

    def at_end(self):
        return self._column == self._len_curr and not self._lines.has_next()

    def column(self):
        return self._column

    def current(self):
        return self._curr

    def line(self):
        return self._line

    def location(self):
        return Location(self._line, self._column, self._curr)

    def reset_to(self, column):
        #self._assert_valid_col(column)
        #if column > self._column:
        #    msg = "Cannot reset column from {0} to {1}".format(self._column, column)
        #    raise ValueError(msg)
        self._column = column

    # def _assert_valid_col(self, column):
    #     if column < 0:
    #         raise ValueError("column ({0}) must be non-negative".format(column))
    #     elif column > len(self._lines.current()):
    #         msg = "column ({0}) is greater than line length ({1})".format(
    #             column, len(self._lines.current()))
    #         raise ValueError(msg)
