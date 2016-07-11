import re

from fro._implementation.chompers.abstract import AbstractChomper
from fro._implementation.chompers.chomp_error import ChompError

class GroupRegexChomper(AbstractChomper):

    def __init__(self, regex_str, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_str)

    def _chomp(self, state, tracker):
        col = state.column()
        line = state.current()
        match = self._regex.match(line, col)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            raise ChompError(msg, state.location(), tracker.current_name())
        state.advance_to(match.end())
        return match.groups()

class RegexChomper(AbstractChomper):

    def __init__(self, regex_string, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_string)

    def _chomp(self, state, tracker):
        col = state.column()
        line = state.current()
        match = self._regex.match(line, col)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            raise ChompError(msg, state.location(), tracker.current_name())
        start_index = col
        end_index = match.end()
        state.advance_to(end_index)
        return line[start_index:end_index]
