

class BoxedValue(object):
    """
    An updatable boxed value
    """
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value

    def get_and_update(self, value):
        old_value = self._value
        self._value = value
        return old_value

    def update_and_get(self, value):
        self._value = value
        return value

    def update(self, value):
        self._value = value
