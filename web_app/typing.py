from typing import Literal, TypedDict

HeaderPositions = Literal['top', 'bottom']
ImportedBomSourceTypes = Literal['file']
BomManagerClassTypes = Literal['default']
BomClassTypes = Literal['default']
PartClassTypes = Literal['default']
PartTypes = Literal['production', 'purchased', 'fastener', 'junk']
PartFileTypes = Literal['part', 'assembly']


class ImportedBomSource(TypedDict):
    """Class defining the source representation."""
    type: ImportedBomSourceTypes
    name: str
