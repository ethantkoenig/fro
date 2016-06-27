import copy

import fro_chomper


class FroParser(object):
    """
    An immutable parser
    """
    def __init__(self, chomper):
        self._chomper = chomper

    # public interface

    def parse(self, s):
        """
        Parses the string into an object
        :param s: string to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        logger = fro_chomper.FroParseErrorTracker()
        chomp_result = self._chomper._chomp(s, 0, logger)
        if chomp_result is None:
            if self._chomper._quiet:
                return None
            raise logger.retrieve_error()
        value, index = chomp_result
        if index < len(s):
            if self._chomper._quiet:
                return None
            raise logger.retrieve_error()
        elif index > len(s):
            raise AssertionError("Invalid index")  # should never happen
        return value

    def name(self, name):
        """
        Set a name for the parser, to be used in error messages
        :param name: name for parser
        :return: a copy of the called parser, with set error message
        """
        carbon = copy.copy(self._chomper)
        carbon._name = name
        return FroParser(carbon)

    def quiet(self):
        carbon = copy.copy(self._chomper)
        carbon._quiet = True
        return FroParser(carbon)

    def lstrip(self):
        if self._chomper._fertile:
            return FroParser(fro_chomper.CompositionChomper(
                [r"@\s*", self._chomper], reducer=lambda x: x))
        return -(+self).lstrip()

    def rstrip(self):
        if self._chomper._fertile:
            return FroParser(fro_chomper.CompositionChomper(
                [self._chomper, r"@\s*"], reducer=lambda x: x))
        return -(+self).rstrip()

    def strip(self):
        return self.lstrip().rstrip()

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._chomper._fertile:
            return self
        return FroParser(fro_chomper.DelegateChomper(
            self._chomper, False, self._chomper._name))

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._chomper._fertile:
            return self
        return FroParser(fro_chomper.DelegateChomper(
            self._chomper, True, self._chomper._name))

    def __or__(self, func):
        return FroParser(fro_chomper.MapChomper(self._chomper, func))

    def __rshift__(self, func):
        return FroParser(fro_chomper.MapChomper(self._chomper, lambda x: func(*x)))
