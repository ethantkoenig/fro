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

    # This class is a hotspot, since it is the "base case" for nearly every other
    # type of chomper. For that reason, this class is implemented for efficiency.

    def __init__(self, regex_string, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        regex = re.compile(regex_string)
        self._match = regex.match
        self._pattern = regex.pattern

    def _chomp(self, state, tracker):
        col = state._column  # state.column()
        line = state._curr  # state.current()
        match = self._match(line, col)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._pattern)
            chomp_err = ChompError(msg, state.location(), tracker.current_name())
            tracker.report_error(chomp_err)
            return None
        end_index = match.end()
        state.advance_to(end_index)
        return Box(line[col:end_index])


def regex_chomp(regex, state, tracker):
    """
    :param regex: regex object to match with
    :param state: ChompState
    :param tracker: FroParseErrorTracker
    :return: Match object of regex match, or throws ChompError
    """
    line = state._curr # state.current()
    index = state._column # state.column()
    match = regex.match(line, index)
    if match is None:
        msg = "Expected pattern \'{}\'".format(regex.pattern)
        chomp_err = ChompError(msg, state.location(), tracker.current_name())
        tracker.report_error(chomp_err)
    return match
