# coding=utf-8
import math
import random
import unittest

import fro
import fro_parse_error


class FroTests(unittest.TestCase):

    def test_alt1(self):
        parser = fro.alt([r"abc+", r"ab+c"])
        self.assertEquals(parser.parse("abcc"), "abcc")
        self.assertEquals(parser.parse("abbbc"), "abbbc")
        self.assertRaises(fro_parse_error.FroParseError, parser.parse, "ac")

    def test_alt2(self):
        parser = fro.alt([r"[0-9]{3}", fro.intp]).quiet()
        self.assertEquals(parser.parse("12"), 12)
        self.assertEquals(parser.parse("358"), "358")
        self.assertEquals(parser.parse("9876"), None)
        self.assertEquals(parser.parse("234t"), None)

    def test_compose1(self):
        rgxs = [fro.rgx(str(n)) | int for n in xrange(100)]
        rgxs = [++rgx if i % 2 == 0 else --rgx for i, rgx in enumerate(rgxs)]
        parser = fro.compose(rgxs) | sum
        actual = parser.parse("".join(str(i) for i in xrange(100)))
        expected = sum(i for i in xrange(100) if i % 2 == 0)
        self.assertEqual(actual, expected)

    def test_compose2(self):
        rgxs = [r"a+b+", r"b+a+"]
        parser = fro.compose(rgxs)
        self.assertRaises(fro_parse_error.FroParseError, parser.parse, "aaabbaa")

    def test_compose3(self):
        rgxs = [r"ab*", "b+"]
        parser = fro.compose(rgxs)
        self.assertRaises(fro_parse_error.FroParseError, parser.parse, "abbb")

    def test_group_rgx1(self):
        parser = fro.group_rgx(r"(a)(b+).*")
        self.assertEqual(parser.parse("abbbcde"), ("a", "bbb"))

    def test_group_rgx2(self):
        parser = fro.group_rgx(".*")
        self.assertEqual(parser.parse("\t\t\t"), ())

    def test_group_rgx3(self):
        parser = fro.group_rgx("(a)(b)")
        self.assertRaises(fro_parse_error.FroParseError, parser.parse, "acdf")

    def test_maybe1(self):
        maybep = fro.rgx(r"ab").maybe()
        parser = fro.compose([-maybep, fro.intp]) >> (lambda x: x)
        for n in xrange(10):
            self.assertEquals(parser.parse(str(n)), n)
            self.assertEquals(parser.parse("ab{}".format(n)), n)

    def test_maybe2(self):
        letters = "abcdefghijklmnop"
        for _ in xrange(10):
            parsers = [fro.rgx(c).maybe() for c in letters]
            s = "".join(c for c in letters if random.random() < 0.5)
            parser = fro.compose(parsers) | (lambda *x: 0)
            self.assertEqual(parser.parse(s), 0)  # parse should not fail

    def test_nested1(self):
        inside = "(())()(())()"
        nested_parser = fro.nested(r"\(", r"\)").name("nested parens")
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

    def test_nested4(self):
        s = "(()"
        nested_parser = fro.nested(r"\(", r"\)")
        self.assertRaises(fro_parse_error.FroParseError, nested_parser.parse, s)

    def test_seq1(self):
        num = fro.rgx(r"[0-9]+") | int
        num_seq = fro.seq(num, ",").quiet()
        for n in xrange(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)))
            expected = range(n)
            self.assertEqual(actual, expected)
        for n in xrange(10):
            actual = num_seq.parse(",".join(str(x) for x in range(n)) + ",")
            expected = None
            self.assertEqual(actual, expected)

    def test_seq2(self):
        sq = fro.seq("a+?", sep="a").quiet()
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
        num_seq = fro.seq(num, r",", sep_at_start=True).quiet()
        actual = num_seq.parse("8,8")
        expected = None
        self.assertEquals(actual, expected)

    def test_floatp(self):
        for _ in xrange(100):
            f = random_float()
            result = fro.floatp.parse(str(f))
            self.assertTrue(abs(f - result) < 1e-6 or abs(f / result - 1) < 1e-6)

    def test_intp(self):
        for n in xrange(-10, 10):
            self.assertEqual(fro.intp.parse(str(n)), n)
        for _ in xrange(100):
            n = random.getrandbits(100)
            self.assertEqual(fro.intp.parse(str(n)), n)

    def test_offset_of_index1(self):
        s = "αβρααμ εγεννησεν τον"
        u = s.decode(encoding="utf-8")
        for i in xrange(len(u)):
            low_index = len(u[:i].encode(encoding="utf-8"))
            high_index = len(u[:(i + 1)].encode(encoding="utf-8"))
            for index in xrange(low_index, high_index):
                self.assertEqual(fro.offset_of_index(s, index), i)
        self.assertEqual(fro.offset_of_index(s, len(s)), len(u))


# utilities

def random_float():
    abs_val = math.exp(random.uniform(-200, 200))
    return abs_val if random.random() < 0.5 else -abs_val


if __name__ == "__main__":
    unittest.main()
