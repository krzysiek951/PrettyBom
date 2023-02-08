from __future__ import annotations

import re
from functools import wraps
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from web_app.models import AbstractPart


def normalize_string(s):
    string = re.sub(r"[^\w\s]", ' ', s)
    string = re.sub(r"\s+", ' ', string)
    normalized_string = string.title().strip()
    return normalized_string


def get_number_delimiter(string: str) -> list[str]:
    """Returns all delimiters between numbers."""
    clean_string = string.strip()
    delimiters = list({char for char in clean_string if not char.isdigit()})
    return delimiters


def create_keyword_list(keywords: Union[str, list]):
    if not keywords:
        return None
    if isinstance(keywords, str):
        keywords = keywords.split(',')
    elif not isinstance(keywords, list):
        raise ValueError('Keywords must be of list or string type.')
    return [keyword.strip(' ') for keyword in keywords if keyword]


def part_modifier(f):
    """ Runs processing function through evert part in a part list """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.processor.processing_succeeded = False
        for part in self.processor.processed_part_list:
            f(self, part, *args, **kwargs)
        self.processor.processing_succeeded = True

    return wrapper


def type_sorter(part):
    parts_order = "pfjabcdeghiklmnoqrstuvwxyz"  # for ordering parts as: "production, purchased, fastener, junk"
    return [parts_order.index(c) for c in part.type]


def sort_by_type_and_number(part_list: list[AbstractPart]):
    """Returns a list of Parts sorted by 'Type' and 'Number'."""
    sorted_part_list = sorted(part_list, key=lambda part: (type_sorter(part), part.number), reverse=True)
    return sorted_part_list
