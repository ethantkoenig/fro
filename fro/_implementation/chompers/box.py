

class Box(object):
    """
    A boxed value. Allows chompers to differentiate between producing the value None,
    and failing to produce
    """
    def __init__(self, value):
        self.value = value
