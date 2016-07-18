from fro._implementation.chompers import abstract
from fro._implementation.chompers.box import Box


class DelegateChomper(abstract.AbstractChomper):
    def __init__(self, delegate, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._delegate = delegate

    def _chomp(self, state, tracker):
        return self._delegate.chomp(state, tracker)


class DependentChomper(abstract.AbstractChomper):
    def __init__(self, dependee, chomper_func, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile=fertile, name=name)
        self._dependee = dependee
        self._chomper_func = chomper_func

    def _chomp(self, state, tracker):
        chomper = self._chomper_func(self._dependee.last_parsed())
        return chomper.chomp(state, tracker)


class LazyChomper(abstract.AbstractChomper):
    def __init__(self, func, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile=fertile, name=name)
        self._generation_func = func
        self._chomper = None

    def _chomp(self, state, tracker):
        if self._chomper is None:
            lazier = LazyChomper(self._generation_func, fertile=self._fertile, name=self._name)
            self._chomper = self._generation_func(lazier)
        return self._chomper.chomp(state, tracker)


class OptionalChomper(abstract.AbstractChomper):
    def __init__(self, child, default=None, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._child = child
        self._default = default

    def _chomp(self, state, tracker):
        line = state.line()
        col = state.column()
        box = self._child.chomp(state, tracker)
        if box is not None:
            return box
        elif state.line() != line:
            self._failed_lookahead(state, tracker)
        state.reset_to(col)
        return Box(self._default)


class StubChomper(abstract.AbstractChomper):
    def __init__(self, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._delegate = None

    def set_delegate(self, delegate):
        if self._delegate is not None:
            raise AssertionError("Cannot set a stub's delegate twice")
        self._delegate = delegate

    def _chomp(self, state, tracker):
        if self._delegate is None:
            raise ValueError("Stub chomper has no delegate")
        return self._delegate.chomp(state, tracker)
