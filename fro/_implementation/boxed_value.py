

class BoxedValue(object):
    """
    An updatable boxed value
    """
    def __init__(self, value):
        """
        Initialize the box with ``value``

        :param value: value for box to hold
        """
        self._value = value

    def get(self):
        """
        Return the box's current value

        :return: current value
        """
        return self._value

    def get_and_update(self, value):
        """
        Updates the box's value, and returns the previous value.

        :param value: updated value for box to hold
        :return: The previously held value
        """
        old_value = self._value
        self._value = value
        return old_value

    def update_and_get(self, value):
        """
        Update the box's value, and the return the updated value

        :param value: updated value for box to hold
        :return: The previously held value
        """
        self._value = value
        return value

    def update(self, value):
        """
        Update the box's value

        :param value: updated value for box to hold
        """
        self._value = value
