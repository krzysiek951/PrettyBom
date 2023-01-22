from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from web_app.models import AbstractBom, AbstractPart


class AbstractBomExporter(ABC):
    """Abstract class for exporting a part list to a various file types."""

    def __init__(self):
        self.exported_filename: str = ''

    @abstractmethod
    def _save(self, part_list: list[AbstractPart], exported_columns: list, filename_without_extension: str,
              exports_pathname: str):
        """Creates a file with a part list."""
        ...

    def export_part_list(self, bom: AbstractBom, exported_columns: list, exports_pathname: str,
                         filename: Optional[str] = None) -> None:
        """Exports the part list to a file."""
        exported_filename = 'PrettyBom - Bill of materials'
        if not filename:
            last_imported_file = self._get_first_imported_file(bom)
            if last_imported_file:
                exported_filename = last_imported_file.rsplit('.', 1)[0]
        self._save(bom.part_list, exported_columns, exported_filename, exports_pathname=exports_pathname)

    @staticmethod
    def _get_first_imported_file(bom: AbstractBom) -> Optional[str]:
        """Returns the last imported file from the list of BOM import sources."""
        file_imports = [source for source in bom.imported_bom_sources if 'file' in source['type']]
        first_imported_file = file_imports[0]['name'] if file_imports else None
        return first_imported_file


class BomXlsxExporter(AbstractBomExporter):
    """Class for exporting a part list to the xlsx file."""

    def _save(self, part_list: list[AbstractPart], exported_columns: list, filename_without_extension: str,
              exports_pathname: str):
        df = pd.DataFrame(map(vars, part_list), columns=exported_columns)
        df.columns = df.columns.str.replace('_', ' ').str.capitalize()

        self.exported_filename = f'{filename_without_extension}.xlsx'
        exported_file_path = f'{exports_pathname}{self.exported_filename}'
        df.to_excel(exported_file_path, index=False, header=True)
        print(f"Exported {len(df)} parts to file: {self.exported_filename}.")
