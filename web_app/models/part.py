from __future__ import annotations

from abc import ABC

from web_app.typing import PartTypes, PartFileTypes, PartClassTypes


class AbstractPart(ABC):
    """Abstract class for a Part."""
    part_type: PartClassTypes = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.sets: int | None = None
        self.to_order: int | None = None
        self.parent: list[str] | None = None
        self.child: list[str] | None = None
        self.parent_assembly: str | None = None
        self.assembly_number: str | None = None
        self.assembly_name: str | None = None
        self.type: PartTypes | None = None
        self.file_type: PartFileTypes | None = None
        self.is_fastener: bool | None = None
        self.is_purchased: bool | None = None
        self.is_production: bool | None = None
        self.is_junk_by_keywords: bool | None = None
        self.is_junk_by_empty_fields: bool | None = None
        self.is_junk_by_purchased_part_nesting: bool | None = None
        self.is_junk: bool | None = None

    def __str__(self):
        return f'{self.part_type} Part: {self.__dict__}'

    def __repr__(self):
        return f'{self.__dict__}'


class DefaultPart(AbstractPart):
    """Class for default type of the Part."""
    part_type: PartClassTypes = 'default'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
