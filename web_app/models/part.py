from __future__ import annotations

from abc import ABC


class AbstractPart(ABC):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.sets = None
        self.to_order = None
        self.parent = None
        self.child = None
        self.parent_assembly = None
        self.assembly_number = None
        self.assembly_name = None
        self.type = None  # TODO: ADD LITERAL
        self.file_type = None  # TODO: ADD LITERAL
        self.is_fastener = None
        self.is_purchased = None
        self.is_production = None
        self.is_junk_by_keywords = None
        self.is_junk_by_empty_fields = None
        self.is_junk_by_purchased_part_nesting = None
        self.is_junk = None


class DefaultPart(AbstractPart):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
