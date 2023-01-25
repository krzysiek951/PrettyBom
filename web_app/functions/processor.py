from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from .functions import normalize_string
from ..assets.data.data import standard_fasteners
from ..typing import PartTypes, PartFileTypes

if TYPE_CHECKING:
    from ..models import AbstractBomProcessor
    from ..models import AbstractPart


def normalize_name(processor: AbstractBomProcessor, part: AbstractPart) -> AbstractPart:
    """Returns a Part with the normalized name of chosen BOM columns."""

    for key in processor.normalized_columns:
        if hasattr(part, key):
            normalized_name = normalize_string(getattr(part, key))
            setattr(part, key, normalized_name)

    return part


def get_parent_assembly(processor: AbstractBomProcessor, part: AbstractPart) -> str:
    """Returns the 'Part number' of the Part's first parent."""

    parent = get_parent(processor, part)
    if parent:
        parent_name = getattr(parent, processor.part_number_column)
    else:
        parent_name = processor.bom.main_assembly_name
    part.parent_assembly = parent_name

    return parent_name


def get_parent_ids(processor: AbstractBomProcessor, part: AbstractPart) -> list[str]:
    """Returns a list of each Part's parent 'position number'."""

    position_split = getattr(part, processor.part_position_column).split(processor.part_position_delimiter)
    parents_count = len(position_split) - 1
    parents_id = [processor.part_position_delimiter.join(position_split[:(num + 1)]) for num in range(parents_count)]
    part.parent = parents_id

    return parents_id


def get_parent(processor: AbstractBomProcessor, part: AbstractPart) -> AbstractPart:
    """Returns the Part's parent."""
    parent = None

    if part.parent:
        parent_id = part.parent[-1]
        parent = get_parent_by_id(processor=processor, part_id=parent_id)

    return parent


def get_parent_by_id(processor: AbstractBomProcessor, part_id: str) -> AbstractPart:
    """Returns the Part's parent by its 'Position number'."""

    parent = [part for part in processor.initial_part_list if getattr(part, processor.part_position_column) == part_id][
        0]

    return parent


def get_child_ids(processor: AbstractBomProcessor, part: AbstractPart) -> list:
    """Returns a list of each child 'position number'."""

    position_split = getattr(part, processor.part_position_column).split(processor.part_position_delimiter)
    part_len = len(position_split)
    child_len = part_len + 2
    child_id = [getattr(item, processor.part_position_column) for item in processor.initial_part_list if
                len(getattr(item, processor.part_position_column).split(
                    processor.part_position_delimiter)) + 1 == child_len and
                getattr(item, processor.part_position_column).split(processor.part_position_delimiter)[
                :part_len] == position_split]
    part.child = child_id

    return child_id


def get_file_type(part: AbstractPart, **_) -> PartFileTypes:
    """Returns a file type of the Part."""

    file_type: PartFileTypes = 'part'

    if len(part.child) > 0 and part.type == 'production':
        file_type = 'assembly'
    part.file_type = file_type

    return file_type


def get_sets(processor: AbstractBomProcessor, part: AbstractPart) -> int:
    """Returns the Part sets quantity to order."""

    parent_sets = []

    for instance in processor.initial_part_list:
        for parent in part.parent:
            if getattr(instance, processor.part_position_column) == parent:
                parent_sets.append(int(getattr(instance, processor.part_quantity_column)))
    sub_sets = math.prod(parent_sets)
    sets = sub_sets * processor.bom.main_assembly_sets
    part.sets = sets

    return sets


def get_to_order(processor: AbstractBomProcessor, part: AbstractPart) -> int:
    """Returns the total quantity of the Part to order."""

    part_quantity = int(getattr(part, processor.part_quantity_column))
    to_order = part_quantity * part.sets
    part.to_order = to_order

    return to_order


def get_type(part: AbstractPart, **_) -> PartTypes:
    """Returns the type of the Part."""

    part_type: PartTypes | None = None

    if part.is_junk:
        part_type = 'junk'
    elif part.is_production:
        part_type = 'production'
    elif part.is_fastener:
        part_type = 'fastener'
    elif part.is_purchased:
        part_type = 'purchased'
    part.type = part_type

    return part_type


def is_production(processor: AbstractBomProcessor, part: AbstractPart) -> bool:
    """Returns True if the Part is of 'production' type based on provided keywords."""

    is_part_production = False
    keywords_split = processor.production_part_keywords

    if isinstance(processor.production_part_keywords, str):
        keywords_split = processor.production_part_keywords.split(',')
    filtered_keywords = list(filter(None, keywords_split))
    keywords = [keyword.strip(' ') for keyword in filtered_keywords]
    if keywords:
        is_part_production = any(
            keyword in getattr(part, processor.part_number_column) for keyword in keywords)
    part.is_production = is_part_production

    return is_part_production


