import re

from fro._implementation.chompers.abstract import AbstractChomper
from fro._implementation.chompers.regex import RegexChomper


class NestedChomper(AbstractChomper):

    def __init__(self, open_regex_string, close_regex_string, fertile=True,
                 name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._init_chomper = RegexChomper(open_regex_string)
        self._open_regex = re.compile(r".*?({})".format(open_regex_string))
        self._close_regex = re.compile(r".*?({})".format(close_regex_string))
        self._open_regex_string = open_regex_string
        self._close_regex_string = close_regex_string

    def _chomp(self, s, index, tracker):
        start_index = index
        chomp_result = self._init_chomper.chomp(s, index, tracker)
        if chomp_result is None:
            return None
        _, index = chomp_result
        start_inside_index = end_index = index
        nesting_level = 1
        while nesting_level > 0:
            open_match = self._open_regex.match(s, index)
            close_match = self._close_regex.match(s, index)
            if open_match is None and close_match is None:
                msg = "No closing {} to match opening {}"\
                    .format(self._open_regex_string, self._close_regex_string)
                end_index = re.compile(r".*").match(s, index).end()
                self._log_error(tracker, msg, start_index, end_index)
                return None
            elif open_match is None:
                match = close_match
                nesting_level -= 1
            elif close_match is None:
                match = open_match
                nesting_level += 1
            elif close_match.end() < open_match.end():
                match = close_match
                nesting_level -= 1
            else:
                match = open_match
                nesting_level += 1
            end_index = match.start(1)
            index = match.end()
        return s[start_inside_index:end_index], index
