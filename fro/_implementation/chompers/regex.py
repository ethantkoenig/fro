import re

from fro._implementation.chompers.abstract import AbstractChomper
from fro._implementation.chompers.chomp_error import ChompError
from fro._implementation.chompers.box import Box

class GroupRegexChomper(AbstractChomper):

    def __init__(self, regex_str, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        self._regex = re.compile(regex_str)

    def _chomp(self, state, tracker):
        match = regex_chomp(self._regex, state, tracker)
        if match is None:
            return None
        state.advance_to(match.end())
        return Box(match.groups())


class RegexChomper(AbstractChomper):

    def __init__(self, regex_string, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        self._regex = re.compile(regex_string)

    def _chomp(self, state, tracker):
        col = state.column()
        line = state.current()
        match = regex_chomp(self._regex, state, tracker)
        if match is None:
            return None
        start_index = col
        end_index = match.end()
        state.advance_to(end_index)
        return Box(line[start_index:end_index])


def regex_chomp(regex, state, tracker):
    """
    :param regex: regex object to match with
    :param state: ChompState
    :param tracker: FroParseErrorTracker
    :return: Match object of regex match, or throws ChompError
    """
    line = state.current()
    index = state.column()
    match = regex.match(line, index)
    if match is None:
        msg = "Expected pattern \'{}\'".format(regex.pattern)
        chomp_err = ChompError(msg, state.location(), tracker.current_name())
        tracker.report_error(chomp_err)
    return match
