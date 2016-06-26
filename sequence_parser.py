import fro_parser
import fro_parser_utils

class SequenceFroParser(fro_parser.AbstractFroParser):

    def __init__(self, element, separator=None, at_start=False, at_end=False):
        fro_parser.AbstractFroParser.__init__(self)
        self._element = fro_parser_utils.parser_of(element)
        self._separator = fro_parser_utils.parser_of(separator) # may be None
        self._at_start = at_start and separator is not None
        self._at_end = at_end and separator is not None

    def _chomp(self, s, index, logger):
        rollback_index = index
        if self._at_start:
            chomp_result = self._separator._chomp(s, index, logger)
            if chomp_result is None:
                return None if self._at_end else [], rollback_index
            _, index = chomp_result

        encountered_values = []
        pending_value = None
        while True:
            chomp_result = self._element._chomp(s, index, logger)
            if chomp_result is None:
                return encountered_values, rollback_index
            value, index = chomp_result
            if self._at_end:
                pending_value = value
            else:
                rollback_index = index
                encountered_values.append(value)

            if self._separator is not None:
                chomp_result = self._separator._chomp(s, index, logger)
                if chomp_result is None:
                    return encountered_values, rollback_index
                _, index = chomp_result
                if self._at_end:
                    rollback_index = index
                    encountered_values.append(pending_value)
                    pending_value = None


