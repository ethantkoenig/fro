
class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, message, start_index, end_index=None, cause=None):
        """
        :param message: description of error
        :param start_index: beginning index of problematic region
        :param end_index: end index of problematic region
        :param cause: Exception that triggered this exception.
        """
        self._message = message
        self._start_index = start_index
        self._end_index = end_index if end_index is not None else start_index + 1
        self._cause = cause

    def __str__(self):
        return self._message

    def cause(self):
        return self._cause

    def start_index(self):
        return self._start_index

    def end_index(self):
        return self._end_index
