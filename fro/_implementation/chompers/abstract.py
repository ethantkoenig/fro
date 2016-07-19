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

    def __init__(self, fertile=True, name=None):
        """
        :param fertile: if the chomper produces a meaningful value
        :param name: name of chomper, for error messages
        """
        self._fertile = fertile
        self._name = name

        if name is None:
            self.chomp = self._chomp

        self._func = None

    def fertile(self):
        return self._fertile

    def name(self):
        return self._name

    def clone(self, fertile=None, name=None, func=None):
        """
        :return: a chomper identical to self, except with the specified values
        """
        fertile = fertile if fertile is not None else self._fertile
        name = name if name is not None else self._name
        if func is None:
            func_ = self._func
        elif self._func is not None:
            func_ = lambda *x: func(self._func(*x))
        else:
            func_ = func
        carbon = copy.copy(self)
        carbon._fertile = fertile
        carbon._name = name
        carbon._last_parsed = None
        carbon._func = func_
        if name is not None or func_ is not None:
            carbon.chomp = AbstractChomper.chomp.__get__(carbon, AbstractChomper)
        else:
            carbon.chomp = carbon._chomp
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
        name = self._name
        if name is not None:
            tracker.offer_name(name)
        box = self._chomp(state, tracker)
        if box is not None:
            if self._func is not None:
                box.value = self._func(box.value)
        if name is not None:
            tracker.revoke_name()
        return box

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
        raise NotImplementedError  # must be implemented by subclasses

    @staticmethod
    def _failed_lookahead(state, tracker):
        msg = "Failed lookahead during parse"
        AbstractChomper._urgent(ChompError(
            msg, state.location(), tracker.current_name()))

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

    def revoke_name(self):
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
