from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from web_app.functions import get_first_imported_file
from web_app.models.bom import AbstractBom


class AbstractBomExporter(ABC):
    """Abstract class for exporting a part list to a various file types."""

    def __init__(self, bom: AbstractBom):
        self.bom: AbstractBom = bom
        self.exported_filename: str = ''

    @abstractmethod
    def _save(self, exported_columns: list, exports_directory: str, filename_without_extension: str):
        """Creates a file with a part list."""
        ...

    def export_part_list(self, exported_columns: list, exports_directory: str, filename: Optional[str] = None) -> None:
        """Exports the part list to a file."""
        exported_filename = 'PrettyBom - Bill of materials'
        if not filename:
            first_imported_file = get_first_imported_file(self.bom)
            if first_imported_file:
                exported_filename = first_imported_file.rsplit('.', 1)[0]
        self._save(exported_columns, exports_directory, exported_filename)


class BomXlsxExporter(AbstractBomExporter):
    """Class for exporting a part list to the xlsx file."""

    def _save(self, exported_columns: list, exports_directory: str, filename_without_extension: str):
        df = pd.DataFrame(map(vars, self.bom.part_list), columns=exported_columns)
        df.columns = df.columns.str.replace('_', ' ').str.capitalize()

        self.exported_filename = f'{filename_without_extension}.xlsx'
        exported_filepath = f'{exports_directory}{self.exported_filename}'
        df.to_excel(exported_filepath, index=False, header=True)
        print(f"Exported {len(df)} parts to file: {self.exported_filename}.")
