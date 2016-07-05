import copy
import re

from fro._implementation import parse_error


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
        :param quiet: if the parser should be "quiet" (not raise errors on parsing failures)
        """
        self._fertile = fertile
        self._name = name
        self._quiet = quiet

    def fertile(self):
        return self._fertile

    def name(self):
        return self._name

    def quiet(self):
        return self._quiet

    def clone(self, fertile=None, name=None, quiet=None):
        """
        :return: a chomper identical to self, except with the specified values
        """
        fertile = fertile if fertile is not None else self._fertile
        name = name if name is not None else self._name
        quiet = quiet if quiet is not None else self._quiet
        carbon = copy.copy(self)
        carbon._fertile = fertile
        carbon._name = name
        carbon._quiet = quiet
        return carbon

    def unname(self):
        carbon = copy.copy(self)
        carbon._name = None
        return carbon
    
    def chomp(self, s, index, tracker):
        """
        Parses the head of the string s, possibly "chomping" off the beginning
        of s and producing a value.

        :param s: string to parse
        :param index: index of s to start at
        :param tracker: FroParseErrorTracker - tracks encountered errors
        :return: (t, index) : value parsed, and first "unconsumed" index
        """
        # does some common bookkeeping, then delegates to specialized _chomp
        if self._name is not None:
            tracker.offer_name(self._name)
        result = self._chomp(s, index, tracker)
        if self._name is not None:
            tracker.revoke_name(self._name)
        return result

    # internals
    @staticmethod
    def _apply(tracker, start_index, end_index, func, *args):
        """
        Convenience method to apply function while gracefully handling errors
        :param tracker: FroParseErrorTracker
        :param start_index: start index of relevant region
        :param end_index: end index of relevant region
        :return: result of function application
        """
        try:
            return func(*args)
        except StandardError as e:
            tracker.urgent_error(str(e), start_index, end_index, e)

    def _chomp(self, s, index, tracker):
        """
        Parses the head of the string s, possibly "chomping" off the beginning
        of s and producing a value. Delegated to by chomp.

        An implementation should not involve recursive calls to _chomp, but instead
        calls to chomp.
        :param s: string to parse
        :param index: index of s to start at
        :param tracker: FroParseErrorTracker - tracks encountered errors
        :return: tuple (value parsed, first "unconsumed" index)
        """
        return None  # must be implemented by subclasses

    @staticmethod
    def _log_error(tracker, message, start_index, end_index):
        """
        Convenience method to add a parse error to the tracker
        """
        tracker.report_error(message, start_index, end_index)

    @staticmethod
    def _next_index(s, index):
        """
        Convenience method for safely incrementing a string index
        """
        return index + 1 if index < len(s) else index


class FroParseErrorTracker(object):
    """
    Tracks the errors that have been encountered during parsing, and preserves the most relevant one
    (i.e. occurred at farthest index). Also tracks names of encountered chompers.
    """
    def __init__(self, string):
        self._messages = []
        self._start_index = -1
        self._end_index = -1
        self._names = []
        self._string = string

    def offer_name(self, name):
        self._names.append(name)

    def revoke_name(self, name):
        current_name = self.current_name()
        if current_name is None:
            msg = "Tracker contains no names, could not revoke name {0}"\
                .format(name)
            raise AssertionError(msg)
        elif name != current_name:
            msg = "Could not revoke name {0}, current name is {1}"\
                .format(name, current_name)
            raise ValueError(msg)
        self._names.pop()

    def current_name(self):
        return None if len(self._names) == 0 else self._names[-1]

    def report_error(self, message, start_index, end_index):
        if start_index < self._start_index:
            return
        elif start_index == self._start_index:
            if end_index < self._end_index:
                return
            elif end_index == self._end_index:
                self._messages.append(parse_error.FroParseError.Message(
                    message, self.current_name()))
                return
        self._end_index = end_index
        self._start_index = start_index
        self._messages = [parse_error.FroParseError.Message(
            message, self.current_name())]

    def retrieve_error(self):
        if len(self._messages) == 0:
            return None
        return parse_error.FroParseError(self._string, self._messages,
                                         self._start_index, self._end_index)

    def urgent_error(self, message, start_index, end_index, cause=None):
        name = self.current_name()
        msg_obj = parse_error.FroParseError.Message(message, name)
        raise parse_error.FroParseError(self._string, [msg_obj], start_index,
                                        end_index, cause)


# Chomper subclasses


class AlternationChomper(AbstractChomper):
    def __init__(self, chompers, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._chompers = list(chompers)

    def _chomp(self, s, index, tracker):
        for chomper in self._chompers:
            result = chomper.chomp(s, index, tracker)
            if result is not None:
                return result
        return None


class CompositionChomper(AbstractChomper):

    def __init__(self, parsers, separator=None, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._parsers = list(parsers)
        self._separator = separator  # self._separator may be None

    def _chomp(self, s, index, tracker):
        values = []
        for i, parser in enumerate(self._parsers):
            chomp_result = parser.chomp(s, index, tracker)
            if chomp_result is None:
                return None
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
            if i < len(self._parsers) - 1 and self._separator is not None:
                chomp_result = self._separator.chomp(s, index, tracker)
                if chomp_result is None:
                    return None
                _, index = chomp_result
        return tuple(values), index


class DelegateChomper(AbstractChomper):
    """
    Fro parser that delegates parsing to another parser
    """
    def __init__(self, delegate, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._delegate = delegate

    def _chomp(self, s, index, tracker):
        return self._delegate.chomp(s, index, tracker)


class GroupRegexChomper(AbstractChomper):

    def __init__(self, regex_str, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_str)

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            self._log_error(tracker, msg, index, self._next_index(s, index))
            return None
        return match.groups(), match.end()


class NestedChomper(AbstractChomper):

    def __init__(self, open_regex_string, close_regex_string, fertile=True,
                 name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._init_chomper = RegexChomper(open_regex_string)
        self._open_regex = re.compile(r".*?({})".format(open_regex_string))
        self._close_regex = re.compile(r".*?({})".format(close_regex_string))
        self._open_regex_string = open_regex_string
        self._close_regex_string = close_regex_string

    def _chomp(self, s, index, tracker):
        start_index = index
        chomp_result = self._init_chomper.chomp(s, index, tracker)
        if chomp_result is None:
            return None
        _, index = chomp_result
        start_inside_index = end_index = index
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
    def __init__(self, parser, func, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, tracker):
        start_index = index
        chomp_result = self._parser.chomp(s, index, tracker)
        if chomp_result is None:
            return None
        value, index = chomp_result
        return AbstractChomper._apply(tracker, start_index, index, self._func, value), index


class OptionalChomper(AbstractChomper):
    def __init__(self, child, default=None, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._child = child
        self._default = default

    def _chomp(self, s, index, tracker):
        child_result = self._child.chomp(s, index, tracker)
        if child_result is not None:
            return child_result
        return self._default, index


class RegexChomper(AbstractChomper):

    def __init__(self, regex_string, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._regex = re.compile(regex_string)

    def _chomp(self, s, index, tracker):
        match = self._regex.match(s, index)
        if match is None:
            msg = "Expected pattern \'{}\'".format(self._regex.pattern)
            self._log_error(tracker, msg, index, self._next_index(s, index))
            return None
        start_index = index
        end_index = match.end()
        return s[start_index:end_index], end_index


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
