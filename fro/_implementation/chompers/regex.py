import re

from fro._implementation.chompers.abstract import AbstractChomper


class GroupRegexChomper(AbstractChomper):

    def __init__(self, regex_str, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_str)

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            self._log_error(tracker, msg, index, self._next_index(s, index))
            return None
        return match.groups(), match.end()

class RegexChomper(AbstractChomper):

    def __init__(self, regex_string, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_string)

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            self._log_error(tracker, msg, index, self._next_index(s, index))
            return None
        start_index = index
        end_index = match.end()
        return s[start_index:end_index], end_index
