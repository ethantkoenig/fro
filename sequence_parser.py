import fro_parser
import fro_parser_utils

class SequenceFroParser(fro_parser.AbstractFroParser):

    def __init__(self, values, separator=None, start=None, end=None):
        fro_parser.AbstractFroParser.__init__(self)
        self.values = fro_parser_utils.parser_of(values)
        self.separator = fro_parser_utils.parser_of(separator) # may be None
        self.start = fro_parser_utils.parser_of(start) # may be None
        self.end = fro_parser_utils.parser_of(end) # may be None

    def _chomp(self, s, index, fail_hard):
        start_index = index
        if self.start is not None:
            chomp_result = self.start._chomp(s, index, False)
            if chomp_result is None:
                return [], index
            _, index = chomp_result

        encountered_values = []
        chomp_result = self.values._chomp(s, index, False)
        if chomp_result is None:
            return [], start_index
        value, index = chomp_result
        encountered_values.append(value)
        while True:
            rollback_index = index
            if self.separator is not None:
                chomp_result = self.separator._chomp(s, index, False)
                if chomp_result is None:
                    break
                _, index = chomp_result

            chomp_result = self.values._chomp(s, index, False)
            if chomp_result is None:
                index = rollback_index
                break
            value, index = chomp_result
            encountered_values.append(value)

        if self.end is not None:
            chomp_result = self.end._chomp(s, index, False)
            if chomp_result is None:
                return [], start_index
            _, index = chomp_result
        return encountered_values, index
