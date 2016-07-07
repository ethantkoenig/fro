from fro._implementation import pretty_printing


class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, string, messages, start_index, end_index=None, cause=None):
        """
        :param string: string being parsed
        :param messages: non-empty list of Message objects
        :param start_index: beginning index of substring causing error
        :param end_index: end index of substring causing error
        :param cause: Exception that triggered this exception
        """
        self._string = string
        self._messages = messages
        self._start_index = start_index
        if end_index is None:
            self._end_index = min(start_index + 1, len(string))
        else:
            self._end_index = end_index
        self._cause = cause

    def __str__(self):
        return "\n".join([
            "At indices {0} to {1}".format(self._start_index, self._end_index),
            "\n".join(str(x) for x in self._messages),
            self.context()])

    def cause(self):
        return self._cause

    def context(self):
        return pretty_printing.printable_substring_with_context(
                self._string,
                self._start_index,
                self._end_index)

    def end_index(self):
        return self._end_index

    def messages(self):
        return list(self._messages)

    def start_index(self):
        return self._start_index

    class Message(object):
        def __init__(self, content, name=None):
            self._content = content
            self._name = name

        def __str__(self):
            if self._name is None:
                return self._content
            return "{0} when parsing {1}".format(self._content, self._name)

        def content(self):
            return self._content

        def name(self):
            return self._name

