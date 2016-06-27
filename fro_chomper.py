import re

import fro_parse_error


class AbstractChomper(object):
    """
    The abstract parent class which chompers should extend. This class should
    not be instantiated, but instead subclassed.

    Every subclass should be immutable (at least from the client's perspective).
    Also, every subclass should be implemented in such a way that no action
    performed on a chomper could alter a shallow copy.
    """
    def __init__(self, fertile=True, name=None, quiet=False):
        """
        :param fertile: if the parser produces a meaningful value
        :param name: name of parser, for error messages
        """
        self._fertile = fertile
        self._name = name
        self._quiet = quiet

    # internals
    @staticmethod
    def _apply(start_index, end_index, func, *args):
        """
        Convenience match to apply function while gracefully handling errors
        :param start_index: start index of relevant region
        :param end_index: end index of relevant region
        :param func: function
        :param args: arguments
        :return: result of function application
        """
        try:
            return func(*args)
        except StandardError as e:
            raise fro_parse_error.FroParseError(str(e), start_index, end_index, e)

    def _log_error(self, tracker, base_msg, start_index, end_index=None):
        """
        Convenience method to add a parse error to the tracker
        :return:
        """
        end_index = start_index + 1 if end_index is None else end_index
        msg = base_msg if self._name is None else "{} when parsing {}".format(base_msg, self._name)
        tracker.report_error(fro_parse_error.FroParseError(msg, start_index, end_index))

    def _chomp(self, s, index, tracker):
        """
        Parses the head of the string s, possibly "chomping" off the beginnig
        of s and producing a value
        :param s: string to parse
        :param index: index of s to start at
        :param tracker: FroParseErrorTracker - tracks encountered errors
        :return: (t, index) : value parsed, and first "unconsumed" index
        """
        return None  # must be implemented by subclasses


class FroParseErrorTracker(object):

    def __init__(self):
        self._error = None

    def report_error(self, error):
        if self._error is None or error.end_index() >= self._error.end_index():
            self._error = error

    def retrieve_error(self):
        return self._error


def chomper_of(x):
    """
    :param x: value representing a fro parser
    :return: fro_parser.AbstractFroParser - the parser represented by x
    """
    if x is None:
        return None
    elif isinstance(x, AbstractChomper):
        return x
    elif isinstance(x, str):
        return RegexChomper(x)
    else:
        raise ValueError("{} does not represent a parser".format(x))


# Chomper subclasses

class CompositionChomper(AbstractChomper):

    def __init__(self, parsers, separator=None, reducer=lambda *x: x):
        AbstractChomper.__init__(self)
        self._parsers = [chomper_of(x) for x in parsers]
        self._separator = chomper_of(separator)  # may be None
        self._reducer = reducer

    def _chomp(self, s, index, tracker):
        start_index = index
        values = []
        for i, parser in enumerate(self._parsers):
            chomp_result = parser._chomp(s, index, tracker)
            if chomp_result is None:
                return None
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
            if i < len(self._parsers) - 1 and self._separator is not None:
                chomp_result = self._separator._chomp(s, index, tracker)
                if chomp_result is None:
                    return None
                _, index = chomp_result
        value = AbstractChomper._apply(start_index, index, self._reducer, *values)
        return value, index


