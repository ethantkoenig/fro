Fro
===

Fro is a Python module for parsing strings and text into Python objects. It
offers a concise, declarative, and expressive interface for mapping strings to
data, abstracting away boilerplate code and making it easy to quickly write
bug-free parsers.

Fro is compatible with Python 2.7+ and Python 3.x, and can be installed via pip.
Documentation for the module can be found at `<http://pythonhosted.org/fro>`_.

Release Notes
-------------

2.0.0: (08-01-16)
~~~~~~~~~~~~~~~~~

Breaking changes:
* Parse input by chunks, allowing for more efficient use of memory
* Replace ``parse()`` method of Parser objects with family of related parsing
  functions
* Change interface of ``FroParseError`` to better accommodate chunks

Non-breaking changes:
* New factory functions for constructing parsers
* Various performance improvements


1.1.0: (07-08-16)
~~~~~~~~~~~~~~~~

Initial release. Versioning begins at 1.1.0 due to a clerical error.
