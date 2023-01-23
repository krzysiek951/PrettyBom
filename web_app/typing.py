from typing import Literal, TypedDict

HeaderPositions = Literal['top', 'bottom']
ImportedBomSourceTypes = Literal['file']


class ImportedBomSource(TypedDict):
    """Class defining the source representation."""
    type: ImportedBomSourceTypes
    name: str
