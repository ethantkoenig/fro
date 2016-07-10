

class Stream(object):
    def __init__(self, container):
        self._iterator = iter(container)
        self._index = -1

        self._current_value = None
        self._peeked_value = None
        self._peeked_value_valid = False
        self._at_end = False
        self._peek()

    def __iter__(self):
        return self

    def current(self):
        return self._current_value

    def has_next(self):
        if self._at_end:
            return False
        return self._peek()

    def next(self):
        if self._at_end:
            raise StopIteration
        elif self._peeked_value_valid:
            self._current_value = self._peeked_value
        else:
            self._advance()
        self._peeked_value_valid = False
        return self._current_value

    def _advance(self):
        if self._at_end:
            return
        self._current_value = self._iterator.next()
        self._peeked_value_valid = False

    def _peek(self):
        if self._peeked_value_valid:
            return True
        try:
            self._peeked_value = self._iterator.next()
            self._peeked_value_valid = True
            return True
        except StopIteration:
            self._at_end = True
            return False


def close(iterator):
    try:
        while True:
            iterator.next()
    except StopIteration:
        pass
