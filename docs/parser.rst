Parser Objects
==============

``Parser`` objects are the workhorses of the fro module, providing all of the module's core parsing functionality.
However, there are a few subtleties to how they operate, which will be discussed in this section.

Parsing via chomping
--------------------

Conceptually, a ``Parser`` object parses a string, it first attempts to "consume" an initial portion of the string,
and from it produce a value. We will refer to this process (consuming an initial portion of the string and producing a
value) as the parser "chomping" the string. The terminology evokes a useful mental image, and may also be part of an
elaborate scheme to make a `Noam Chomsky <https://en.wikipedia.org/wiki/Noam_Chomsky>`_ pun.

If the parser is not successful in chomping the string, then it fails to parse it. Otherwise, the parser is successful
in *parsing* the string if (and only if) it consumed the *entire* string during chomping. This conceptual model will be
useful for understanding what happens when ``Parser`` objects are combined into new parsers.

As an example, ``fro.intp`` is a parser which consumes non-empty sequences of digits (or equivalently,
the regular expression ``r"[0-9]+"``) and produces the corresponding ``int`` values. When parsing the string ``"2358"``
it will consume the initial portion ``"2358"`` (which happens to be the entire string), and from it produces
the ``int`` value ``2358``. Since the parser consumes the entire string during chomping, the parse is successful.::

  fro.intp.parse("2358")  # chomps "2358" producing 2358, a successful parse!

When parsing the string ``"123abc"``, it will consume the initial portion ``"123"``, producing the ``int`` value
``123``. However, the parse will be unsuccessful since the remaining ``"abc"`` was not consumed.::

  fro.intp.parse("123abc")  # chomps "123" producing 123, an unsuccessful parse

Finally, when parsing the string ``"abc123"``, it will not be able to consume any part of the string, since there is no
initial portion that contains only digits. Since ``fro.intp`` only consumes *non-empty* sequences of digits, it cannot
consume an empty initial portion (which parsers are allowed to do).::

  fro.intp.parse("abc123")  # cannot chomp anything, an unsuccessful parse

Combining parsers: composition
------------------------------

With this model in place, it is much easier to make sense of what happens when you combine multiple parsers together.
As a case study, let's consider parser composition. Given two parsers ``p1`` and ``p2``, the composition of ``p1`` and
``p2`` is a new parser, separate from but dependent on ``p1`` and ``p2``. When chomping a string, it first has ``p1``
attempt to chomp. If ``p1`` successfully chomps, then ``p2`` chomps on the remaining, unconsumed portion of the string.
If either ``p1`` or ``p2`` is unable to chomp, the composition does not successfully chomp. If both ``p1`` and ``p2``
are able to chomp and produce values ``v1`` and ``v2`` respectively, then the composition consumes both of the portions
that ``p1`` and ``p2`` consumed and produces the tuple ``(v1, v2)``.

As an example, consider the following::

  az_parser = fro.rgx(r"[a-z]*")  # consumes strings that match regex, produces consumed string
  composition_parser = fro.comp([fro.intp, az_parser])  # composition of fro.intp and az_parser
  composition_parser.parse("2357primes")

When ``composition_parser`` tries to chomp ``"2357primes"``, first ``fro.intp`` will consume ``"2357"`` (of off
``"2357primes"``) and produce ``2357``, then ``az_parser`` will consume ``"primes"`` (of off ``"primes"``, which is
what remains after ``fro.intp``'s chomp) and produces ``"primes"``. Therefore, ``composition_parser``
consumes ``"2357primes"`` and produces the tuple ``(2357, "primes")``. Since ``composition_parser`` chomps the entire
string, it parses successfully.

As another example::

  twoints_parser = fro.comp([fro.intp, fro.intp])
  twoints_parser.parse("149")  # what will happen??

When ``twoints_parser`` tries to chomp ``"149"``, the first ``fro.intp`` will consume ``"149"`` and produce ``149``.
However, there will nothing left for the second ``fro.intp`` to consume, so it will not successfully chomp anything.
Since the second ``fro.intp`` cannot chomp, the composition fails to chomp, and thus fails to parse.

This example highlights an important property of fro parsers: parsers chomp myopically. If the first ``fro.intp`` in the
above example had known that it was followed by another ``fro.intp``, it perhaps could have only chomped the first two digits,
leaving the ``"9"`` for the second ``fro.intp``, and the composition could have produced the tuple ``(14, 9)``. However,
``fro.intp`` is based on the regular expression ``[0-9]+``, which matches as many digits as possible, so it consumes
as many digits as possible while chomping.

Finally, you can compose more than two parsers together. Consider the following::

    composition = fro.comp([fro.intp, fro.rgx(r"@"), fro.intp, fro.rgx(r"@"), fro.intp])
    composition.parse("123@45@6")  # returns the tuple (123, "@", 45, "@", 6)

When ``composition`` attempts to chomp ``"123@45@6"``, the first ``fro.intp`` consumes ``"123"`` and produces ``123``.
Then, the remaining, unconsumed ``"@45@6"`` is given to the first ``r"@"`` parser to chomp, which consumes and produces
``"@"``. After this, the remaining, unconsumed ``"45@6"`` is given to the second ``fro.intp``, so it continues for each
of the composition's children parsers. The children parsers produces the values ``123``, ``"@"``, ``45``, ``"@"``, and
``6`` respectively, so the composition produces the tuple ``(123, "@", 45, "@", 6)``.


Parser significance
-------------------

Sometimes, when we compose multiple parsers together, some of the values produced by the children parsers are not important. In the above
example, we might only care about the three int values, and not about the delimiting ``"@"`` values.
To exclude some produced values from the resulting tuple of a composition, we can mark some of it's children as
insignificant::

    composition = fro.comp([fro.intp, -fro.rgx(r"@"), fro.intp, -fro.rgx(r"@"), fro.intp])
    composition.parse("123@45@6")  # returns the tuple (123, 45, 6)

Here, the ``-fro.rgx(r"@")`` evaluates to an insignificant version of the parser ``fro.rgx(r"@")``; for more on the syntax of marking parsers as
significant or insignificant, see :doc:`api`. What is important to notice is that the ``"@"`` value are not present in the tuple
value produced by ``composition``.

Parsers are significant by default. If a parser is insignificant, that only means that the values it produces will be ignored when it appears inside a
composition. An insignificant parser will still produce a value if you directly call ``parse(..)`` on it, or if it
appears in something other than a composition.
