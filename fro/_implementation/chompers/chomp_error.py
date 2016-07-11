
class ChompError(Exception):
    def __init__(self, message, location, name=None):
        self._location = location
        self._message = message
        self._name = name

    def message(self):
        return self._message

    def location(self):
        return self._location

    def name(self):
        return self._name
