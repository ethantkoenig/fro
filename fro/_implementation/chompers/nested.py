import re

from fro._implementation import iters, parse_error
from fro._implementation.chompers import abstract, chomp_error


class NestedChomper(abstract.AbstractChomper):
    def __init__(self, open_regex_string, close_regex_func, reducer,
                 fertile=True, name=None, quiet=False):
        abstract.AbstractChomper.__init__(self, fertile, name, quiet)
        self._open_regex = re.compile(open_regex_string)
        self._close_regex_func = close_regex_func
        self._reducer = reducer

    def _chomp(self, state, tracker):
        curr = state.current()
        col = state.column()
        match = self._open_regex.match(curr, col)
        if match is None:
            return None
        close_regex = self._close_regex_func(match.group())
        err = self._err(
            self._open_regex.pattern,
            close_regex.pattern,
            state.location(),
            tracker.current_name())
        state.advance_to(match.end())
        iterable = NestedIterable(state, self._open_regex, close_regex,
                                  lambda: self._raise(err))
        iterator = iter(iterable)
        value = self._apply(tracker, state, self._reducer, iterator)
        iters.close(iterator)
        return value

    @staticmethod
    def _err(open_str, close_str, location, name):
        msg = "No closing {c} to match opening {o}".format(
            c=close_str, o=open_str)
        err = chomp_error.ChompError(msg, location, name)
        return parse_error.FroParseError([err])

    @staticmethod
    def _raise(err):
        raise err


class NestedIterable(object):
    def __init__(self, state, open_regex, close_regex, failure_callback):
        self._state = state
        self._open_regex = open_regex
        self._close_regex = close_regex
        self._failure_callback = failure_callback

    def __iter__(self):
        start_index = self._state.column()
        nesting_level = 1
        while nesting_level > 0:
            current = self._state.current()
            sentinel = self.sentinel(current)
            open_start, open_end = self.match_indices(self._open_regex)
            close_start, close_end = self.match_indices(self._close_regex)
            if open_start == sentinel and close_start == sentinel:
                yield current[start_index:]
                self._state.advance_to(len(current))
                start_index = 0
                if self._state.at_end():
                    self._failure_callback()
            elif close_start < open_start:
                nesting_level -= 1
                if nesting_level == 0:
                    yield self._state.current()[start_index:close_start]
                self._state.advance_to(close_end)
            else:
                nesting_level += 1
                self._state.advance_to(open_end)

    def match_indices(self, regex):
        curr = self._state.current()
        match = regex.search(curr, self._state.column())
        if match is None:
            sentinel = NestedIterable.sentinel(curr)
            return sentinel, sentinel
        return match.start(), match.end()

    @staticmethod
    def sentinel(row):
        return len(row) + 1
