from fro._implementation import pretty_printing


class FroParseError(Exception):
    """
    An exception for parsing failures
    """
    def __init__(self, chomp_errors, cause=None):
        self._messages = [_message_of_chomp_error(ce) for ce in chomp_errors]
        self._location = chomp_errors[0].location()
        self._cause = cause

    def __str__(self):
        """
        A human readable description of the error. Include both the error messages, and extra information describing the
        location of the error. Equivalent to ``to_str()``.

        :return: a human readable description
        :rtype: str
        """
        return self.to_str(index_from=1)

    def cause(self):
        """
        Returns the ``Exception`` that triggered this error, or ``None`` is this error was not triggered by another
        exception

        :return: the exception that triggered this error
        :rtype: Exception
        """
        return self._cause

    def context(self):
        return pretty_printing.printable_string_index_with_context(
                self._location.text(),
                self.column(0))

    def column(self, index_from=1):
        """
        Returns the column number where the error occurred, or more generally the
        index inside the chunk where the error occurred. Indices are indexed from
        ``index_from``.

        :param int index_from: number to index column numbers by
        :return: column number of error
        :rtype: int
        """
        return self._location.column() + index_from

    def line(self, index_from=1):
        """
        Returns the line number where the error occurred, or more generally
        the index of the chunk where the error occurred. Indices are indexed from
        ``index_from``.

        :param int index_from: number to index line numbers by
        :return: row number of error
        :rtype: int
        """
        return self._location.line() + index_from

    def messages(self):
        """
        A non-empty list of ``Message`` objects which describe the reasons for failure.
        :return: a non-empty list of ``Message`` objects which describe the reasons for failure.
        :rtype: List[FroParseError.Message]
        """
        return list(self._messages)

    def to_str(self, index_from=1, filename=None):
        """
        Returns a readable description of the error, with indices starting at ``index_from``, and a
        filename of ``filename`` include if a filename is provided. Include both the error messages,
        and extra information describing the location of the error. This method is essentially a
        configurable version of ``__str__()``.

        :param int index_from: number to index column/line numbers by
        :param str filename: name of file whose parse trigger the exception
        :return: a readable description of the error
        :rtype: str
        """
        first_line = "At line {l}, column {c}".format(
            l=self.line(index_from),
            c=self.column(index_from))
        if filename is not None:
            first_line += " of " + filename

        result = "\n".join([
            first_line,
            "\n".join(str(x) for x in self._messages),
            self.context()])

        if self._cause is not None:
            result += "\n\nCaused by: " + str(self._cause)

        return result

    class Message(object):
        """
        Represents an error message describing a reason for failure
        """

        def __init__(self, content, name=None):
            self._content = content
            self._name = name

        def __str__(self):
            """
            A string representation of the message that includes both the content and parser name.
            :return:
            """
            if self._name is None:
                return self._content
            return "{0} when parsing {1}".format(self._content, self._name)

        def content(self):
            """
            The content of the error message

            :return: the content of the error message
            :rtype: str
            """
            return self._content

        def name(self):
            """
            The name of the parser at which the message was generated, or ``None`` if all relevant parsers are unnamed.
            :return: name of parser where error occurred
            :rtype: str
            """
            return self._name


# ----------------------------- internals

def _message_of_chomp_error(chomp_error):
    return FroParseError.Message(chomp_error.message(), chomp_error.name())
