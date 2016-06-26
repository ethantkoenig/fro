import re

import fro_parser


class GroupRegexFroParser(fro_parser.AbstractFroParser):

    def __init__(self, regex_str, func=lambda *x: x):
        fro_parser.AbstractFroParser.__init__(self)
        self._regex = re.compile(regex_str)
        self._func = func

    def _chomp(self, s, index, logger):
        match = self._regex.match(s, index)
        if match is None:
            self._log_error(logger, "Expected pattern {}".format(self._regex.pattern), index)
            return None
        end_index = match.end()
        value = fro_parser.AbstractFroParser._apply(index, end_index, self._func, *match.groups())
        return value, end_index
