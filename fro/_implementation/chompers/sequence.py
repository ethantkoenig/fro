from fro._implementation import iters
from fro._implementation.chompers import abstract
from fro._implementation.chompers.box import Box

class SequenceChomper(abstract.AbstractChomper):

    def __init__(self, element, reducer, separator=None,
                 fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._element = element
        self._reducer = reducer
        self._separator = separator  # self._separator may be None

    def _chomp(self, state, tracker):
        iterable = SequenceIterable(self, state, tracker)
        iterator = iter(iterable)
        value = self._reducer(iterator)
        iters.close(iterator)
        return Box(value)


class SequenceIterable(object):
    def __init__(self, chomper, state, tracker):
        self._state = state
        self._element = chomper._element
        self._sep = chomper._separator  # may be None
        self._tracker = tracker
        self._failed_lookahead = chomper._failed_lookahead

    def __iter__(self):
        state = self._state
        element = self._element
        tracker = self._tracker
        sep = self._sep

        rollback_line = state.line()
        rollback_col = state.column()
        while True:
            box = element.chomp(state, tracker)
            if box is None:
                if state.line() != rollback_line:
                    self._failed_lookahead(state, tracker)
                state.reset_to(rollback_col)
                return
            yield box.value
            rollback_line = state.line()
            rollback_col = state.column()

            if sep is not None:
                box_ = sep.chomp(state, tracker)
                if box_ is None:
                    if state.line() != rollback_line:
                        self._failed_lookahead(state, tracker)
                    state.reset_to(rollback_col)
                    return
