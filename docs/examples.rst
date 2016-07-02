



Examples
========


Example 1: Email Addresses
--------------------------

Suppose you are given a text file where each line is of the form:

  <first name> <last name> : <email address>

Unfortunately for you, the file is rather sloppy; sometimes there is no whitespace between the last name and the colon,
other times there are multiple spaces. There are some blank lines, and there are some lines with multiple entries. You
need generate an ``EmailDirectory`` object from this file::

    class EmailAddress(object):
        def __init__(self, local_name, domain):
            self.local_name = local_name
            self.domain = domain

        def __str__(self):
            return "{loc}@{dom}".format(loc=self.local_name, dom=self.domain)


    class Name(object):
        def __init__(self, first, last):
            self.first = first
            self.last = last

        def __str__(self):
            return "{f} {l}".format(f=self.first, l=self.last)


    class EmailDirectory(object):
        def __init__(self, entries):  # entries: (Name, EmailAddress) iterator
            self.entries = dict(entries) # dict from Name to EmailAddress

        def __str__(self):
            entry_strings = ("{n} : {a}".format(n=name, a=addr) for (name, addr) in self.entries.items())
            return "\n".join(entry_strings)

Using fro, you can write code for parsing the text file in under ten lines::

    # email address ::= <local name>@<domain>, where <domain> is <something>.<something>
    emailaddrp = fro.comp([r"[\w]+", r"~@", r"[\w]+\.[\w]+"], name="email address")\
                     .strip() >> EmailAddress
    firstnamep = fro.rgx(r"[\w]+", name="first name").strip()
    lastnamep = firstnamep.name("last name")
    namep = fro.comp([firstnamep, lastnamep], name="full name") >> Name
    # entry ::= <full name> : <email address>
    entryp = fro.comp([namep, r"~:", emailaddrp], name="directory entry")
    emaildirp = fro.seq(entryp, name="directory") | EmailDirectory

    with open("input.txt", "r") as input_file:
        return emaildirp.parse(input_file.read())

Not only will this code exhibit the desired behavior, it will raise informative error messages when it encounters
misformatted input.

