import unittest

from fro._implementation.iters import Stream
from fro._implementation.chompers.state import ChompState


class ChompStateTest(unittest.TestCase):

    def test1(self):
        strs = ["x" * i for i in range(5, 10)]
        stream = Stream(strs)
        state = ChompState(stream)
        for i, s in enumerate(strs):
            self.assertEqual(i, state.line())
            self.assertEqual(0, state.column())
            self.assertEqual(s, state.current())
            state.advance_to(len(s))
        self.assertEqual(len(state.current()), state.column())


if __name__ == "__main__":
    unittest.main()
