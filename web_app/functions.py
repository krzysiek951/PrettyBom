import re


def normalize_string(s):
    string = re.sub(r"[^\w\s]", ' ', s)
    string = re.sub(r"\s+", ' ', string)
    return string
