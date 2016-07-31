
Introduction to Fro
===================

Overview
--------

Fro is a Python module for parsing strings and text into Python objects. It
offers a concise, declarative, and expressive interface for mapping strings to
data, abstracting away boilerplate code and making it easy to quickly write
bug-free parsers.

Fro is compatible with Python 2.7+ and Python 3+, and can be found on the
`Python Package Index <http://pypi.python.org/>`_.

Motivation
----------
It is relatively simple to create string representations of objects, or to
serialize objects into a readable, textual format. Overloaded ``__str__()`` methods
usually contain a few lines of hard-to-mess-up code.

On the other hand, writing code for turning string representations back into
the objects that they represent can be tricky. This code is commonly error-prone,
boilerplate, and distracts from a program's higher-level goals. Fro allows
programmers to quickly write clean, expressive and maintainable parsing code.

Additionally, Fro provides informative error messages for easily diagnosing and
correcting parsing issues.

Installation
------------

The easiest way to install Fro is via `pip <http://pypi.python.org/pypi/pip>`_::

  $ pip install fro

You can also download the source from `Github <http://github.com/ethantkoenig/fro/>`_.