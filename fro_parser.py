"""
Extensible framework for fro parsers
"""

import copy

class AbstractFroParser(object):
    """
    The abstract parent class which fro parsers should extend. This class should
    not be instantiated, but instead subclassed.

    Every subclass should be immutable (at least from the client's perspective).
    Also, every subclass should be implemented in such a way that no action
    performed on a parser could alter a shallow copy.
    """
    def __init__(self, fertile=True, err=None):
        """
        :param fertile: if the parser produces a meaningful value
        :param err: formatted strnig for error msg in event of failed parse
        """
        self._fertile = fertile
        self._err = err

    # public interface

    def parse(self, s):
        """
        Parses the string into an object
        :param s: string to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        chomp_result = self._chomp(s, 0, True)
        if chomp_result is None:
            return self._quit(0, True)
        value, index = chomp_result
        return value if index == len(s) else self._quit(0, True)

    def err(self, err):
        """
        Set an error message, to be thrown on parse failures
        :param err: A formatable string represent
        :return: a copy of the called parser, with set error message
        """
        carbon = copy.copy(self)
        carbon._err = err
        return carbon

    def no_err(self):
        """
        :return: a copy of called parser that does not throw errors on failed parses
        """
        if self._err is None:
            return self
        return self.err(None)

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._fertile:
            return self
        return DelegateFroParser(self, False, self._err)

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._fertile:
            return self
        return DelegateFroParser(self, True, self._err)

    def __or__(self, func):
        return MapFroParser(self, func)

    def __rshift__(self, func):
        return MapFroParser(self, lambda x: func(*x))

    # internals

    def _quit(self, index, fail_hard):
        """
        Called on a failed parse
        :param index: index of input string where failure occured
        :param fail_hard: if exceptions should be thrown on failed parses
        :return: the value to be returns
        :raises: a parse error, if the parser is configured to raise parse
            errors and fail_hard is True
        """
        if self._err is None or not fail_hard:
            return None
        raise ValueError(self._err.format(index, i=index))

    def _chomp(self, s, index, fail_hard):
        """
        ARGUMENTS:
          s : string to parse
          index : int, index of s at which to start parsing
          fail_hard : bool - if exceptions should be thrown on failed parses
        RETURNS:
          t, index : value parsed, and first "unconsumed" index of s, or None
                       if parse failed (and no exception was thrown)
        """
        return self._quit(index, fail_hard) # must be implemented by subclasses


class MapFroParser(AbstractFroParser):
    """
    Fro parser that performs map operation on parsed values
    """
    def __init__(self, parser, func):
        AbstractFroParser.__init__(self)
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, fail_hard):
        chomp_result = self._parser._chomp(s, index, fail_hard)
        if chomp_result is None:
            return self._quit(index, fail_hard)
        value, index = chomp_result
        return self._func(value), index


class DelegateFroParser(AbstractFroParser):
    """
    Fro parser that delegates parsing to another parser
    """
    def __init__(self, delegate, fertile, err):
        AbstractFroParser.__init__(self, fertile, err)
        self._delegate = delegate

    def _chomp(self, s, index, fail_hard):
        return self._delegate._chomp(s, index, fail_hard)
