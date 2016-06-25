import re

import fro_parser

class GroupRegexFroParser(fro_parser.AbstractFroParser):

    def __init__(self, regex_str, reduce = lambda *x: x):
        fro_parser.AbstractFroParser.__init__(self)
        self._regex = re.compile(regex_str)
        self._reduce = reduce

    def _chomp(self, s, index, fail_hard):
        match = self._regex.match(s, index)
        if match is None:
            return self._quit(self, index, fail_hard)
        return reduce(*match.groups()), match.end()
