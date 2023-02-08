from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..assets.data.data import standard_fasteners
from ..functions import normalize_string
from ..functions.functions import create_keyword_list, part_modifier
from ..typing import PartTypes

if TYPE_CHECKING:
    from . import BomProcessor, AbstractPart


class ProcessorMethods:
    """Class that stores all the part list processing methods."""

    def __init__(self, processor: BomProcessor):
        self.processor = processor

    @part_modifier
    def set_parent(self, part: AbstractPart) -> None:
        """Returns a list of each Part's parent 'position number'."""
        parent = [item for item in self.processor.processed_part_list if item.id == part.parent_id]
        part.parent = parent[0] if parent else None

    @part_modifier
    def set_child(self, part: AbstractPart) -> None:
        """Returns a list of each child 'position number'."""
        child_list = [item for item in self.processor.processed_part_list if item.parent_id == part.id]
        part.child = child_list

    @part_modifier
    def set_sets(self, part: AbstractPart) -> None:
        """Returns the quantity of Part sets to order."""
        sets = self.processor.bom.main_assembly_sets
        current_part = part
        while current_part.parent:
            sets *= current_part.parent.quantity
            current_part = current_part.parent
        part.sets = sets

    @part_modifier
    def set_to_order(self, part: AbstractPart) -> None:
        """Returns the total quantity of the Part to order."""
        part.to_order = part.quantity * part.sets

    @part_modifier
    def set_file_type(self, part: AbstractPart) -> None:
        """Returns a file type of the Part."""
        part.file_type = 'assembly' if part.child and part.is_production else 'part'

    @part_modifier
    def set_type(self, part: AbstractPart) -> None:
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

    @part_modifier
    def set_is_production(self, part: AbstractPart) -> None:
        """Returns True if the Part is of 'production' type based on provided keywords."""
        keywords = create_keyword_list(self.processor.production_part_keywords)
        part.is_production = any(keyword in part.number for keyword in keywords) if keywords else False

    @part_modifier
    def set_is_fastener(self, part: AbstractPart) -> None:
        """Returns True if the Part is of 'fastener' type based on keywords."""
        name_split = [str(value).upper() for key, value in vars(part).items() if key != "parent" and key != "child"]
        norm_in_name = {norm: name for norm, value in standard_fasteners.items() for name in name_split if norm in name}
        is_part_fastener = False
        if norm_in_name:
            part_norm = next(iter(norm_in_name))
            part_name = norm_in_name[part_norm]
            part_numbers = [int(num) for num in re.findall(r'\d+', part_name)]
            is_part_fastener = any(x in part_numbers for x in standard_fasteners[part_norm])
        part.is_fastener = is_part_fastener

    @part_modifier
    def set_is_purchased(self, part: AbstractPart) -> None:
        """Returns True if the Part is of 'purchased' type. It could be only if it's not "production" or "fastener"."""
        part.is_purchased = True if not part.is_production and not part.is_fastener else False

    @part_modifier
    def set_parent_assembly(self, part: AbstractPart):
        part.parent_assembly = self.processor.bom.main_assembly_name if not part.parent else part.parent.number

    @part_modifier
    def set_is_junk_by_keywords(self, part: AbstractPart) -> None:
        """Returns True if the Part is of 'junk' type based by provided keywords."""
        keywords = create_keyword_list(self.processor.junk_part_keywords)
        is_junk = any(keyword in part.name or keyword in part.number for keyword in keywords) if keywords else False
        part.is_junk_by_keywords = is_junk

    @part_modifier
    def set_is_junk_by_empty_fields(self, part: AbstractPart) -> None:
        """Function that sets a part as "junk" if all specified fields are empty."""
        fields = create_keyword_list(self.processor.junk_part_empty_fields)
        part.is_junk_by_empty_fields = not any(getattr(part, field) for field in fields) if fields else False

    @part_modifier
    def set_is_junk_by_purchased_part_nesting(self, part: AbstractPart) -> None:
        """Returns True if the Part is nested in another Part that is not a 'Production' type."""
        part.is_junk_by_purchased_part_nesting = False if not part.parent or part.parent.is_production else True

    @part_modifier
    def set_is_junk(self, part: AbstractPart) -> None:
        """Returns True if any 'is_junk' condition is True."""
        is_junk = any([part.is_junk_by_keywords, part.is_junk_by_empty_fields, part.is_junk_by_purchased_part_nesting])
        part.is_junk = is_junk

    @part_modifier
    def set_normalized_names(self, part: AbstractPart) -> None:
        """Returns a Part with the normalized name of chosen BOM columns."""
        for key in self.processor.normalized_columns:
            if hasattr(part, key):
                normalized_name = normalize_string(getattr(part, key))
                setattr(part, key, normalized_name)
