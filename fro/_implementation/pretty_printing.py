"""
Various pretty-printing and string-formatting utilities
"""


def printable_substring_with_context(string, start_index, end_index, context_len=50, max_len=80):
    """
    :param string: string
    :param start_index: start index of substring
    :param end_index: end index of substring
    :param context_len: length of context sections
    :param max_len: max length of lines in result
    :return: A pretty-printable string showing the specified substring along with before
        and after context
    """
    before_str = string[max(0, start_index - context_len):start_index]
    sub_str = string[start_index:end_index]
    end_str = string[end_index:min(len(string), end_index + context_len)]

    lines = [
        "(strings shown with quotes, long contents may be replaced with ...)",
        "CONTEXT (BEFORE):",
        _printable_string(before_str, max_len),
        "SUBSTRING:",
        _printable_string(sub_str, max_len),
        "CONTEXT (AFTER):",
        _printable_string(end_str, max_len)
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
