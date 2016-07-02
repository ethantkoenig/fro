import fro


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
        self.entries = dict(entries)

    def __str__(self):
        entry_strings = ("{n} : {a}".format(n=name, a=addr) for (name, addr) in self.entries.items())
        return "\n".join(entry_strings)


emailaddrp = fro.comp([r"[\w]+", r"~@", r"[\w]+\.[\w]+"], name="email address")\
                 .strip() >> EmailAddress
firstnamep = fro.rgx(r"[\w]+", name="first name").strip()
lastnamep = firstnamep.name("last name")
namep = fro.comp([firstnamep, lastnamep], name="full name") >> Name
entryp = fro.comp([namep, r"~:", emailaddrp], name="directory entry")
emaildirp = fro.seq(entryp, name="directory") | EmailDirectory
