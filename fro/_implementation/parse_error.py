from fro._implementation import pretty_printing

class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, string, message, start_index, end_index=None, cause=None):
        """
        :param string: string being parsed
        :param message: description of error
        :param start_index: beginning index of problematic region
        :param end_index: end index of problematic region
        :param cause: Exception that triggered this exception.
        """
        self._string = string
        self._message = message
        self._start_index = start_index
        self._end_index = end_index if end_index is not None else start_index + 1
        self._cause = cause

    def __str__(self):
        try: # TODO
            first_line = "{m} at indices {s} to {e}".format(
                m=self._message,
                s=self._start_index,
                e=self._end_index)
            printable = pretty_printing.PrintableString(self._string)
            second_line = "Substring:" + printable.substring(
                self._start_index,
                self._end_index,
                max_length=70)
            context_start = max(0, self._start_index - 15)
            context_end = min(len(self._string), self._end_index + 15)
            third_line = "Context  :" + printable.substring(
                context_start,
                context_end,
                max_length=70)
            return "\n".join([first_line, second_line, third_line])
        except Exception as e:
            print(str(e))
    def cause(self):
        return self._cause

    def end_index(self):
        return self._end_index

    def message(self):
        return self._message

    def start_index(self):
        return self._start_index
