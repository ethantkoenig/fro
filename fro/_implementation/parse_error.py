from fro._implementation import pretty_printing


class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, string, message, start_index, end_index=None, name=None, cause=None):
        """
        :param string: string being parsed
        :param message: description of error
        :param start_index: beginning index of substring causing error
        :param end_index: end index of substring causing error
        :param cause: Exception that triggered this exception
        """
        self._string = string
        self._message = message
        self._start_index = start_index
        if end_index is None:
            self._end_index = min(start_index + 1, len(string))
        else:
            self._end_index = end_index
        self._name = name
        self._cause = cause

    def __str__(self):
        if self._name is None:
            msg = self._message
        else:
            msg = "{m} when parsing {n}".format(m=self._message, n=self._name)
        first_line = "{m} at indices {s} to {e}".format(
            m=msg,
            s=self._start_index,
            e=self._end_index)
        return "\n".join([first_line, self.context()])

    def cause(self):
        return self._cause

    def context(self):
        return pretty_printing.printable_substring_with_context(
                self._string,
                self._start_index,
                self._end_index)

    def end_index(self):
        return self._end_index

    def message(self):
        return self._message

    def name(self):
        return self._name

    def start_index(self):
        return self._start_index

