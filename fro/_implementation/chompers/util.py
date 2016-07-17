from fro._implementation.chompers import abstract, chomp_error


class DelegateChomper(abstract.AbstractChomper):
    """
    Fro parser that delegates parsing to another parser
    """
    def __init__(self, delegate, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._delegate = delegate

    def _chomp(self, state, tracker):
        return self._delegate.chomp(state, tracker)


class DependentChomper(abstract.AbstractChomper):

    def __init__(self, dependee, chomper_func, name=None, fertile=True):
        abstract.AbstractChomper.__init__(self, name=name, fertile=fertile)
        self._dependee = dependee
        self._chomper_func = chomper_func

    def _chomp(self, state, tracker):
        chomper = self._chomper_func(self._dependee.last_parsed())
        return chomper.chomp(state, tracker)


class MapChomper(abstract.AbstractChomper):
    """
    Fro parser that performs map operation on parsed values
    """
    def __init__(self, parser, func, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._parser = parser
        self._func = func

    def _chomp(self, state, tracker):
        value = self._parser.chomp(state, tracker)
        return abstract.AbstractChomper._apply(tracker, state, self._func, value)


class OptionalChomper(abstract.AbstractChomper):
    def __init__(self, child, default=None, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._child = child
        self._default = default

    def _chomp(self, state, tracker):
        line = state.line()
        col = state.column()
        try:
            result = self._child.chomp(state, tracker)
            return result
        except chomp_error.ChompError as e:
            if state.line() != line:
                self._failed_lookahead(state, tracker)
            tracker.report_error(e)
        state.reset_to(col)
        return self._default


class StubChomper(abstract.AbstractChomper):
    def __init__(self, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._delegate = None

    def set_delegate(self, delegate):
        if self._delegate is not None:
            raise AssertionError("cannot set a stub's delegate twice")
        self._delegate = delegate

    def _chomp(self, state, tracker):
        if self._delegate is None:
            raise ValueError("Stub chomper has no delegate")
        return self._delegate._chomp(state, tracker)
