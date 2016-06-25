import re

import fro_parser


class RegexFroParser(fro_parser.AbstractFroParser):

    def __init__(self, regex_string, func=None):
        fertile = True
        if regex_string[0:1] == "@":
            fertile = False
            regex_string = regex_string[1:]
        elif regex_string[0:2] == "\\@":
            regex_string = "@"+regex_string[2:]
        fro_parser.AbstractFroParser.__init__(self, fertile)
        self._regex = re.compile(regex_string)
        self._func = func

    def _chomp(self, s, index, fail_hard):
        match = self._regex.match(s, index)
        if match is None:
            return self._quit(index, fail_hard)
        start_index = index
        end_index = match.end()
        matched = s[start_index:end_index]
        value = matched if self._func is None else self._func(matched)
        return value, end_index
