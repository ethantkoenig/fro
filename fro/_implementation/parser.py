from fro._implementation import chompers


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
        tracker = chompers.FroParseErrorTracker(s)
        chomp_result = self._chomper.chomp(s, 0, tracker)
        if chomp_result is None:
            if self._chomper.quiet():
                return None
            raise tracker.retrieve_error()
        value, index = chomp_result
        if index < len(s):
            if self._chomper.quiet():
                return None
            raise tracker.retrieve_error()
        elif index > len(s):
            raise AssertionError("Invalid index")  # should never happen
        return value

    def name(self, name):
        """
        Set a name for the parser, to be used in error messages
        :param name: name for parser
        :return: a copy of the called parser, with set error message
        """
        return FroParser(self._chomper.clone(name=name))

    def maybe(self, default=None):
        return FroParser(chompers.OptionalChomper(
            self._chomper,
            default=default,
            fertile=self._chomper.fertile(),
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def quiet(self):
        return FroParser(self._chomper.clone(quiet=True))

    def lstrip(self):
        if self._chomper.fertile():
            return FroParser(chompers.CompositionChomper(
                [chompers.RegexChomper(r"\s*", fertile=False), self._chomper],
                fertile=True,
                name=self._chomper.name(),
                quiet=self._chomper.quiet())).get()
        return -((+self).lstrip())

    def rstrip(self):
        if self._chomper.fertile():
            return FroParser(chompers.CompositionChomper(
                [self._chomper, chompers.RegexChomper(r"\s*", fertile=False)],
                fertile=True,
                name=self._chomper.name(),
                quiet=self._chomper.quiet())).get()
        return -((+self).rstrip())

    def strip(self):
        return self.lstrip().rstrip()

    def get(self):
        return self >> (lambda x: x)

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._chomper.fertile():
            return self
        return FroParser(chompers.DelegateChomper(
            self._chomper,
            fertile=False,
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._chomper.fertile():
            return self
        return FroParser(chompers.DelegateChomper(
            self._chomper,
            fertile=True,
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __or__(self, func):
        return FroParser(chompers.MapChomper(
            self._chomper,
            func,
            fertile=self._chomper.fertile(),
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __rshift__(self, func):
        return FroParser(chompers.MapChomper(
            self._chomper,
            lambda x: func(*x),
            fertile=self._chomper.fertile(),
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))
