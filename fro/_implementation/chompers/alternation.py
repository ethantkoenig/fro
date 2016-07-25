from fro._implementation.chompers import abstract

class AlternationChomper(abstract.AbstractChomper):
    def __init__(self, chompers, significant=True, name=None):
        abstract.AbstractChomper.__init__(self, significant, name)
        self._chompers = list(chompers)

    def _chomp(self, state, tracker):
        col = state.column()
        line = state.line()
        for chomper in self._chompers:
            box = chomper.chomp(state, tracker)
            if box is not None:
                return box
            elif state.line() != line:
                self._failed_lookahead(state, tracker)
            state.reset_to(col)
        return None
