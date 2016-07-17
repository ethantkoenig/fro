from fro._implementation.chompers import abstract, chomp_error


class AlternationChomper(abstract.AbstractChomper):
    def __init__(self, chompers, fertile=True, name=None):
        abstract.AbstractChomper.__init__(self, fertile, name)
        self._chompers = list(chompers)

    def _chomp(self, state, tracker):
        col = state.column()
        line = state.line()
        for chomper in self._chompers:
            try:
                return chomper.chomp(state, tracker)
            except chomp_error.ChompError as e:
                if state.line() != line:
                    self._failed_lookahead(state, tracker)
                self._log_error(e, tracker)
                state.reset_to(col)
