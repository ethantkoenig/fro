# coding=utf-8
import math
import random
import unittest

import interface
from parse_error import FroParseError


class FroTests(unittest.TestCase):

    # Tests for parser-constructing functions

    def test_alt1(self):
        parser = interface.alt([r"abc+", r"ab+c"])
        self.assertEqual(parser.parse("abcc"), "abcc")
        self.assertEqual(parser.parse("abbbc"), "abbbc")
        self.assertRaises(FroParseError, parser.parse, "ac")

    def test_alt2(self):
        parser = interface.alt([r"[0-9]{3}", interface.intp]).quiet()
        self.assertEqual(parser.parse("12"), 12)
        self.assertEqual(parser.parse("358"), "358")
        self.assertEqual(parser.parse("9876"), None)
        self.assertEqual(parser.parse("234t"), None)

    def test_compose1(self):
        rgxs = [interface.rgx(str(n)) | int for n in range(100)]
        rgxs = [++rgx if i % 2 == 0 else --rgx for i, rgx in enumerate(rgxs)]
        parser = interface.comp(rgxs) | sum
        actual = parser.parse("".join(str(i) for i in range(100)))
        expected = sum(i for i in range(100) if i % 2 == 0)
        self.assertEqual(actual, expected)

    def test_compose2(self):
        rgxs = [r"a+b+", r"b+a+"]
        parser = interface.comp(rgxs)
        self.assertRaises(FroParseError, parser.parse, "aaabbaa")

    def test_compose3(self):
        rgxs = [r"ab*", "b+"]
        parser = interface.comp(rgxs)
        self.assertRaises(FroParseError, parser.parse, "abbb")

    def test_group_rgx1(self):
        parser = interface.group_rgx(r"(a)(b+).*")
        self.assertEqual(parser.parse("abbbcde"), ("a", "bbb"))

    def test_group_rgx2(self):
        parser = interface.group_rgx(".*")
        self.assertEqual(parser.parse("\t\t\t"), ())

    def test_group_rgx3(self):
        parser = interface.group_rgx("(a)(b)")
        self.assertRaises(FroParseError, parser.parse, "acdf")

    def test_nested1(self):
        inside = "(())()(())()"
        nested_parser = interface.nested(r"\(", r"\)").name("nested parens")
        parens = "({})".format(inside)
        actual = nested_parser.parse(parens)
        expected = inside
        self.assertEqual(actual, expected)

    def test_nested2(self):
        inside = "00jk1kj0lk1kkj01101".replace("0", "aa").replace("1", "ab")
        nested_parser = interface.nested("aa", "ab")
        expected = inside
        actual = nested_parser.parse("aa{}ab".format(inside))
        self.assertEqual(actual, expected)

    def test_nested3(self):
        open_regex_str = r"ab*c"
        close_regex_str = r"c+"
        s = "abbbcdeefc"
        nested_parser = interface.nested(open_regex_str, close_regex_str)
        expected = "deef"
        actual = nested_parser.parse(s)
        self.assertEqual(actual, expected)

    def test_nested4(self):
        s = "(()"
        nested_parser = interface.nested(r"\(", r"\)")
        self.assertRaises(FroParseError, nested_parser.parse, s)

    def test_seq1(self):
        num = interface.rgx(r"[0-9]+") | int
        num_seq = interface.seq(num, ",").quiet()
        for n in range(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)))
            expected = list(range(n))
            self.assertEqual(actual, expected)
        for n in range(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)) + ",")
            expected = None
            self.assertEqual(actual, expected)

    def test_seq2(self):
        sq = interface.seq("a+?", sep="a").quiet()
        for n in range(20):
            actual = sq.parse("a" * n)
            if n == 0:
                expected = []
            elif n % 2 == 1:
                expected = ["a"] * ((n + 1) // 2)
            else:
                expected = None
            self.assertEqual(actual, expected)

    def test_seq_empty(self):
        num = interface.rgx(r"[0-9]+", int)
        num_seq = interface.seq(num, r",", sep_at_start=True).quiet()
        actual = num_seq.parse("8,8")
        expected = None
        self.assertEqual(actual, expected)

    # tests for parser methods

    def test_lstrip1(self):
        parser = interface.intp.lstrip()
        self.assertEquals(parser.parse("  12"), 12)
        self.assertEquals(parser.parse("-78"), -78)
        self.assertRaises(FroParseError, parser.parse, "45 ")
        self.assertRaises(FroParseError, parser.parse, "\t34\n")

    def test_map1(self):
        parser = interface.intp | (lambda x: x * x)
        for n in range(10):
            self.assertEqual(parser.parse(str(n)), n * n)

    def test_map2(self):
        def f(x, y):
            return x + y
        parser = interface.comp([interface.intp, r"~,", interface.intp]) >> f
        for n in range(10):
            for m in range(10):
                s = "{n},{m}".format(n=n, m=m)
                self.assertEqual(parser.parse(s), n + m)

    def test_maybe1(self):
        maybep = interface.rgx(r"ab").maybe()
        parser = interface.comp([-maybep, interface.intp]) >> (lambda x: x)
        for n in range(10):
            self.assertEqual(parser.parse(str(n)), n)
            self.assertEqual(parser.parse("ab{}".format(n)), n)

    def test_maybe2(self):
        letters = "abcdefghijklmnop"
        for _ in range(10):
            parsers = [interface.rgx(c).maybe() for c in letters]
            s = "".join(c for c in letters if random.random() < 0.5)
            parser = interface.comp(parsers) | (lambda *x: 0)
            self.assertEqual(parser.parse(s), 0)  # parse should not fail

    def test_rstrip1(self):
        parser = interface.natp.rstrip()
        self.assertEqual(parser.parse("01"), 1)
        self.assertEqual(parser.parse("7890\r\n\r"), 7890)
        self.assertRaises(FroParseError, parser.parse, " 0 ")
        self.assertRaises(FroParseError, parser.parse, "\t094")
        self.assertRaises(FroParseError, parser.parse, "-12")

    def test_strip1(self):
        parser = interface.rgx(r"abc").strip()
        self.assertEqual(parser.parse("abc"), "abc")
        self.assertEqual(parser.parse("\t\tabc  "), "abc")
        self.assertEqual(parser.parse("\n\n\rabc"), "abc")
        self.assertEqual(parser.parse("abc "), "abc")
        self.assertRaises(FroParseError, parser.parse, "ab c")

    # tests for built-in parsers

    def test_floatp(self):
        for _ in range(100):
            f = random_float()
            result = interface.floatp.parse(str(f))
            self.assertTrue(abs(f - result) < 1e-6 or abs(f / result - 1) < 1e-6)

    def test_intp(self):
        for n in range(-10, 10):
            self.assertEqual(interface.intp.parse(str(n)), n)
        for _ in range(100):
            n = random.getrandbits(100)
            self.assertEqual(interface.intp.parse(str(n)), n)

# utilities


def random_float():
    abs_val = math.exp(random.uniform(-200, 200))
    return abs_val if random.random() < 0.5 else -abs_val


if __name__ == "__main__":
    unittest.main()
