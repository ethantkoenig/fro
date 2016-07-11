import random
import unittest

import fro
import utils


class ErrorTests(unittest.TestCase):

    def __init__(self, method_name):
        unittest.TestCase.__init__(self, method_name)
        self.longMessage = True

    def test_alt1(self):
        p1 = fro.comp([r"a", r"b", r"c"], name="p1") >> (lambda a, b, c: a + b + c)
        p2 = fro.rgx(r"abQ", name="p2")
        parser = fro.alt([p1, p2], name="parent")
        self.assertParseErrorAttributes(
            parser, "ab0",
            column=2,
            line=0,
            name="p1")

    def test_comp1(self):
        p1 = fro.seq(fro.intp, sep=r",").name("p1")
        parser = fro.comp([r"~\[", p1, r"~\]"], name="comp").get() | sum
        length = random.randint(0, 5)
        s = "[{}]".format(",".join(str(n) for n in range(length)))
        for i in range(len(s)):
            char = s[i]
            names = []
            if char in '[]':
                names.append("comp")
            elif char in ',':
                names.append("p1")
                names.append("comp")
            else:
                names.append("int")
            modified_s = s[:i] + "$" + s[i+1:]
            self.assertParseErrorAttributes(
                parser,
                modified_s,
                column=i,
                line=0,
                message="i={0}, s={1}".format(i, modified_s),
                names=names)

    def test_nested1(self):
        parser = fro.nested(r"\(", r"\)")
        s = "((hey there)(goodbye)"
        self.assertParseErrorAttributes(
            parser,
            s,
            column=0,
            line=0)

    def test_seq1(self):
        floatsp = fro.seq(fro.floatp, sep=r"~,")
        for _ in range(10):
            length = random.randint(2, 8)
            s = ",".join(str(utils.random_float()) for _ in range(length))
            s = s.replace(",", ">", 1)
            self.assertParseErrorAttributes(
                floatsp,
                s,
                line=0,
                message="s={0}".format(s))

    def assertParseErrorAttributes(self, parser, string, message=None, **kwargs):
        """
        Asserts that parser.parse(s) raises a FroParseError, and asserts
        specified properties of the raised error
        """
        try:
            parser.parse_str(string)
            self.fail("No error was thrown")
        except fro.FroParseError as e:
            names = [m.name() for m in e.messages()]
            if "column" in kwargs:
                self.assertEqual(kwargs["column"], e.column(index_from=0), message)
            if "line" in kwargs:
                self.assertEqual(kwargs["line"], e.line(index_from=0), message)
            if "name" in kwargs:
                self.assertIn(kwargs["name"], names, message)
            if "names" in kwargs:
                for name in kwargs["names"]:
                    self.assertIn(name, names, message)


if __name__ == "__main__":
    unittest.main()
