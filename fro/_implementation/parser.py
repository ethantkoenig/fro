from fro._implementation import chompers, iters, parse_error


class FroParser(object):
    """
    An immutable parser
    """
    def __init__(self, chomper, quiet=False):
        self._chomper = chomper
        self._quiet = quiet

    # public interface

    def parse(self, lines):
        """
        Parses the string into an object
        :param lines: lines to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        tracker = chompers.abstract.FroParseErrorTracker()
        state = chompers.state.ChompState(iters.Stream(lines))
        try:
            value = self._chomper.chomp(state, tracker)
        except chompers.chomp_error.ChompError as e:
            tracker.report_error(e)
            return self._failed_parse(state, tracker)
        if not state.at_end():
            return self._failed_parse(state, tracker)
        return value

    def parse_str(self, string_to_parse):
        return self.parse([string_to_parse])

    def name(self, name):
        """
        :return: a parser identical to this, but with specified name
        """
        return FroParser(self._chomper.clone(name=name))

    def maybe(self, default=None):
        return FroParser(chompers.util.OptionalChomper(
            self._chomper,
            default=default,
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    def quiet(self):
        return FroParser(self._chomper, quiet=True)

    def loud(self):
        return FroParser(self._chomper, quiet=False)

    def lstrip(self):
        if self._chomper.fertile():
            chomper = chompers.composition.CompositionChomper(
                [chompers.regex.RegexChomper(r"\s*", fertile=False), self._chomper],
                fertile=True,
                name=self._chomper.name())
            return FroParser(chomper, quiet=self._quiet).get()
        return -((+self).lstrip())

    def rstrip(self):
        if self._chomper.fertile():
            chomper = chompers.composition.CompositionChomper(
                [self._chomper, chompers.regex.RegexChomper(r"\s*", fertile=False)],
                fertile=True,
                name=self._chomper.name())
            return FroParser(chomper, quiet=self._quiet).get()
        return -((+self).rstrip())

    def strip(self):
        return self.lstrip().rstrip()

    def unname(self):
        return FroParser(self._chomper.unname())

    def get(self):
        return self >> (lambda x: x)

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._chomper.fertile():
            return self
        return FroParser(chompers.util.DelegateChomper(
            self._chomper,
            fertile=False,
            name=self._chomper.name()))

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._chomper.fertile():
            return self
        return FroParser(chompers.util.DelegateChomper(
            self._chomper,
            fertile=True,
            name=self._chomper.name()))

    def __or__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            func,
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    def __rshift__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            lambda x: func(*x),
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    # internals

    def _failed_parse(self, state, tracker):
        error = tracker.retrieve_error()
        if error is not None:
            return self._raise(error)
        curr = state.current()
        col = state.column()
        msg = "Unexpected character {}".format(curr[col])
        return self._raise(parse_error.FroParseError(
            [chompers.chomp_error.ChompError(msg, state.location())]))

    def _raise(self, err):
        if self._quiet:
            return None
        raise err
