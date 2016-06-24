import re


def parser_of(x):
    if x is None:
        return None
    elif isinstance(x, AbstractParser):
        return x
    elif isinstance(x, str):
        return RegexParser(x)
    else:
        raise ValueError("{} does not represent a parser".format(x))


class AbstractParser(object):
    """
    Immutable.

    FIELDS:
    _err - formatted string for error msg in event of parse error 
    _fertile(bool) - if the parser produces a meaningful value. defaults to True
    """
    def __init__(self, fertile = True, err = None):
        self._fertile = fertile
        self._err = err

    def parse(self, s):
        chomp_result = self._chomp(s, 0, True)
        if chomp_result is None: return self._quit(0, True)
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
        return MapParser(self, func)

    def __rshift__(self, func):
        return MapParser(self, lambda x: func(*x))

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
        return self._quit(index) if fail_hard else None # must be implemented by subclasses


def compose(parsers, reducer = lambda *x : x):
    return CompositionParser(parsers, reducer)

class CompositionParser(AbstractParser):

    def __init__(self, parsers, reducer):
        AbstractParser.__init__(self)
        self._parsers = [parser_of(x) for x in parsers]
        self._reducer = reducer

    def _chomp(self, s, index, fail_hard):
        remainder = s
        values = []
        for parser in self._parsers:
            chomp_result = parser._chomp(remainder, index, fail_hard)
            if chomp_result is None:
                return self._quit(index, fail_hard)
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
        return self._reducer(*tuple(values)), index

def rgx(regex_string, func = None):
    return RegexParser(regex_string, func)

class RegexParser(AbstractParser):

    def __init__(self, regex_string, func = None):
        fertile = True
        if regex_string[0:1] == "@":
            fertile = False
            regex_string=regex_string[1:]
        elif regex_string[0:2] == "\\@":
            regex_string="@"+regex_string[2:]
        AbstractParser.__init__(self, fertile)
        self._regex = re.compile(regex_string)
        self._func = func

    def _chomp(self, s, index, fail_hard):
        match = self._regex.match(s, index)
        if match is None: return self._quit(index, fail_hard)
        start_index = index
        end_index = match.end()
        matched = s[start_index:end_index]
        value = matched if self._func is None else self._func(matched)
        return value, end_index


class MapParser(AbstractParser):

    def __init__(self, parser, func):
        self._parser = parser
        self._func = func

    def _chomp(self, s, index, fail_hard):
        chomp_result = self._parser._chomp(s, index, fail_hard)
        if chomp_result is None: return None
        value, index = chomp_result
        return self._func(value), index


# TODO

def seq(value, separator = None, start = None, end = None):
    return ListParser(value, separator, start, end)

class ListParser(AbstractParser):

    def __init__(self, values, separator = None, start = None, end = None):
        AbstractParser.__init__(self)
        self.values = parser_of(values)
        self.separator = parser_of(separator) # may be None
        self.start = parser_of(start) # may be None
        self.end = parser_of(end) # may be None

    def _chomp(self, s, index, fail_hard):
        if self.start is not None:
            chomp_result = self.start(s, index, False)
            if chomp_result is None:
                return [], index
            _, index = chomp_result

        encountered_values = []
        chomp_result = self.values._chomp(s, index, True)
        if chomp_result is None:
            if self.start is None: 
                return [], index
            return self._quit(index, fail_hard)
        value, index = chomp_result
        encountered_values.append(value)
        while True:
            if self.separator is not None:
                chomp_result = self.separator._chomp(s, index, False)
                if chomp_result is None:
                    break
                _, index = chomp_result
            chomp_result = self.values._chomp(s, index, True)
            if chomp_result is None:
                return self._quit(index, fail_hard)
            value, index = chomp_result
            encountered_values.append(value)

        if self.end is not None:
            chomp_result = self.end(s, index, True)
            if chomp_result is None:
                return self._quit(index, fail_hard)
            _, index = chomp_result
        return encountered_values, index 

class TwinParser(AbstractParser):

    def __init__(self, twin):
        AbstractParser.__init__(self, not twin._fertile)
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

def nested(open_regex_string, close_regex_string):
    return NestedParser(open_regex_string, close_regex_string)

class NestedParser(AbstractParser):

    def __init__(self, open_regex_string, close_regex_string):
        AbstractParser.__init__(self)
        self._init_regex = re.compile(open_regex_string)
        self._open_regex = re.compile(r".*?" + open_regex_string)
        self._close_regex = re.compile(r".*?" + close_regex_string)

    def _chomp(self, s, index, fail_hard):
        init_match = self._init_regex.match(s, index)
        if init_match is None:
            self._quit(index, fail_hard)
        start_index = index = init_match.end()
        nesting_level = 1
        while nesting_level > 0:
            end_index = index
            open_match = self._open_regex.match(s, index)
            close_match = self._close_regex.match(s, index)
            if open_match is None and close_match is None:
                return self._quit(index, fail_hard)
            elif open_match is None:
                index = close_match.end()
                nesting_level -= 1
            elif close_match is None:
                index = open_match.end()
                nesting_level += 1
            elif close_match.end() < open_match.end():
                index = close_match.end()
                nesting_level -= 1
            else:
                index = open_match.end()
                nesting_level += 1
        return s[start_index:end_index], index
