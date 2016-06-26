import re

from fro_parser import AbstractFroParser


class NestedFroParser(AbstractFroParser):

    def __init__(self, open_regex_string, close_regex_string):
        AbstractFroParser.__init__(self)
        self._init_regex = re.compile(open_regex_string)
        self._open_regex = re.compile(r".*?({})".format(open_regex_string))
        self._close_regex = re.compile(r".*?({})".format(close_regex_string))
        self._open_regex_string = open_regex_string
        self._close_regex_string = close_regex_string

    def _chomp(self, s, index, logger):
        start_index = index
        init_match = self._init_regex.match(s, index)
        if init_match is None:
            return None
        start_inside_index = index = init_match.end()
        nesting_level = 1
        while nesting_level > 0:
            open_match = self._open_regex.match(s, index)
            close_match = self._close_regex.match(s, index)
            if open_match is None and close_match is None:
                msg = "No closing {} to match opening {}"\
                    .format(self._open_regex_string, self._close_regex_string)
                self._log_error(logger, msg, start_index, len(s))
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
