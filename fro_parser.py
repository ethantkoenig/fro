
class AbstractFroParser(object):
    """
    Immutable.

    FIELDS:
    _err - formatted string for error msg in event of parse error
    _fertile(bool) - if the parser produces a meaningful value. defaults to True
    """
    def __init__(self, fertile=True, err=None):
        self._fertile = fertile
        self._err = err

    def parse(self, s):
        chomp_result = self._chomp(s, 0, True)
        if chomp_result is None:
            return self._quit(0, True)
        value, index = chomp_result
        return value if index == len(s) else self._quit(0, True)

    def err(self, err):
        self._err = err
        return self

    def __neg__(self):
        if not self._fertile:
            return self
        return TwinParser(self)

    def __pos__(self):
        if self._fertile:
            return self
        return TwinParser(self)

    def __or__(self, func):
        return MapFroParser(self, func)

    def __rshift__(self, func):
        return MapFroParser(self, lambda x: func(*x))

    def _quit(self, index, fail_hard):
        if self._err is None or not fail_hard:
            return None
        raise ValueError(self._err.format(index))

    def _chomp(self, s, index, fail_hard):
        """
        ARGUMENTS:
          s : str
          index : int
          fail_hard : bool
        RETURNS:
          (t, str), or None
        """
        return self._quit(index, fail_hard) # must be implemented by subclasses

class MapFroParser(AbstractFroParser):

    def __init__(self, parser, func):
        AbstractFroParser.__init__(self)
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, fail_hard):
        chomp_result = self._parser._chomp(s, index, fail_hard)
        if chomp_result is None:
            return None
        value, index = chomp_result
        return self._func(value), index

class TwinParser(AbstractFroParser):

    def __init__(self, twin):
        AbstractFroParser.__init__(self, not twin._fertile)
        self._twin = twin

    def __neg__(self):
        if not self._fertile:
            return self
        return self._twin

    def __pos__(self):
        if self._fertile:
            return self
        return self._twin

    def _chomp(self, s, index, fail_hard):
        return self._twin._chomp(s, index, fail_hard)

