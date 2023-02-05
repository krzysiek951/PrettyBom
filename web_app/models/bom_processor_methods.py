from __future__ import annotations

import math
import re
from functools import wraps
from typing import TYPE_CHECKING

from ..assets.data.data import standard_fasteners
from ..exceptions import AttrNotSetException, QuantityColumnIsNotDigit, DelimiterNotUnique
from ..functions import normalize_string
from ..functions.functions import get_number_delimiter
from ..typing import PartTypes, PartFileTypes

if TYPE_CHECKING:
    from . import BomProcessor, AbstractPart


def part_modifier(f):
    """ Runs processing function through evert part in a part list """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.processor.processing_succeeded = False
        for part in self.processor.processed_part_list:
            f(self, part, *args, **kwargs)
        self.processor.processing_succeeded = True

    return wrapper


class ProcessorMethods:
    """Class that stores all the part list processing methods."""

    def __init__(self, processor: BomProcessor):
        self.processor = processor

    def _get_pos_delimiter(self, part: AbstractPart) -> str:
        """" Returns Part's position unique delimiter. """
        position_delimiters = get_number_delimiter(self.get_part_position(part))
        delimiter = ' '.join(position_delimiters) if position_delimiters else None
        is_part_delimiter_unique = len(position_delimiters) <= 1
        current_set_delimiter = self.processor.part_position_delimiter
        if not delimiter:
            return delimiter
        if current_set_delimiter and current_set_delimiter != delimiter or not is_part_delimiter_unique:
            raise DelimiterNotUnique(current_set_delimiter, delimiter, part)
        else:
            self.processor.part_position_delimiter = delimiter
        return delimiter

    def get_part_position(self, part: AbstractPart) -> str:
        """Returns the 'Part position' attribute of the Part."""
        if not self.processor.part_position_column:
            raise AttrNotSetException('Processor must have the name of the "Part position" column set.')
        return getattr(part, self.processor.part_position_column)

    def get_part_number(self, part: AbstractPart) -> str:
        """Returns the 'Part number' attribute of the Part."""
        if not self.processor.part_number_column:
            raise AttrNotSetException('Processor must have the name of the "Part number" column set.')
        return getattr(part, self.processor.part_number_column)

    def get_part_quantity(self, part: AbstractPart) -> int:
        """Returns the 'Part quantity' attribute of the Part."""
        if not self.processor.part_quantity_column:
            raise AttrNotSetException('Processor must have the name of the "Part quantity" column set.')
        try:
            qty = int(getattr(part, self.processor.part_quantity_column))
        except ValueError as e:
            raise QuantityColumnIsNotDigit(part, self.processor.part_quantity_column) from e
        return qty

    def get_part_name(self, part: AbstractPart) -> str:
        """Returns the 'Part name' attribute of the Part."""
        if not self.processor.part_name_column:
            raise AttrNotSetException("Part name")
        return getattr(part, self.processor.part_name_column)

    def _get_position_split(self, part: AbstractPart) -> list[str]:
        """ Returns Part position split."""
        return self.get_part_position(part).split(self._get_pos_delimiter(part))

    def _get_parts_parent(self, part: AbstractPart) -> AbstractPart:
        """Returns the Part's parent."""
        parent = None
        if part.parent:
            parent_id = part.parent[-1]
            parent = self._get_parent_by_id(part_id=parent_id)
        return parent

    def _get_parent_by_id(self, part_id: str) -> AbstractPart:
        """Returns the Part's parent by its 'Position number'."""
        parent = [part for part in self.processor.processed_part_list if self.get_part_position(part) == part_id][0]
        return parent

    @part_modifier
    def set_parent(self, part: AbstractPart):
        """Returns a list of each Part's parent 'position number'."""
        pos_delimiter = self._get_pos_delimiter(part)
        position_split = self.get_part_position(part).split(pos_delimiter)
        parents_count = len(position_split) - 1
        parents_id = [pos_delimiter.join(position_split[:(parent + 1)]) for parent in range(parents_count)]
        part.parent = parents_id

    @part_modifier
    def set_parent_assembly(self, part: AbstractPart) -> str:
        """Returns the 'Part number' of the Part's first parent."""
        parent = self._get_parts_parent(part)
        if parent:
            parent_name = self.get_part_number(parent)
        else:
            parent_name = self.processor.bom.main_assembly_name
        part.parent_assembly = parent_name
        return parent_name

    @part_modifier
    def set_child(self, part: AbstractPart) -> list:
        """Returns a list of each child 'position number'."""
        part_position_split = self._get_position_split(part)
        part_len = len(part_position_split)
        child_len = part_len + 1
        child_id = []
        for item in self.processor.processed_part_list:
            has_child_len = len(self._get_position_split(item)) == child_len
            has_same_pos_split = self._get_position_split(item)[:part_len] == part_position_split
            child_id.append(self.get_part_position(item)) if has_child_len and has_same_pos_split else None
        part.child = child_id
        return child_id

    @part_modifier
    def set_sets(self, part: AbstractPart) -> int:
        """Returns the Part sets quantity to order."""
        parent_sets = []
        for instance in self.processor.processed_part_list:
            for parent in part.parent:
                if self.get_part_position(instance) == parent:
                    parent_sets.append(self.get_part_quantity(instance))
        sub_sets = math.prod(parent_sets)
        sets = sub_sets * self.processor.bom.main_assembly_sets
        part.sets = sets
        return sets

    @part_modifier
    def set_to_order(self, part: AbstractPart) -> int:
        """Returns the total quantity of the Part to order."""
        part_quantity = self.get_part_quantity(part)
        to_order = part_quantity * part.sets
        part.to_order = to_order
        return to_order

    @part_modifier
    def set_file_type(self, part: AbstractPart, **_) -> PartFileTypes:
        """Returns a file type of the Part."""
        file_type: PartFileTypes = 'part'
        if len(part.child) > 0 and part.type == 'production':
            file_type = 'assembly'
        part.file_type = file_type
        return file_type

    @part_modifier
    def set_type(self, part: AbstractPart) -> PartTypes:
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

    @part_modifier
    def set_is_production(self, part: AbstractPart) -> bool:
        """Returns True if the Part is of 'production' type based on provided keywords."""
        is_part_production = False
        keywords_split = self.processor.production_part_keywords
        if isinstance(self.processor.production_part_keywords, str):
            keywords_split = self.processor.production_part_keywords.split(',')
        filtered_keywords = list(filter(None, keywords_split))
        keywords = [keyword.strip(' ') for keyword in filtered_keywords]
        if keywords:
            is_part_production = any(
                keyword in self.get_part_number(part) for keyword in keywords)
        part.is_production = is_part_production
        return is_part_production

    @part_modifier
    def set_is_fastener(self, part: AbstractPart, **__) -> bool:
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

    @part_modifier
    def set_is_purchased(self, part: AbstractPart, **_) -> bool:
        """Returns True if the Part is of 'purchased' type. It could be only if it's not "production" or "fastener"."""
        is_part_purchased = True if not part.is_production and not part.is_fastener else False
        part.is_purchased = is_part_purchased
        return is_part_purchased

    @part_modifier
    def set_is_junk_by_keywords(self, part: AbstractPart) -> bool:
        """Returns True if the Part is of 'junk' type based by provided keywords."""
        is_junk = False
        junk_keywords = self.processor.junk_part_keywords
        keywords_split = junk_keywords.split(',') if isinstance(junk_keywords, str) else junk_keywords
        filtered_keywords = list(filter(None, keywords_split))
        keywords = [keyword.strip(' ') for keyword in filtered_keywords]
        if keywords:
            is_junk = any(f in (self.get_part_number(part) or self.get_part_name(part)) for f in keywords)
        part.is_junk_by_keywords = is_junk
        return is_junk

    @part_modifier
    def set_is_junk_by_empty_fields(self, part: AbstractPart) -> bool:
        """Function that sets a part as "junk" if all specified fields are empty."""
        is_junk = False
        fields = self.processor.junk_part_empty_fields
        fields_split = fields.split(',') if isinstance(fields, str) else fields
        filtered_fields = list(filter(None, fields_split))
        fields = [keyword.strip(' ') for keyword in filtered_fields]
        if fields:
            is_junk = not any(getattr(part, key) for key in fields)
        part.is_junk_by_empty_fields = is_junk
        return is_junk

    @part_modifier
    def set_is_junk_by_purchased_part_nesting(self, part: AbstractPart) -> bool:
        """Returns True if the Part is nested in another Part that is not a 'Production' type."""
        is_junk = False
        if self.processor.set_junk_for_purchased_nests:
            if part.parent:
                parent = self._get_parent_by_id(part.parent[-1])
                is_junk = False if parent.is_production else True
        part.is_junk_by_purchased_part_nesting = is_junk
        return is_junk

    @part_modifier
    def set_is_junk(self, part: AbstractPart) -> bool:
        """Returns True if any 'is_junk' condition is True."""
        is_junk = any([part.is_junk_by_keywords, part.is_junk_by_empty_fields, part.is_junk_by_purchased_part_nesting])
        part.is_junk = is_junk
        return is_junk

    @part_modifier
    def set_normalized_names(self, part: AbstractPart) -> AbstractPart:
        """Returns a Part with the normalized name of chosen BOM columns."""
        for key in self.processor.normalized_columns:
            if hasattr(part, key):
                normalized_name = normalize_string(getattr(part, key))
                setattr(part, key, normalized_name)
        return part

    def _get_sub_bom(self, part: AbstractPart) -> list[AbstractPart]:
        """Returns a list of Parts in Assembly."""
        part_len = len(part.parent) + 1
        child_len = len(part.parent) + 2
        parts_order = "pfjabcdeghiklmnoqrstuvwxyz"  # for ordering parts as: "production, purchased, fastener, junk"
        part_list = self.processor.processed_part_list
        sub_bom = [item for item in part_list if len(item.parent) + 1 == child_len and
                   self._get_position_split(item)[:part_len] == self._get_position_split(part)]
        sub_bom = sorted(sub_bom, key=lambda word: ([parts_order.index(c) for c in word.type],
                                                    self.get_part_number(word)), reverse=True)
        return sub_bom

    def set_tree_sorting(self) -> None:
        """Converts BOM to a tree list."""
        part_list = self.processor.processed_part_list
        initial_bom_tree_list = [part for part in part_list if len(self._get_position_split(part)) == 1]
        bom_tree_list = sorted(initial_bom_tree_list, key=lambda part: self.get_part_number(part), reverse=False)
        last_generation = 20
        for generation in range(1, last_generation):
            for part in bom_tree_list:
                part_generation = len(self._get_position_split(part))
                if part_generation == generation:
                    child_bom = sorted(self._get_sub_bom(part), key=lambda d: self.processor.part_number_column,
                                       reverse=False)
                    for item in child_bom:
                        bom_tree_list.insert(bom_tree_list.index(part) + 1, item)
        self.processor.processed_part_list = bom_tree_list
