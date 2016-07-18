import re

from fro._implementation import iters
from fro._implementation.chompers.abstract import AbstractChomper
from fro._implementation.chompers.box import Box


class UntilChomper(AbstractChomper):
    def __init__(self, regex_str, reducer, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile=fertile, name=name)
        self._regex = re.compile(regex_str)
        self._reducer = reducer

    def _chomp(self, state, tracker):
        iterable = UntilIterable(self._regex, state, tracker)
        iterator = iter(iterable)
        value = self._reducer(iterator)
        iters.close(iterator)
        return Box(value)


class UntilIterable(object):
    def __init__(self, regex, state, tracker):
        self._regex = regex
        self._state = state
        self._tracker = tracker

    def __iter__(self):
        regex = self._regex
        state = self._state
        tracker = self._tracker

        start_index = state.column()

        while not state.at_end():
            curr = state.current()
            col = state.column()
            match = regex.search(curr, col)
            if match is not None:
                end_index = match.start()
                state.advance_to(end_index)
                yield curr[start_index:end_index]
                return
            yield curr[start_index:]
            state.advance_to(len(curr))
            start_index = 0
