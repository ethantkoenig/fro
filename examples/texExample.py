import fro


class TexElement(object):
    pass  # "abstract" parent class


class TexCommand(TexElement):
    def __init__(self, name, argument=None):
        self.name = name
        self.argument = argument

    def __str__(self):
        if self.argument is None:
            return "\%s" % self.name
        return "\%s{%s}" % (self.name, self.argument)


class TexText(TexElement):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class TexDocument(object):
    def __init__(self, elements):
        self.elements = elements

    def __str__(self):
        return " ".join(str(e) for e in self.elements)


# parser for TexText objects
textp = fro.rgx(r"[^\\s]+", name="TeX text") | TexText

# parser for TexCommand objects
namep = fro.group_rgx(r"\\([^\{\s]+)").get()
argumentp = fro.group_rgx(r"\{([^\}]*?)\}").get().maybe()
commandp = fro.comp([namep, argumentp], name="TeX command") >> TexCommand

# parser for TexDocument objects
elementp = fro.alt([commandp, textp]).strips()
documentp = fro.seq(elementp, name="Tex document") | TexDocument
