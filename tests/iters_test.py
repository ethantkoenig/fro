import random
import unittest

from fro._implementation import iters


class StreamTest(unittest.TestCase):

    def test_as_iter1(self):
        l = list(iters.CheckableIterator(range(20)))
        self.assertEqual(l, list(range(20)))

    def test_current1(self):
        l = [str(x) for x in range(10)]
        stream = iters.CheckableIterator(l)
        self.assertIsNone(stream.current())
        for index, element in enumerate(l):
            self.assertEqual(next(stream), element)
            self.assertEqual(stream.current(), element)
            if index + 1 < len(l):
                self.assertTrue(stream.has_next())
            else:
                self.assertFalse(stream.has_next())
            self.assertEqual(stream.current(), element)

    def test_has_next1(self):
        for _ in range(10):
            length = random.randint(0, 20)
            l = [random.random() for _ in range(length)]
            stream = iters.CheckableIterator(l)
            for _ in range(length):
                self.assertTrue(stream.has_next())
                next(stream)  # should not raise
            self.assertFalse(stream.has_next())
            for _ in range(5):
                self.assertRaises(StopIteration, lambda: next(stream))

if __name__ == "__main__":
    unittest.main()
