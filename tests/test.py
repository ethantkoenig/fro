# coding=utf-8
import random
import unittest

import fro
import utils


class FroTests(unittest.TestCase):

    # Tests for parser-constructing functions

    def test_alt1(self):
        parser = fro.alt([r"abc+", r"ab+c"])
        self.assertEqual(parser.parse_str("abcc"), "abcc")
        self.assertEqual(parser.parse_str("abbbc"), "abbbc")
        self.assertRaises(fro.FroParseError, parser.parse_str, "ac")

    def test_alt2(self):
        parser = fro.alt([r"[0-9]{3}", fro.intp])

        def parse(s):
            return parser.parse_str(s, loud=False)

        self.assertEqual(parse("12"), 12)
        self.assertEqual(parse("358"), "358")
        self.assertEqual(parse("9876"), None)
        self.assertEqual(parse("234t"), None)

    def test_chain1(self):
        def func(parser):
            return fro.comp([r"~a", fro.seq(parser), r"~b"]) >> (lambda x: 1 + sum(x))
        chained = fro.chain(func)
        self.assertEqual(chained.parse("aababb"), 3)

    def test_chain2(self):
        def func(parser):
            box = fro.BoxedValue(None)
            openp = fro.rgx("[a-z]+") | box.update_and_get
            closep = fro.thunk(lambda: box.get().upper())
            children = fro.seq(parser) | (lambda l: 1 + sum(l))
            return fro.comp([~openp, children, ~closep]).get()
        chained = fro.chain(func)
        l = ["abc", "efg", "EFG", "q", "Q", "ABC"]
        self.assertEqual(chained.parse(l), 3)
        l_ = [chr(i) for i in range(97, 123)]
        l = l_ + list(reversed([x.upper() for x in l_]))
        self.assertEqual(chained.parse(l), 26)
        l = ["abc", "def", "DEF", "DEF"]
        self.assertRaises(fro.FroParseError, chained.parse, l)

    def test_compose1(self):
        rgxs = [fro.rgx(str(n)) | int for n in range(100)]
        rgxs = [rgx.significant() if i % 2 == 0 else ~~rgx for i, rgx in enumerate(rgxs)]
        parser = fro.comp(rgxs) | sum
        actual = parser.parse_str("".join(str(i) for i in range(100)))
        expected = sum(i for i in range(100) if i % 2 == 0)
        self.assertEqual(actual, expected)

    def test_compose2(self):
        rgxs = [r"a+b+", r"b+a+"]
        parser = fro.comp(rgxs)
        self.assertRaises(fro.FroParseError, parser.parse_str, "aaabbaa")

    def test_compose3(self):
        rgxs = [r"ab*", "b+"]
        parser = fro.comp(rgxs)
        self.assertRaises(fro.FroParseError, parser.parse_str, "abbb")

    def test_group_rgx1(self):
        parser = fro.group_rgx(r"(a)(b+).*")
        self.assertEqual(parser.parse_str("abbbcde"), ("a", "bbb"))

    def test_group_rgx2(self):
        parser = fro.group_rgx(".*")
        self.assertEqual(parser.parse_str("\t\t\t"), ())

    def test_group_rgx3(self):
        parser = fro.group_rgx("(a)(b)")
        self.assertRaises(fro.FroParseError, parser.parse_str, "acdf")

    def test_nested1(self):
        inside = "(())()(())()"
        nested_parser = fro.nested(r"\(", r"\)").name("nested parens")
        parens = "({})".format(inside)
        actual = nested_parser.parse_str(parens)
        expected = inside
        self.assertEqual(actual, expected)

    def test_nested2(self):
        inside = "00jk1kj0lk1kkj01101".replace("0", "aa").replace("1", "ab")
        nested_parser = fro.nested("aa", "ab")
        expected = inside
        actual = nested_parser.parse_str("aa{}ab".format(inside))
        self.assertEqual(actual, expected)

    def test_nested3(self):
        open_regex_str = r"ab*c"
        close_regex_str = r"c+"
        s = "abbbcdeefc"
        nested_parser = fro.nested(open_regex_str, close_regex_str)
        expected = "deef"
        actual = nested_parser.parse_str(s)
        self.assertEqual(actual, expected)

    def test_nested4(self):
        s = "(()"
        nested_parser = fro.nested(r"\(", r"\)")
        self.assertRaises(fro.FroParseError, nested_parser.parse_str, s)

    def test_seq1(self):
        num = fro.rgx(r"[0-9]+") | int
        num_seq = fro.seq(num, sep=",")
        for n in range(10):
            actual = num_seq.parse_str(",".join(str(x) for x in range(n)), loud=False)
            expected = list(range(n))
            self.assertEqual(actual, expected)
        for n in range(10):
            actual = num_seq.parse_str(",".join(str(x) for x in range(n)) + ",", loud=False)
            expected = None
            self.assertEqual(actual, expected)

    def test_seq2(self):
        sq = fro.seq("a+?", sep="a")
        for n in range(20):
            actual = sq.parse_str("a" * n, loud=False)
            if n == 0:
                expected = []
            elif n % 2 == 1:
                expected = ["a"] * ((n + 1) // 2)
            else:
                expected = None
            self.assertEqual(actual, expected)

    def test_seq3(self):
        sq = fro.seq(r"[a-z]+\n")
        lines = ["asdfj\n", "q\n", "adsjfa\n"]
        actual = sq.parse(lines)
        self.assertEqual(actual, lines)

    def test_seq_empty(self):
        num = fro.rgx(r"[0-9]+", "natural number")
        num_seq = fro.seq(num, sep=r",")
        actual = num_seq.parse_str(",8,8", loud=False)
        self.assertIsNone(actual)

    def test_thunk1(self):
        box = fro.BoxedValue(0)
        thunkp = fro.thunk(lambda: str(box.update_and_get(box.get() + 1)))
        for s in "12345":
            self.assertEqual(thunkp.parse_str(s), s)

    def test_thunk2(self):
        box = fro.BoxedValue(-1)
        thunkp = fro.thunk(lambda: str(box.update_and_get(box.get() + 1)))
        parser = fro.seq(thunkp, sep=r",")
        l = [str(i) for i in range(20)]
        self.assertEqual(parser.parse_str(",".join(l)), l)

    def test_tie1(self):
        def _func(p):
            return fro.comp([r"~\(", p.maybe(0), r"~\)"]) >> (lambda x: x + 1)
        parser = fro.tie(_func, name="knot")
        actual = parser.parse_str("((()))")
        self.assertEqual(actual, 3)

    def test_tie2(self):
        def _func(p):
            return fro.comp([r"~a", fro.seq(p), r"~b"]).get()
        parser = fro.tie(_func, name="knot")
        actual = parser.parse_str("aababb")
        self.assertEqual(actual, [[], []])

    def test_until1(self):
        lines = ["sdf", "sdf", "a"]
        parser = fro.comp([fro.until(r"a", reducer="".join), r"a"])
        self.assertEqual(parser.parse(lines), ("sdfsdf", "a"))

    def test_until2(self):
        lines = "hello from a far place".split()
        parser = fro.until(r"zebra") | (lambda _: True)
        self.assertEqual(parser.parse(lines), True)

    def test_until3(self):
        lines = ["hello", "there", "big", "world"]
        parser = fro.comp([~fro.until("i"), fro.seq(r"[a-z]+")]).get()
        self.assertEqual(parser.parse(lines), ["ig", "world"])

    # tests for parser methods

    def test_lstrip1(self):
        parser = fro.intp.lstrip()
        self.assertEqual(parser.parse_str("  12"), 12)
        self.assertEqual(parser.parse_str("-78"), -78)
        self.assertRaises(fro.FroParseError, parser.parse_str, "45 ")
        self.assertRaises(fro.FroParseError, parser.parse_str, "\t34\n")

    def test_lstrips1(self):
        parser = fro.intp.lstrips()

        def parse(s, sep=","):
            return parser.parse(s.split(sep))
        self.assertEqual(parse("  ,,  12,"), 12)
        self.assertEqual(parse("-125"), -125)
        self.assertRaises(fro.FroParseError, parse, " ,, 145, ")
        self.assertRaises(fro.FroParseError, parse, "2\n")

    def test_map1(self):
        parser = fro.intp | (lambda x: x * x)
        for n in range(10):
            self.assertEqual(parser.parse_str(str(n)), n * n)

    def test_map2(self):
        def f(x, y):
            return x + y
        parser = fro.comp([fro.intp, r"~,", fro.intp]) >> f
        for n in range(10):
            for m in range(10):
                s = "{n},{m}".format(n=n, m=m)
                self.assertEqual(parser.parse_str(s), f(n, m))

    def test_maybe1(self):
        maybep = fro.rgx(r"ab").maybe()
        parser = fro.comp([~maybep, fro.intp]) >> (lambda x: x)
        for n in range(10):
            self.assertEqual(parser.parse_str(str(n)), n)
            self.assertEqual(parser.parse_str("ab{}".format(n)), n)

    def test_maybe2(self):
        letters = "abcdefghijklmnop"
        for _ in range(10):
            parsers = [fro.rgx(c).maybe() for c in letters]
            s = "".join(c for c in letters if random.random() < 0.5)
            parser = fro.comp(parsers) | (lambda *x: 0)
            self.assertEqual(parser.parse_str(s), 0)  # parse should not fail

    def test_rstrip1(self):
        parser = fro.natp.rstrip()
        self.assertEqual(parser.parse_str("01"), 1)
        self.assertEqual(parser.parse_str("7890\r\n\r"), 7890)
        self.assertRaises(fro.FroParseError, parser.parse_str, " 0 ")
        self.assertRaises(fro.FroParseError, parser.parse_str, "\t094")
        self.assertRaises(fro.FroParseError, parser.parse_str, "-12")

    def test_rstrips1(self):
        parser = fro.floatp.rstrips()

        def parse(s, sep=","):
            return parser.parse(s.split(sep))
        self.assertAlmostEqual(parse("3.5E2   , \t"), 3.5E2, 1e-3)
        self.assertAlmostEqual(parse("3"), 3, 1e-3)
        self.assertRaises(fro.FroParseError, parse, ",2")

    def test_strip1(self):
        parser = fro.rgx(r"abc").strip()
        self.assertEqual(parser.parse_str("abc"), "abc")
        self.assertEqual(parser.parse_str("\t\tabc  "), "abc")
        self.assertEqual(parser.parse_str("\n\n\rabc"), "abc")
        self.assertEqual(parser.parse_str("abc "), "abc")
        self.assertRaises(fro.FroParseError, parser.parse_str, "ab c")
        self.assertEqual(fro.comp([parser]).get().parse_str("abc "), "abc")

    def test_strips1(self):
        parser = fro.rgx(r"[a-z]+").strips()

        def parse(s, sep=","):
            return parser.parse(s.split(sep))
        self.assertEqual(parse("  ,  ,abc,,, \r"), "abc")
        self.assertRaises(fro.FroParseError, parse, "  abc  ,  def\n")
        self.assertRaises(fro.FroParseError, parse, "\n\n\r \t")


    # tests for built-in parsers

    def test_floatp(self):
        for _ in range(100):
            f = utils.random_float()
            result = fro.floatp.parse_str(str(f))
            self.assertTrue(abs(f - result) < 1e-6 or abs(f / result - 1) < 1e-6)

    def test_intp(self):
        for n in range(-10, 10):
            self.assertEqual(fro.intp.parse_str(str(n)), n)
        for _ in range(100):
            n = random.getrandbits(100)
            self.assertEqual(fro.intp.parse_str(str(n)), n)


# helpers and utilities



if __name__ == "__main__":
    unittest.main()