def is_fastener(part: AbstractPart, **__) -> bool:
    """Returns True if the Part is of 'fastener' type based on keywords."""

    name_split = [str(value).upper() for key, value in vars(part).items()]
    norm_in_name = {norm: name for norm, value in standard_fasteners.items() for name in name_split if norm in name}
    is_part_fastener = False
    if norm_in_name:
        part_norm = next(iter(norm_in_name))
        part_name = norm_in_name[part_norm]
        part_numbers = [int(num) for num in re.findall(r'\d+', part_name)]
        is_part_fastener = any(x in part_numbers for x in standard_fasteners[part_norm])
    part.is_fastener = is_part_fastener

    return is_part_fastener


def is_purchased(part: AbstractPart, **_) -> bool:
    """Returns True if the Part is of 'purchased' type. It could be only if it's not "production" or "fastener"."""

    is_part_purchased = True if not part.is_production and not part.is_fastener else False
    part.is_purchased = is_part_purchased

    return is_part_purchased


def is_junk_by_keywords(processor: AbstractBomProcessor, part: AbstractPart) -> bool:
    """Returns True if the Part is of 'junk' type based by provided keywords."""

    is_part_junk_by_keywords = False

    keywords_split = processor.junk_part_keywords.split(',') if isinstance(processor.junk_part_keywords, str) \
        else processor.junk_part_keywords
    filtered_keywords = list(filter(None, keywords_split))
    keywords = [keyword.strip(' ') for keyword in filtered_keywords]
    if keywords:
        is_part_junk_by_keywords = any(
            f in (getattr(part, processor.part_number_column) or getattr(part, processor.part_name_column)) for f in
            keywords)
    part.is_junk_by_keywords = is_part_junk_by_keywords

    return is_part_junk_by_keywords


def is_junk_by_empty_fields(processor: AbstractBomProcessor, part: AbstractPart) -> bool:
    """Function that sets a part as "junk" if all specified fields are empty."""

    is_part_junk_by_empty_fields = False
    fields_split = processor.junk_part_empty_fields.split(',') if isinstance(processor.junk_part_empty_fields,
                                                                             str) else processor.junk_part_empty_fields
    filtered_fields = list(filter(None, fields_split))
    fields = [keyword.strip(' ') for keyword in filtered_fields]

    if fields:
        is_part_junk_by_empty_fields = not any(getattr(part, key) for key in fields)
    part.is_junk_by_empty_fields = is_part_junk_by_empty_fields

    return is_part_junk_by_empty_fields


def is_junk_by_purchased_part_nesting(processor: AbstractBomProcessor, part: AbstractPart) -> bool:
    """Returns True if the Part is nested in another Part that is not a 'Production' type."""

    is_part_junk_by_purchased_part_nesting = False
    if processor.set_junk_for_purchased_nests:
        if part.parent:
            parent_id = part.parent[-1]
            parent = get_parent_by_id(processor, parent_id)
            is_part_junk_by_purchased_part_nesting = not is_production(processor, parent)
    part.is_junk_by_purchased_part_nesting = is_part_junk_by_purchased_part_nesting

    return is_part_junk_by_purchased_part_nesting


def is_junk(part: AbstractPart, **_) -> bool:
    """Returns True if any 'is_junk' condition is True."""

    is_part_junk = any([part.is_junk_by_keywords, part.is_junk_by_empty_fields, part.is_junk_by_purchased_part_nesting])
    part.is_junk = is_part_junk

    return is_part_junk


def get_sub_bom(processor: AbstractBomProcessor, part: AbstractPart, part_list: list[AbstractPart]) -> \
        list[AbstractPart]:
    """Returns a list of Parts in Assembly."""

    name_split = getattr(part, processor.part_position_column).split(processor.part_position_delimiter)
    part_len = len(getattr(part, "parent")) + 1
    child_len = len(getattr(part, "parent")) + 2
    parts_order = "pfjabcdeghiklmnoqrstuvwxyz"
    # implemented for ordering parts as: "production, purchased, fastener, junk

    sub_bom = [item for item in part_list if len(getattr(item, "parent")) + 1 == child_len and
               getattr(item, processor.part_position_column).split(processor.part_position_delimiter)[
               :part_len] == name_split]
    sub_bom = sorted(sub_bom,
                     key=lambda word: ([parts_order.index(c) for c in word.type],
                                       getattr(word, processor.part_number_column)), reverse=True)

    return sub_bom


def create_bom_tree_list(processor: AbstractBomProcessor, part_list: list[AbstractPart]) -> list[AbstractPart]:
    """Returns a tree list of a BOM."""

    bom_tree_list = [part for part in part_list if
                     len(getattr(part, processor.part_position_column).split(processor.part_position_delimiter)) == 1]
    bom_tree_list = sorted(bom_tree_list, key=lambda d: getattr(d, processor.part_number_column), reverse=False)
    last_generation = 20
    for generation in range(1, last_generation):
        for part in bom_tree_list:
            child_generation = len(
                getattr(part, processor.part_position_column).split(processor.part_position_delimiter))
            if child_generation == generation:
                child_bom = sorted(get_sub_bom(processor, part, part_list), key=lambda d: processor.part_number_column,
                                   reverse=False)
                for item in child_bom:
                    bom_tree_list.insert(bom_tree_list.index(part) + 1, item)

    return bom_tree_list
