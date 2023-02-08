from __future__ import annotations

from abc import ABC
from typing import Optional

from web_app.exceptions import AttrNotSetException, QuantityColumnIsNotDigit, DelimiterNotUnique
from web_app.functions.functions import get_number_delimiter
from web_app.typing import PartTypes, PartFileTypes, PartClassTypes


class AbstractPart(ABC):
    """Abstract class for a Part."""
    part_type: PartClassTypes = None

    def __init__(self, **kwargs):
        self.sets: int | None = None
        self.to_order: int | None = None
        self.parent: AbstractPart | None = None
        self.child: list[AbstractPart] | None = None
        self.parent_assembly: str | None = None
        self.type: PartTypes | None = None
        self.file_type: PartFileTypes | None = None
        self.is_fastener: bool | None = None
        self.is_purchased: bool | None = None
        self.is_production: bool | None = None
        self.is_junk_by_keywords: bool | None = None
        self.is_junk_by_empty_fields: bool | None = None
        self.is_junk_by_purchased_part_nesting: bool | None = None
        self.is_junk: bool | None = None

        self._position_column: str = ''
        self._quantity_column: str = ''
        self._number_column: str = ''
        self._name_column: str = ''
        self.__dict__.update(kwargs)

    def __str__(self):
        return f'{self.part_type} Part: {self.number} {self.name}'

    def __repr__(self):
        return f'{self.number} {self.name}'

    @property
    def position(self) -> str:
        """Returns the 'Part position' attribute of the Part."""
        if not self._position_column:
            raise AttrNotSetException('Part position')
        return getattr(self, self._position_column)

    @property
    def number(self) -> str:
        """Returns the 'Part number' attribute of the Part."""
        if not self._number_column:
            raise AttrNotSetException('Part number')
        return getattr(self, self._number_column)

    @property
    def quantity(self) -> int:
        """Returns the 'Part quantity' attribute of the Part."""
        if not self._quantity_column:
            raise AttrNotSetException('Part quantity')
        try:
            qty = int(getattr(self, self._quantity_column))
        except ValueError as e:
            raise QuantityColumnIsNotDigit(self, self._quantity_column) from e
        return qty

    @property
    def name(self) -> str:
        """Returns the 'Part name' attribute of the Part."""
        if not self._name_column:
            raise AttrNotSetException('Part name')
        return getattr(self, self._name_column)

    def get_pos_delimiter(self) -> str:
        """" Returns Part's position unique delimiter. """
        position_delimiters = get_number_delimiter(self.position)
        delimiter = ' '.join(position_delimiters) if position_delimiters else None
        is_part_delimiter_unique = len(position_delimiters) <= 1
        if not is_part_delimiter_unique:
            raise DelimiterNotUnique(self, delimiter)
        return delimiter

    @property
    def parent_id(self) -> Optional[str]:
        """ Returns Part parent id."""
        delimiter = self.get_pos_delimiter()
        return delimiter.join(self.position.split(delimiter)[:-1]) if delimiter else None

    @property
    def id(self) -> str:
        """ Returns Part id."""
        return self.position


class DefaultPart(AbstractPart):
    """Class for default type of the Part."""
    part_type: PartClassTypes = 'default'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
