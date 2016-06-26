"""
Extensible framework for fro parsers
"""

import copy

import composition_parser


class AbstractFroParser(object):
    """
    The abstract parent class which fro parsers should extend. This class should
    not be instantiated, but instead subclassed.

    Every subclass should be immutable (at least from the client's perspective).
    Also, every subclass should be implemented in such a way that no action
    performed on a parser could alter a shallow copy.
    """
    def __init__(self, fertile=True, name=None, quiet=False):
        """
        :param fertile: if the parser produces a meaningful value
        :param name: name of parser, for error messages
        """
        self._fertile = fertile
        self._name = name
        self._quiet = quiet

    # public interface

    def parse(self, s):
        """
        Parses the string into an object
        :param s: string to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        logger = FroParseErrorTracker()
        chomp_result = self._chomp(s, 0, logger)
        if chomp_result is None:
            if self._quiet:
                return None
            raise logger.retrieve_error()
        value, index = chomp_result
        if index < len(s):
            if self._quiet:
                return None
            raise logger.retrieve_error()
        elif index > len(s):
            raise AssertionError("Invalid index")  # should never happen
        return value

    def name(self, name):
        """
        Set an error message, to be thrown on parse failures
        :param name: error message to be thrown TODO
        :return: a copy of the called parser, with set error message
        """
        carbon = copy.copy(self)
        carbon._name = name
        return carbon

    def quiet(self):
        carbon = copy.copy(self)
        carbon._quiet = True
        return carbon

    def lstrip(self):
        if self._fertile:
            return composition_parser.CompositionFroParser([r"@\s*", self], reducer=lambda x: x)
        return -composition_parser.CompositionFroParser([r"@\s*", +self], reducer=lambda x: x)

    def rstrip(self):
        if self._fertile:
            return composition_parser.CompositionFroParser([self, r"@\s*"], reducer=lambda x: x)
        return -composition_parser.CompositionFroParser([+self, r"@\s*"], reducer=lambda x: x)

    def strip(self):
        return self.lstrip().rstrip()

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._fertile:
            return self
        return DelegateFroParser(self, False, self._name)

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._fertile:
            return self
        return DelegateFroParser(self, True, self._name)

    def __or__(self, func):
        return MapFroParser(self, func)

    def __rshift__(self, func):
        return MapFroParser(self, lambda x: func(*x))

    # internals

    @staticmethod
    def _apply(start_index, end_index, func, *args):
        try:
            return func(*args)
        except StandardError as e:
            raise FroParseError(str(e), start_index, end_index, e)

    def _log_error(self, logger, base_msg, start_index, end_index=None):
        end_index = start_index + 1 if end_index is None else end_index
        msg = base_msg if self._name is None else "{} when parsing {}".format(base_msg, self._name)
        logger.report_error(FroParseError(msg, start_index, end_index))

    def _chomp(self, s, index, tracker):
        """
        ARGUMENTS:
          s : string to parse
          index : int, index of s at which to start parsing
          tracker : FroParseErrorTracker - tracks errors encountered during parsing
        RETURNS:
          t, index : value parsed, and first "unconsumed" index of s, or None
                       if parse failed (and no exception was thrown)
        """
        return None  # must be implemented by subclasses


class FroParseError(StandardError):

    def __init__(self, message, start_index, end_index=None, cause=None):
        self._message = message
        self._start_index = start_index
        self._end_index = end_index if end_index is not None else start_index + 1
        self._cause = cause

    def __str__(self):
        return self._message

    def cause(self):
        return self._cause

    def start_index(self):
        return self._start_index

    def end_index(self):
        return self._end_index


class FroParseErrorTracker(object):

    def __init__(self):
        self._error = None

    def report_error(self, error):
        if self._error is None or error.end_index() >= self._error.end_index():
            self._error = error

    def retrieve_error(self):
        return self._error


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
    def __init__(self, delegate, fertile, name):
        AbstractFroParser.__init__(self, fertile, name)
        self._delegate = delegate

    def _chomp(self, s, index, fail_hard):
        return self._delegate._chomp(s, index, fail_hard)
