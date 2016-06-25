import re

import fro_parser

class GroupRegexFroParser(fro_parser.AbstractFroParser):

    def __init__(self, regex_str, func=lambda *x: x):
        fro_parser.AbstractFroParser.__init__(self)
        self._regex = re.compile(regex_str)
        self._func = func

    def _chomp(self, s, index, fail_hard):
        match = self._regex.match(s, index)
        if match is None:
            return self._quit(index, fail_hard)
        return self._func(*match.groups()), match.end()
