import re

import fro_parser


class RegexFroParser(fro_parser.AbstractFroParser):

    def __init__(self, regex_string, func=lambda x: x):
        fertile = True
        if regex_string[0:1] == "@":
            fertile = False
            regex_string = regex_string[1:]
        elif regex_string[0:2] == "\\@":
            regex_string = "@"+regex_string[2:]
        fro_parser.AbstractFroParser.__init__(self, fertile)
        self._regex = re.compile(regex_string)
        self._func = func

    def _chomp(self, s, index, logger):
        match = self._regex.match(s, index)
        if match is None:
            self._log_error(logger, "Expected pattern {}".format(self._regex.pattern), index)
            return None
        start_index = index
        end_index = match.end()
        if end_index < len(s):
            self._log_error(logger, "Unexpected character", end_index)
        elif end_index > len(s):
            raise AssertionError("Invalid index")
        matched = s[start_index:end_index]
        value = fro_parser.AbstractFroParser._apply(start_index, end_index, self._func, matched)
        return value, end_index
