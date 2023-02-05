from __future__ import annotations

import copy
import os
from abc import ABC, abstractmethod

import pandas as pd

from web_app.models import AbstractBom, AbstractPart
from web_app.typing import ImportedBomSource, HeaderPositions


class AbstractPartListImporter(ABC):
    """Abstract class for importing a part list from various sources."""

    def __init__(self):
        self.imported_part_list: list = self._read_part_list()
        self.imported_bom_columns: list = self._get_part_list_columns()

    @abstractmethod
    def _read_part_list(self) -> list[AbstractPart]:
        """Read a source and return a part list."""
        ...

    @abstractmethod
    def _get_part_list_columns(self) -> list[str]:
        """Get a part list column names from read source."""
        ...

    @abstractmethod
    def _get_imported_bom_source(self) -> ImportedBomSource:
        """Get a source from where imported bom comes from."""
        ...

    def import_to(self, part_list: AbstractBom) -> None:
        """Import read parts to any part list created by BOM Manager."""
        for part in self.imported_part_list:
            part_list.create_part(**part)
        part_list.imported_bom_columns = self.imported_bom_columns
        part_list.imported_bom_sources.append(self._get_imported_bom_source())


class PartListCsvImporter(AbstractPartListImporter):
    """Class for importing a part list from a csv file."""

    def __init__(self, filepath: str, imported_bom_header_position: HeaderPositions):
        self.filepath = filepath
        self.imported_bom_header_position: HeaderPositions = imported_bom_header_position
        self._df = None
        super().__init__()

    def _read_part_list(self) -> list[AbstractPart]:
        df_initial = pd.read_csv(self.filepath, sep=',', on_bad_lines='skip', header=None,
                                 skipinitialspace=True,
                                 encoding='cp1250')

        columns_count = len(df_initial.columns)
        df = pd.read_csv(self.filepath, sep=',', usecols=range(columns_count), header=None,
                         skipinitialspace=True,
                         encoding='cp1250')
        df_diff = pd.concat([df_initial, df]).drop_duplicates(keep=False)
        imported_bom_sliced_rows = []
        if not df_diff.empty:
            for index, row in df_diff.iterrows():
                imported_bom_sliced_rows.append(dict(row))
            sliced_rows_count = len(imported_bom_sliced_rows)
            print(f"Sliced {sliced_rows_count} rows.")

        df = df.fillna('').astype(str)
        df.applymap(lambda x: x.strip().replace('\n', '') if isinstance(x, str) else x)
        print(f"Imported {len(df)} items including header. ")

        self._df = copy.deepcopy(df)
        df.columns = self._get_part_list_columns()
        df = self._remove_part_list_header(df)

        part_list = [row.to_dict() for index, row in df.iterrows()]
        self.imported_part_list = part_list
        return part_list

    def _remove_part_list_header(self, dataframe):
        """Removes a dataframe row with a part list column names."""
        if self.imported_bom_header_position == 'bottom':
            dataframe.drop(index=dataframe.index[-1], axis=0, inplace=True)
        else:
            dataframe.drop(index=dataframe.index[1], axis=0, inplace=True)
        return dataframe

    def _get_part_list_columns(self) -> list:
        if self.imported_bom_header_position == 'bottom':
            last_row = self._df.tail(1).values.flatten().tolist()
            column_list = last_row
        else:
            first_row = self._df.head(1).values.flatten().tolist()
            column_list = first_row
        self.imported_bom_columns = column_list
        return column_list

    def _get_imported_bom_source(self) -> ImportedBomSource:
        """Returns the representation of the imported source."""
        filename = os.path.basename(self.filepath)
        source = {'type': 'file', 'name': filename}
        return source
