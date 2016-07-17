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
        rollback_line = self._state.line()
        rollback_col = self._state.column()
        while True:
            try:
                yield self._element.chomp(self._state, self._tracker)
                rollback_line = self._state.line()
                rollback_col = self._state.column()
            except chomp_error.ChompError as e:
                if self._state.line() != rollback_line:
                    self._failed_lookahead()
                self._tracker.report_error(e)
                self._state.reset_to(rollback_col)
                return

            if self._sep is not None:
                try:
                    self._sep.chomp(self._state, self._tracker)
                except chomp_error.ChompError as e:
                    if self._state.line() != rollback_line:
                        self._tracker.urgent()
                    self._tracker.report_error(e)
                    return
