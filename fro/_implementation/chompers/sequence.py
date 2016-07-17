from fro._implementation import iters
from fro._implementation.chompers import abstract, chomp_error


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
        return value


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
            try:
                yield element.chomp(state, tracker)
                rollback_line = state.line()
                rollback_col = state.column()
            except chomp_error.ChompError as e:
                if state.line() != rollback_line:
                    self._failed_lookahead(state, tracker)
                tracker.report_error(e)
                state.reset_to(rollback_col)
                return

            if sep is not None:
                try:
                    sep.chomp(state, tracker)
                except chomp_error.ChompError as e:
                    if state.line() != rollback_line:
                        tracker.urgent()
                    tracker.report_error(e)
                    return
