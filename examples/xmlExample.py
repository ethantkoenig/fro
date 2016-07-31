import fro
import re


class XmlNode(object):
    def __init__(self, tag, text, children, tail):
        self._tag = tag
        self._text = text  # text appearing inside the node
        self._children = children  # list of XmlNodes
        self._tail = tail  # text appearing immediately after the node


# Recognizes <open> tags, producing the tag name
open_tagp = fro.rgx(r"\w+",name="open tag").prepend(r"<").append(r">")


def close_of_tag(tag_name):
    # Regex for the </close> tag of a given tag name
    return re.escape("</{}>".format(tag_name))


def xml_node_parser(recursive_parser):
    tag = fro.BoxedValue(None)  # stores the tag name of the current XML node
    boxed_open_tagp = open_tagp.lstrips() | tag.update_and_get
    textp = fro.until(r"<", reducer="".join, name="text")
    childrenp = fro.seq(recursive_parser)
    tailp = textp.name("tail")
    boxed_close_tagp = fro.thunk(lambda: close_of_tag(tag.get()), name="close_tag")
    return fro.comp([boxed_open_tagp, textp,
                     childrenp, ~boxed_close_tagp, tailp]) >> XmlNode


xmlp = fro.chain(xml_node_parser)
