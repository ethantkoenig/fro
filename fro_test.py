import fro
import unittest

class FroTests(unittest.TestCase):

    def test_compose1(self):
        rgxs = [fro.rgx(str(x), int) for x in xrange(100)]
        rgxs = [++rgx if i % 2 == 0 else --rgx for i, rgx in enumerate(rgxs)]
        parser = fro.compose(rgxs, lambda *x: sum(x))
        actual = parser.parse("".join(str(i) for i in xrange(100)))
        expected = sum(i for i in xrange(100) if i % 2 == 0)
        self.assertEqual(actual, expected)

    def test_nested1(self):
        nested_parser = fro.nested(r"\(", r"\)")
        parens = "((())()(())())"
        actual = nested_parser.parse(parens)
        expected = "(())()(())()"
        self.assertEqual(actual, expected)

    def test_nested2(self):
        nested_parser = fro.nested("aa", "ab")
        s = "000101011011".replace("0", "aa").replace("1", "ab")
        actual = nested_parser.parse(s)
        expected = "0010101101".replace("0", "aa").replace("1", "ab")
        self.assertEqual(actual, expected)

    def test_seq1(self):
        num = fro.rgx(r"[0-9]+", int)
        num_seq = fro.seq(num, ",")
        for n in xrange(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)))
            expected = range(n)
            self.assertEqual(actual, expected)
        for n in xrange(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)) + ",")
            expected = None
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
