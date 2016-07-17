# coding=utf-8
import random
import re
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
        parser = fro.alt([r"[0-9]{3}", fro.intp]).quiet()
        self.assertEqual(parser.parse_str("12"), 12)
        self.assertEqual(parser.parse_str("358"), "358")
        self.assertEqual(parser.parse_str("9876"), None)
        self.assertEqual(parser.parse_str("234t"), None)

    def test_compose1(self):
        rgxs = [fro.rgx(str(n)) | int for n in range(100)]
        rgxs = [++rgx if i % 2 == 0 else --rgx for i, rgx in enumerate(rgxs)]
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
        num_seq = fro.seq(num, sep=",").quiet()
        for n in range(10):
            actual = num_seq.parse_str(",".join(str(x) for x in range(n)))
            expected = list(range(n))
            self.assertEqual(actual, expected)
        for n in range(10):
            actual = num_seq.parse_str(",".join(str(x) for x in range(n)) + ",")
            expected = None
            self.assertEqual(actual, expected)

    def test_seq2(self):
        sq = fro.seq("a+?", sep="a").quiet()
        for n in range(20):
            actual = sq.parse_str("a" * n)
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
        num_seq = fro.seq(num, sep=r",").quiet()
        actual = num_seq.parse_str(",8,8")
        self.assertIsNone(actual)

    def test_tie1(self):
        def _func(parser):
            return fro.comp([r"~\(", parser.maybe(0), r"~\)"]) >>  (lambda x: x + 1)
        parser = fro.tie(_func, name="knot")
        actual = parser.parse_str("((()))")
        self.assertEqual(actual, 3)

    def test_tie2(self):
        def _func(parser):
            return fro.comp([r"~a", fro.seq(parser), r"~b"]).get()

        parser = fro.tie(_func, name="knot")
        actual = parser.parse_str("aababb")
        self.assertEqual(actual, [[], []])

    # tests for parser methods

    def test_dependent1(self):
        p1 = fro.rgx(r"[abc]+!")
        parser = fro.comp([p1, p1.dependent(lambda s: s)]) | "".join
        s = "acc!acc!"
        self.assertEqual(parser.parse_str(s), s)

    def test_dependent2(self):
        p1 = fro.rgx(r"[abc]+!")
        parser = fro.comp([p1, p1.dependent(lambda s: s)]) | "".join
        self.assertRaises(fro.FroParseError, parser.parse_str, "cb!aa!")

    def test_dependent3(self):
        p1 = fro.rgx(r"[a-z]+")

        def _parser(string):
            if len(string) > 0 and string[0] == "a":
                return fro.rgx(r"TheFirstOneStartsWithA")
            elif len(string) < 3:
                return p1
            return re.escape(string)

        parser = fro.comp([p1, r"~,", p1.dependent(_parser)]) | (lambda _: 0)
        self.assertEqual(parser.parse_str("ui,ou"), 0)
        self.assertEqual(parser.parse_str("asdf,TheFirstOneStartsWithA"), 0)
        self.assertEqual(parser.parse_str("qwerty,qwerty"), 0)
        self.assertRaises(fro.FroParseError, parser.parse_str, "hello,goodbye")

    def test_lstrip1(self):
        parser = fro.intp.lstrip()
        self.assertEqual(parser.parse_str("  12"), 12)
        self.assertEqual(parser.parse_str("-78"), -78)
        self.assertRaises(fro.FroParseError, parser.parse_str, "45 ")
        self.assertRaises(fro.FroParseError, parser.parse_str, "\t34\n")

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
        parser = fro.comp([-maybep, fro.intp]) >> (lambda x: x)
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

    def test_strip1(self):
        parser = fro.rgx(r"abc").strip()
        self.assertEqual(parser.parse_str("abc"), "abc")
        self.assertEqual(parser.parse_str("\t\tabc  "), "abc")
        self.assertEqual(parser.parse_str("\n\n\rabc"), "abc")
        self.assertEqual(parser.parse_str("abc "), "abc")
        self.assertRaises(fro.FroParseError, parser.parse_str, "ab c")
        self.assertEqual(fro.comp([parser]).get().parse_str("abc "), "abc")

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

if __name__ == "__main__":
    unittest.main()
