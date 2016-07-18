from fro._implementation.chompers.abstract import AbstractChomper


class CompositionChomper(AbstractChomper):

    def __init__(self, chompers, separator=None, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        self._chompers = list(chompers)
        self._separator = separator  # self._separator may be None

    def _chomp(self, state, tracker):
        values = []
        length = len(self._chompers)
        for i, chomper in enumerate(self._chompers):
            box_ = chomper.chomp(state, tracker)
            if box_ is None:
                return None
            if chomper._fertile:
                values.append(box_.value)
            if i == length - 1:
                box_.value = tuple(values)
                return box_
            elif self._separator is not None:
                if self._separator.chomp(state, tracker) is None:
                    return None
        raise AssertionError()
