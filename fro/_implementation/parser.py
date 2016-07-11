from fro._implementation import chompers, iters, parse_error


class FroParser(object):
    """
    An immutable parser
    """
    def __init__(self, chomper):
        self._chomper = chomper

    # public interface

    def parse(self, lines):
        """
        Parses the string into an object
        :param string_to_parse: string to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        tracker = chompers.abstract.FroParseErrorTracker()
        state = chompers.state.ChompState(iters.Stream(lines))
        success = True
        try:
            value = self._chomper.chomp(state, tracker)
        except chompers.chomp_error.ChompError as e:
            tracker.report_error(e)
            success = False
        success = success and state.at_end()
        if not success:
            error = tracker.retrieve_error()
            if error is not None:
                return self._raise(error)
            curr = state.current()
            col = state.column()
            msg = "Unexpected character {}".format(curr[col])
            return self._raise(parse_error.FroParseError(
                [chompers.chomp_error.ChompError(msg, state.location())]))
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
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def quiet(self):
        return FroParser(self._chomper.clone(quiet=True))

    def loud(self):
        return FroParser(self._chomper.clone(quiet=False))

    def lstrip(self):
        if self._chomper.fertile():
            return FroParser(chompers.composition.CompositionChomper(
                [chompers.regex.RegexChomper(r"\s*", fertile=False), self._chomper],
                fertile=True,
                name=self._chomper.name(),
                quiet=self._chomper.quiet())).get()
        return -((+self).lstrip())

    def rstrip(self):
        if self._chomper.fertile():
            return FroParser(chompers.composition.CompositionChomper(
                [self._chomper, chompers.regex.RegexChomper(r"\s*", fertile=False)],
                fertile=True,
                name=self._chomper.name(),
                quiet=self._chomper.quiet())).get()
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
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._chomper.fertile():
            return self
        return FroParser(chompers.util.DelegateChomper(
            self._chomper,
            fertile=True,
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __or__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            func,
            fertile=self._chomper.fertile(),
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    def __rshift__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            lambda x: func(*x),
            fertile=self._chomper.fertile(),
            name=self._chomper.name(),
            quiet=self._chomper.quiet()))

    # internals

    def _raise(self, err):
        if self._chomper.quiet():
            return None
        raise err
