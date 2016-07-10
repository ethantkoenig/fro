from fro._implementation.chompers.abstract import AbstractChomper


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
