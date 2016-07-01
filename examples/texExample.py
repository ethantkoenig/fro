import fro

class TexElement(object):
    pass

class TexCommand(TexElement):
    def __init__(self, name, content=None):
        self.name = name
        self.content = content

    def __str__(self):
        if self.content is None:
            return "\%s" % self.name
        return "\%s{%s}" % (self.name, self.content)

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

textp = fro.rgx(r"[^\\\s]+", name="TeX text") | TexText
cmdbasep = fro.group_rgx(r"\\([^\{\s]+)").get()
cmdcontentp = fro.group_rgx(r"\{([^\}]*?)\}").get().maybe()
commandp = fro.comp([cmdbasep, cmdcontentp], name="TeX command") >> TexCommand
elementp = fro.alt([commandp, textp])
documentp = fro.seq(elementp, sep=r" ", name="Tex document") | TexDocument
