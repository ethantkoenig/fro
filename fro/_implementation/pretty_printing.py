"""
Various pretty-printing and string-formatting utilities
"""

import pprint


class PrintableString(object):

    def __init__(self, string_to_print):
        self._escaped_string, self._indices = self._escape(string_to_print)

    def string(self):
        return self._escaped_string

    def round_raw_index_up(self, index):
        return min(i for i in self._indices if i >= index)

    def round_raw_index_down(self, index):
        return max(i for i in self._indices if i <= index)

    def raw_index_of_char(self, index):
        return self._indices[index]

    def length_of(self, index):
        return self._indices[index + 1] - self._indices[index]

    def substring(self, start_index, end_index, max_length=80):
        raw_start = self._indices[start_index]
        raw_end = self._indices[end_index]
        if raw_end - raw_start <= max_length:
            return self._escaped_string[raw_start:raw_end]
        offset = (max_length - 4) / 2
        raw_mid1 = self.round_raw_index_down(raw_start + offset)
        raw_mid2 = self.round_raw_index_up(raw_end - offset)
        return self._escaped_string[raw_start:raw_mid1] + "..."\
               + self._escaped_string[raw_mid2:raw_end]

    @staticmethod
    def _escape(s):
        """
        :param s: string to escape
        :return: escaped string, list of raw indices indexed by char indices
        """
        escaped_chars = []
        indices = []
        len_so_far = 0
        for char in s:
            escaped_char = pprint.pformat(char)[1:-1]
            escaped_chars.append(escaped_char)
            indices.append(len_so_far)
            len_so_far += len(escaped_char)
        indices.append(len_so_far)
        return "".join(escaped_chars), indices
