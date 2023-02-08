from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import AbstractBom


def get_first_imported_file(bom: AbstractBom) -> Optional[str]:
    """Returns the last imported file from the list of BOM import sources."""
    file_imports = [source for source in bom.imported_bom_sources if 'file' in source['type']]
    first_imported_file = file_imports[0]['name'] if file_imports else None
    return first_imported_file
