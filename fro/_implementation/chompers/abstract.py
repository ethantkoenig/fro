import copy

from fro._implementation import parse_error
from fro._implementation.chompers.chomp_error import ChompError


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

    def chomp(self, state, tracker):
        """
        Parses the head of the string s, possibly "chomping" off the beginning
        of s and producing a value.

        :param state: ChompState
        :param tracker: FroParseErrorTracker - tracks encountered errors
        :return: (t, index) : value parsed, and first "unconsumed" index
        """
        # does some common bookkeeping, then delegates to specialized _chomp
        if self._name is not None:
            tracker.offer_name(self._name)
        try:
            return self._chomp(state, tracker)
        finally:
            if self._name is not None:
                tracker.revoke_name(self._name)

    # internals
    @staticmethod
    def _apply(tracker, state, func, *args):
        """
        Convenience method to apply function while gracefully handling errors
        :param tracker: FroParseErrorTracker
        :param start_index: start index of relevant region
        :param end_index: end index of relevant region
        :return: result of function application
        """
        try:
            return func(*args)
        except parse_error.FroParseError as e:
            # Add a special case for parse errors because nested parsers can throw a
            # "no closing to match open" parse error during reducer application
            raise e
        except Exception as e:
            msg = "Error during function application"
            chomp_error = ChompError(msg, state.location(), tracker.current_name())
            AbstractChomper._urgent(chomp_error, e)

    def _chomp(self, state, tracker):
        """
        Parses the head of the string s, possibly "chomping" off the beginning
        of s and producing a value. Delegated to by chomp.

        An implementation should not involve recursive calls to _chomp, but instead
        calls to chomp.
        :param state: ChompState - state/location of chomping
        :param tracker: FroParseErrorTracker - tracks encountered errors
        :return: tuple (value parsed, first "unconsumed" index)
        """
        return None  # must be implemented by subclasses

    @staticmethod
    def _failed_lookahead(state, tracker):
        msg = "Failed lookahead during parse"
        AbstractChomper._urgent(ChompError(msg, state.location, tracker.current_name))

    @staticmethod
    def _log_error(chomp_error, tracker):
        """
        Convenience method to add a parse error to the tracker
        """
        tracker.report_error(chomp_error)

    @staticmethod
    def _next_index(s, index):
        """
        Convenience method for safely incrementing a string index
        """
        return index + 1 if index < len(s) else index

    @staticmethod
    def _urgent(chomp_error, cause=None):
        raise parse_error.FroParseError([chomp_error], cause)


class FroParseErrorTracker(object):
    """
    Tracks the errors that have been encountered during parsing, and preserves the most relevant one
    (i.e. occurred at farthest index). Also tracks names of encountered chompers.
    """
    def __init__(self):
        self._chomp_errors = []
        self._location = None
        self._names = []

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

    def report_error(self, chomp_error):
        if self._location is None or chomp_error.location() > self._location:
            self._location = chomp_error.location()
            self._chomp_errors = [chomp_error]
        elif chomp_error.location() < self._location:
            return
        elif chomp_error.location() == self._location:
            self._chomp_errors.append(chomp_error)
        else:
            msg = "Incomparable locations: {0} {1}".format(
                self._location,
                chomp_error.location())
            raise AssertionError(msg)

    def retrieve_error(self):
        if len(self._chomp_errors) == 0:
            return None
        return parse_error.FroParseError(self._chomp_errors)
