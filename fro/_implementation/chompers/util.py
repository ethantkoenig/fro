from fro._implementation.chompers.abstract import AbstractChomper


class DelegateChomper(AbstractChomper):
    """
    Fro parser that delegates parsing to another parser
    """
    def __init__(self, delegate, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._delegate = delegate

    def _chomp(self, s, index, tracker):
        return self._delegate.chomp(s, index, tracker)


class MapChomper(AbstractChomper):
    """
    Fro parser that performs map operation on parsed values
    """
    def __init__(self, parser, func, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, tracker):
        start_index = index
        chomp_result = self._parser.chomp(s, index, tracker)
        if chomp_result is None:
            return None
        value, index = chomp_result
        return AbstractChomper._apply(tracker, start_index, index, self._func, value), index


class OptionalChomper(AbstractChomper):
    def __init__(self, child, default=None, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._child = child
        self._default = default

    def _chomp(self, s, index, tracker):
        child_result = self._child.chomp(s, index, tracker)
        if child_result is not None:
            return child_result
        return self._default, index