class DelegateChomper(AbstractChomper):
    """
    Fro parser that delegates parsing to another parser
    """
    def __init__(self, delegate, fertile, name, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._delegate = delegate

    def _chomp(self, s, index, tracker):
        return self._delegate._chomp(s, index, tracker)


class GroupRegexChomper(AbstractChomper):

    def __init__(self, regex_str, func=lambda *x: x):
        AbstractChomper.__init__(self)
        self._regex = re.compile(regex_str)
        self._func = func

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            self._log_error(tracker, "Expected pattern {}".format(self._regex.pattern), index)
            return None
        end_index = match.end()
        value = AbstractChomper._apply(index, end_index, self._func, *match.groups())
        return value, end_index


class NestedChomper(AbstractChomper):

    def __init__(self, open_regex_string, close_regex_string):
        AbstractChomper.__init__(self)
        self._init_regex = re.compile(open_regex_string)
        self._open_regex = re.compile(r".*?({})".format(open_regex_string))
        self._close_regex = re.compile(r".*?({})".format(close_regex_string))
        self._open_regex_string = open_regex_string
        self._close_regex_string = close_regex_string

    def _chomp(self, s, index, tracker):
        start_index = index
        init_match = self._init_regex.match(s, index)
        if init_match is None:
            return None
        start_inside_index = index = init_match.end()
        nesting_level = 1
        while nesting_level > 0:
            open_match = self._open_regex.match(s, index)
            close_match = self._close_regex.match(s, index)
            if open_match is None and close_match is None:
                msg = "No closing {} to match opening {}"\
                    .format(self._open_regex_string, self._close_regex_string)
                end_index = re.compile(r".*").match(s, index).end()
                self._log_error(tracker, msg, start_index, end_index)
                return None
            elif open_match is None:
                match = close_match
                nesting_level -= 1
            elif close_match is None:
                match = open_match
                nesting_level += 1
            elif close_match.end() < open_match.end():
                match = close_match
                nesting_level -= 1
            else:
                match = open_match
                nesting_level += 1
            end_index = match.start(1)
            index = match.end()
        return s[start_inside_index:end_index], index


class MapChomper(AbstractChomper):
    """
    Fro parser that performs map operation on parsed values
    """
    def __init__(self, parser, func):
        AbstractChomper.__init__(self)
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, tracker):
        chomp_result = self._parser._chomp(s, index, tracker)
        if chomp_result is None:
            return None
        value, index = chomp_result
        return self._func(value), index


class RegexChomper(AbstractChomper):

    def __init__(self, regex_string, func=lambda x: x):
        fertile = True
        if regex_string[0:1] == "@":
            fertile = False
            regex_string = regex_string[1:]
        elif regex_string[0:2] == "\\@":
            regex_string = "@"+regex_string[2:]
        AbstractChomper.__init__(self, fertile)
        self._regex = re.compile(regex_string)
        self._func = func

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            self._log_error(tracker, "Expected pattern {}".format(self._regex.pattern), index)
            return None
        start_index = index
        end_index = match.end()
        if end_index < len(s):
            self._log_error(tracker, "Unexpected character", end_index)
        elif end_index > len(s):
            raise AssertionError("Invalid index")
        matched = s[start_index:end_index]
        value = AbstractChomper._apply(start_index, end_index, self._func, matched)
        return value, end_index


class SequenceChomper(AbstractChomper):

    def __init__(self, element, separator=None, at_start=False, at_end=False):
        AbstractChomper.__init__(self)
        self._element = chomper_of(element)
        self._separator = chomper_of(separator)  # may be None
        self._at_start = at_start and separator is not None
        self._at_end = at_end and separator is not None

    def _chomp(self, s, index, tracker):
        rollback_index = index
        if self._at_start:
            chomp_result = self._separator._chomp(s, index, tracker)
            if chomp_result is None:
                return None if self._at_end else [], rollback_index
            _, index = chomp_result

        encountered_values = []
        pending_value = None
        while True:
            chomp_result = self._element._chomp(s, index, tracker)
            if chomp_result is None:
                return encountered_values, rollback_index
            value, index = chomp_result
            if self._at_end:
                pending_value = value
            else:
                rollback_index = index
                encountered_values.append(value)

            if self._separator is not None:
                chomp_result = self._separator._chomp(s, index, tracker)
                if chomp_result is None:
                    return encountered_values, rollback_index
                _, index = chomp_result
                if self._at_end:
                    rollback_index = index
                    encountered_values.append(pending_value)
                    pending_value = None

