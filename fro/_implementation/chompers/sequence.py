from fro._implementation.chompers.abstract import AbstractChomper


class SequenceChomper(AbstractChomper):

    def __init__(self, element, separator=None, at_start=False, at_end=False,
                 fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._element = element
        self._separator = separator  # self._separator may be None
        self._at_start = at_start and separator is not None
        self._at_end = at_end and separator is not None

    def _chomp(self, s, index, tracker):
        rollback_index = index
        if self._at_start:
            chomp_result = self._separator.chomp(s, index, tracker)
            if chomp_result is None:
                return None if self._at_end else [], rollback_index
            _, index = chomp_result

        encountered_values = []
        pending_value = None
        while True:
            chomp_result = self._element.chomp(s, index, tracker)
            if chomp_result is None:
                return encountered_values, rollback_index
            value, index = chomp_result
            if self._at_end:
                pending_value = value
            else:
                rollback_index = index
                encountered_values.append(value)

            if self._separator is not None:
                chomp_result = self._separator.chomp(s, index, tracker)
                if chomp_result is None:
                    return encountered_values, rollback_index
                _, index = chomp_result
                if self._at_end:
                    rollback_index = index
                    encountered_values.append(pending_value)
                    pending_value = None
