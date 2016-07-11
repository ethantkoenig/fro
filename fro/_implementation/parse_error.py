from fro._implementation import pretty_printing


class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, chomp_errors, cause=None, filename=None):
        """
        :param string: string being parsed
        :param messages: non-empty list of Message objects
        :param start_index: beginning index of substring causing error
        :param end_index: end index of substring causing error
        :param cause: Exception that triggered this exception
        """
        self._messages = [_message_of_chomp_error(ce) for ce in chomp_errors]
        self._location = chomp_errors[0].location()
        self._cause = cause
        self._filename = filename

    def __str__(self, index_from=1):
        first_line = "At line {l}, column {c}".format(
            l=self.line(index_from),
            c=self.column(index_from))
        if self._filename is not None:
            first_line += " of " + self._filename

        return "\n".join([
            first_line,
            "\n".join(str(x) for x in self._messages),
            self.context()])

    def cause(self):
        return self._cause

    def context(self):
        return pretty_printing.printable_string_index_with_context(
                self._location.text(),
                self.line(0))

    def column(self, index_from=1):
        return self._location.column() + index_from

    def filename(self):
        return self._filename

    def line(self, index_from=1):
        return self._location.line() + index_from

    def messages(self):
        return list(self._messages)


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


# ----------------------------- internals

def _message_of_chomp_error(chomp_error):
    return Message(chomp_error.message(), chomp_error.name())