import unittest

import fro


class FroTests(unittest.TestCase):

    def test_compose1(self):
        rgxs = [fro.rgx(str(x), int) for x in xrange(100)]
        rgxs = [++rgx if i % 2 == 0 else --rgx for i, rgx in enumerate(rgxs)]
        parser = fro.compose(rgxs, lambda *x: sum(x))
        actual = parser.parse("".join(str(i) for i in xrange(100)))
        expected = sum(i for i in xrange(100) if i % 2 == 0)
        self.assertEqual(actual, expected)

    def test_compose2(self):
        rgxs = ["a+b+", "b+a+"]
        parser = fro.compose(rgxs)
        actual = parser.parse("aaabbaa")
        expected = None
        self.assertEqual(actual, expected)

    def test_nested1(self):
        inside = "(())()(())()"
        nested_parser = fro.nested(r"\(", r"\)")
        parens = "({})".format(inside)
        actual = nested_parser.parse(parens)
        expected = inside
        self.assertEqual(actual, expected)

    def test_nested2(self):
        inside = "00jk1kj0lk1kkj01101".replace("0", "aa").replace("1", "ab")
        nested_parser = fro.nested("aa", "ab")
        expected = inside
        actual = nested_parser.parse("aa{}ab".format(inside))
        self.assertEqual(actual, expected)

    def test_nested3(self):
        open_regex_str = r"ab*c"
        close_regex_str = r"c+"
        s = "abbbcdeefc"
        nested_parser = fro.nested(open_regex_str, close_regex_str)
        expected = "deef"
        actual = nested_parser.parse(s)
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

    def test_seq2(self):
        sq = fro.seq("a+?", separator="a")
        for n in xrange(20):
            actual = sq.parse("a" * n)
            if n == 0:
                expected = []
            elif n % 2 == 1:
                expected = ["a"] * ((n + 1) / 2)
            else:
                expected = None
            self.assertEqual(actual, expected)

    def test_seq_empty(self):
        num = fro.rgx(r"[0-9]+", int)
        num_seq = fro.seq(num, ",", start = r"\@")
        actual = num_seq.parse("")
        expected = []
        self.assertEquals(actual, expected)


if __name__ == "__main__":
    unittest.main()
