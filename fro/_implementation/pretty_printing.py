"""
Various pretty-printing and string-formatting utilities
"""


def printable_string_index_with_context(string, index, context_len=50, max_len=80):
    """
    :param string: string
    :param index: index of string of interest
    :param context_len: length of context sections
    :param max_len: max length of lines in result
    :return: A pretty-printable string showing the specified substring along with before
        and after context
    """
    before_str = string[max(0, index - context_len):index]
    after_str = string[index:min(len(string), index + context_len)]

    lines = [
        "(strings shown with quotes, long contents may be replaced with ...)",
        "BEFORE:",
        _printable_string(before_str, max_len),
        "AFTER:",
        _printable_string(after_str, max_len)
    ]
    return "\n".join(lines)


def _printable_string(string, max_len=80):
    """
    :param string: string
    :param max_len: maximum length
    :return: printable version of the given string adhering to the maximum length
    """
    if max_len < 3:
        raise ValueError("max_len is {0}, must be at least 3".format(max_len))
    repred_str = repr(string)
    if len(repred_str) < max_len:
        return repred_str
    offset = (max_len - 3) // 2
    return repred_str[:offset] + "..." + repred_str[-offset:]
