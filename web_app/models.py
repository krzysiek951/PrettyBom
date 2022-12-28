from __future__ import annotations

import copy
import math
import os
from abc import ABC, abstractmethod

import pandas as pd

from web_app.assets.data.data import *
from web_app.functions import *
from .typing import *


class BaseBomManager(ABC):
    def __init__(self):
        self._bom_list: list = []

    @property
    def bom_list(self) -> list[BaseBom]:
        return self._bom_list

    @bom_list.setter
    def bom_list(self, bom_list: list[BaseBom]) -> None:
        self._bom_list = bom_list

    @abstractmethod
    def create_bom(self, **kwargs) -> BaseBom:
        pass

    @abstractmethod
    def reset_bom(self, bom: BaseBom) -> BaseBom:
        pass

    def get_bom_count(self) -> int:
        bom_count = len(self.bom_list)
        return bom_count

    def delete_bom(self, bom: BaseBom) -> None:
        if bom not in self.bom_list:
            raise ValueError(f'{bom} does not exist in a BOM list.')
        else:
            self.bom_list = [item for item in self.bom_list if item is not bom]

    def print_bom_list(self) -> None:
        print("==== BOM LIST ====")
        for index, bom in enumerate(self.bom_list):
            print(index, bom.__dict__)


class DefaultBomManager(BaseBomManager):
    def __init__(self):
        super().__init__()
        self.bom_manager_type = 'default'

    def create_bom(self, **kwargs) -> DefaultBom:
        bom = DefaultBom(**kwargs)
        self.bom_list.append(bom)
        return bom

    def reset_bom(self, bom: DefaultBom) -> DefaultBom:
        if bom not in self.bom_list:
            raise ValueError(f"{bom} does not exist in a BOM list.")
        else:
            clean_bom = DefaultBom()
            self.bom_list = [item if item is not bom else clean_bom for item in self.bom_list]
            return clean_bom


class BaseBom(ABC):
    def __init__(self, **kwargs):
        self.part_list: list[BasePart] = []
        self.imported_bom_filepath: str = ''
        self.imported_bom_columns: list[str] = []
        self.exported_columns: list[str] = []
        self.part_position_column: str = kwargs.get('part_position_column', '')
        self.part_quantity_column: str = kwargs.get('part_quantity_column', '')
        self.part_number_column: str = kwargs.get('part_number_column', '')
        self.part_name_column: str = kwargs.get('part_name_column', '')
        self._main_assembly_sets: int = kwargs.get('main_assembly_sets', 0)
        self.main_assembly_name: str = kwargs.get('main_assembly_name', '')

    @abstractmethod
    def create_part(self, **kwargs) -> BasePart:
        pass

    @abstractmethod
    def process_part_list(self) -> None:
        pass

    def delete_part(self, part: BasePart) -> None:
        if part not in self.part_list:
            raise ValueError(f'{part} does not exist in a Bill of Materials.')
        else:
            self.part_list = [item for item in self.part_list if item is not part]

    def delete_all_parts(self) -> None:
        self.part_list.clear()

    def get_part_count(self) -> int:
        part_count = len(self.part_list)
        return part_count

    def print_part_list(self) -> None:
        print("==== PART LIST ====")
        for index, part in enumerate(self.part_list):
            print(index, part.__dict__)

    def import_csv(self, filepath: str, bom_header_position: HeaderPositions) -> None:
        importer = CsvBomImporter(filepath, bom_header_position)
        self.imported_bom_columns = importer.imported_bom_columns
        self.imported_bom_filepath = filepath
        for part in importer.imported_bom_list:
            self.create_part(**part)

    def export_to_xlsx(self, export_folder_pathname: str, filename: str = '') -> str:
        default_file_name = 'PrettyBom - Bill of materials'
        if not filename:
            if self.imported_bom_filepath:
                filename = os.path.basename(self.imported_bom_filepath).split('.')[0]
            else:
                filename = default_file_name
        exporter = XlsxBomExporter()
        exporter.save_to_xls(self.part_list, self.exported_columns, filename,
                             export_folder_pathname=export_folder_pathname)
        return filename


class DefaultBom(BaseBom):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bom_type = 'default'
        self.production_part_keywords: list = kwargs.get('production_part_keywords', [])
        self.junk_part_keywords: list = kwargs.get('junk_part_keywords', [])
        self.junk_part_empty_fields: list = kwargs.get('junk_part_empty_fields', [])
        self.normalized_columns: list = kwargs.get('normalized_columns', [])
        self.parts_sorting: bool = kwargs.get('parts_sorting', True)
        self.bom_processor: DefaultBomProcessor | None = None

    def create_part(self, **kwargs) -> DefaultPart:
        part = DefaultPart(**kwargs)
        self.part_list.append(part)
        return part

    def process_part_list(self):
        self.bom_processor = DefaultBomProcessor(
            production_part_keywords=self.production_part_keywords,
            junk_part_keywords=self.junk_part_keywords,
            junk_part_empty_fields=self.junk_part_empty_fields,
            part_position_column=self.part_position_column,
            part_quantity_column=self.part_quantity_column,
            part_number_column=self.part_number_column,
            part_name_column=self.part_name_column,
            main_assembly_name=self.main_assembly_name,
            main_assembly_sets=self.main_assembly_sets,
            normalized_columns=self.normalized_columns,
            parts_sorting=self.parts_sorting,
        )
        try:
            self.bom_processor.run_processing(self.part_list)
            self.part_list = self.bom_processor.processed_part_list
        except ValueError as error:
            return error

    def undo_processing(self) -> None:
        self.part_list = self.bom_processor.initial_part_list

    @property
    def main_assembly_sets(self) -> int:
        return self._main_assembly_sets

    @main_assembly_sets.setter
    def main_assembly_sets(self, main_assembly_sets: int) -> None:
        try:
            main_assembly_sets = int(main_assembly_sets)
            self._main_assembly_sets = main_assembly_sets
        except ValueError as e:
            raise ValueError('Main assembly sets must be of integer type.') from e


class BasePart(ABC):
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


class DefaultPart(BasePart):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseBomFileImporter(ABC):
    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self.imported_bom_list: list = []
        self.imported_bom_columns: list = []

    @abstractmethod
    def import_file(self) -> None:
        pass

    @abstractmethod
    def get_imported_bom_columns(self, df) -> list:
        pass


class CsvBomImporter(BaseBomFileImporter):

    def __init__(self, filepath: str, imported_bom_header_position: HeaderPositions):
        super().__init__(filepath)
        self.imported_bom_header_position: HeaderPositions = imported_bom_header_position  # TODO: ADD LITERAL
        self.import_file()

    def import_file(self) -> None:
        df_initial = pd.read_csv(self.filepath, sep=',', on_bad_lines='skip', header=None, skipinitialspace=True,
                                 encoding='cp1250')
        columns_count = len(df_initial.columns)
        df = pd.read_csv(self.filepath, sep=',', usecols=range(columns_count), header=None, skipinitialspace=True,
                         encoding='cp1250')
        df_diff = pd.concat([df_initial, df]).drop_duplicates(keep=False)
        imported_bom_sliced_rows = []
        if not df_diff.empty:
            for index, row in df_diff.iterrows():
                imported_bom_sliced_rows.append(dict(row))
            sliced_rows_count = len(imported_bom_sliced_rows)
            print(f"Sliced {sliced_rows_count} rows.")
        df = df.fillna('')
        df = df.astype(str)
        df.applymap(lambda x: x.strip().replace('\n', '') if isinstance(x, str) else x)
        print(f"Imported {len(df)} items including header. ")
        df.columns = self.get_imported_bom_columns(df)
        self.imported_bom_list = [row.to_dict() for index, row in df.iterrows()]

    def get_imported_bom_columns(self, df) -> list:
        column_list = df.head(1).values.flatten().tolist()
        if self.imported_bom_header_position == 'bottom':
            column_list = df.tail(1).values.flatten().tolist()
            df.drop(index=df.index[-1], axis=0, inplace=True)
        else:
            df.drop(index=df.index[1], axis=0, inplace=True)
        self.imported_bom_columns = column_list
        return column_list


class BaseBomProcessor:
    def __init__(self):
        self.initial_part_list: list = []
        self.processed_part_list: list = []

    def print_initial_part_list(self) -> None:
        print("====== INITIAL PART LIST ======")
        for index, part in enumerate(self.initial_part_list):
            print(index, part.__dict__)

    def print_processed_part_list(self) -> None:
        print("====== PROCESSED PART LIST ======")
        for index, part in enumerate(self.processed_part_list):
            print(index, part.__dict__)


class DefaultBomProcessor(BaseBomProcessor):
    def __init__(self, **kwargs):
        super().__init__()
        self.processing_succeeded = False
        self.production_part_keywords = kwargs.get('production_part_keywords', '')
        self.junk_part_keywords = kwargs.get('junk_part_keywords', '')
        self.junk_part_empty_fields = kwargs.get('junk_part_empty_fields', '')
        self.set_junk_for_purchased_nests = True
        self.reverse_bom_sorting = False
        self.part_position_column = kwargs.get('part_position_column', '')
        self.part_quantity_column = kwargs.get('part_quantity_column', '')
        self.part_number_column = kwargs.get('part_number_column', '')
        self.part_name_column = kwargs.get('part_name_column', '')
        self.main_assembly_name = kwargs.get('main_assembly_name', '')
        self.main_assembly_sets = kwargs.get('main_assembly_sets', 0)
        self.normalized_columns = kwargs.get('normalized_columns', '')
        self.parts_sorting = kwargs.get('parts_sorting', '')
        self.processor_validator: BomProcessorValidator | None = None
        self.part_position_delimiter: str | None = None

    def run_processing(self, part_list: list[DefaultPart]) -> None:
        print('Part list processing started...')

        self.initial_part_list = copy.deepcopy(part_list)

        self.run_validation()
        if not self.processor_validator.validation_succeded:
            raise ValueError('\n'.join(self.processor_validator.error_messages) + '\nProcessing cancelled.')

        self.part_position_delimiter = self.processor_validator.part_position_delimiter

        new_part_list = []
        for part in part_list:
            self._set_part_extra_keys(part)
            self._normalize_name(part) if self.normalized_columns else None
            new_part_list.append(part)
        processed_part_list = self._create_bom_tree_list(new_part_list)
        self.processed_part_list = processed_part_list
        self.processing_succeeded = True
        print('Success! Part list processing finished.\n')

    def run_validation(self) -> None:
        validator = self.processor_validator = BomProcessorValidator()
        validator.run(
            self.initial_part_list,
            self.part_position_column,
            self.part_quantity_column,
        )

    def _set_part_extra_keys(self, part: BasePart) -> None:
        """A function that fills up the part attributes."""
        part.parent = self._get_parent_ids(part)
        part.child = self._get_child_ids(part)
        part.sets = self._get_sets(part)
        part.to_order = self._get_to_order(part)
        part.is_production = self._is_production_part(part)
        part.is_fastener = self._is_fastener(part)
        part.is_purchased = self._is_purchased(part)
        part.is_junk_by_keywords = self._is_junk_by_keywords(part)
        part.is_junk_by_empty_fields = self._is_junk_by_empty_fields(part)
        part.is_junk_by_purchased_part_nesting = self._is_junk_by_purchased_part_nesting(part)
        part.is_junk = self._is_junk(part)
        part.type = self._get_type(part)
        part.file_type = self._get_file_type(part)
        part.parent_assembly = self._get_parent_assembly(part)

    def _get_parent_assembly(self, part: BasePart) -> str:
        parent = self._get_parent(part)
        if parent:
            parent_name = getattr(parent, self.part_number_column)
        else:
            parent_name = self.main_assembly_name
        return parent_name

    def _get_parent_ids(self, part: BasePart) -> list:
        position_split = getattr(part, self.part_position_column).split(self.part_position_delimiter)
        parents_count = len(position_split) - 1
        parents_id = [self.part_position_delimiter.join(position_split[:(num + 1)]) for num in range(parents_count)]
        return parents_id

    def _get_parent(self, part: BasePart) -> BasePart:
        parent = None
        if part.parent:
            parent_id = part.parent[-1]
            parent = self._get_parent_by_id(parent_id)
        return parent

    def _get_parent_by_id(self, part_id: str) -> BasePart:
        parent = [part for part in self.initial_part_list if getattr(part, self.part_position_column) == part_id][0]
        return parent

    def _get_child_ids(self, part: BasePart) -> list:
        position_split = getattr(part, self.part_position_column).split(self.part_position_delimiter)
        part_len = len(position_split)
        child_len = part_len + 2
        child_id = [getattr(item, self.part_position_column) for item in self.initial_part_list if
                    len(getattr(item, self.part_position_column).split(
                        self.part_position_delimiter)) + 1 == child_len and
                    getattr(item, self.part_position_column).split(self.part_position_delimiter)[
                    :part_len] == position_split]
        return child_id

    @staticmethod
    def _get_file_type(part: BasePart) -> str:
        if len(part.child) > 0 and part.type == 'production':
            file_type = 'assembly'
        else:
            file_type = 'part'
        return file_type

    def _get_sets(self, part: BasePart) -> int:
        # parent_sets = [int(getattr(instance, self.part_quantity_column)) for instance in self.initial_part_list for
        #                parent in part.parent if getattr(instance, self.part_position_column) == parent]
        parent_sets = []
        for instance in self.initial_part_list:
            for parent in part.parent:
                if getattr(instance, self.part_position_column) == parent:
                    parent_sets.append(int(getattr(instance, self.part_quantity_column)))
        sub_sets = math.prod(parent_sets)
        sets = sub_sets * self.main_assembly_sets
        return sets

    def _get_to_order(self, part: BasePart) -> int:
        part_quantity = int(getattr(part, self.part_quantity_column))
        to_order = part_quantity * part.sets
        return to_order

    @staticmethod
    def _get_type(part: BasePart) -> str:
        if part.is_junk:
            part_type = 'junk'
        elif part.is_production:
            part_type = 'production'
        elif part.is_fastener:
            part_type = 'fastener'
        elif part.is_purchased:
            part_type = 'purchased'
        else:
            part_type = None
        return part_type

    def _is_production_part(self, part: BasePart) -> bool:
        """Function that checks if a part is "production" based by provided keywords."""
        is_production_part = False
        keywords_split = self.production_part_keywords.split(',') if isinstance(self.production_part_keywords,
                                                                                str) else self.production_part_keywords
        filtered_keywords = list(filter(None, keywords_split))
        keywords = [keyword.strip(' ') for keyword in filtered_keywords]
        if keywords:
            is_production_part = any(
                keyword in getattr(part, self.part_number_column) for keyword in keywords)
        return is_production_part

    @staticmethod
    def _is_fastener(part: BasePart) -> bool:
        """Function that checks if a part is "fastener" based on library of keywords."""
        name_split = [str(value).upper() for key, value in vars(part).items()]
        norm_in_name = {norm: name for norm, value in standard_fasteners.items() for name in name_split if norm in name}
        is_part_fastener = False
        if norm_in_name:
            part_norm = next(iter(norm_in_name))
            part_name = norm_in_name[part_norm]
            part_numbers = [int(num) for num in re.findall(r'\d+', part_name)]
            is_part_fastener = any(x in part_numbers for x in standard_fasteners[part_norm])
        return is_part_fastener

    @staticmethod
    def _is_purchased(part: BasePart) -> bool:
        """Function that checks if a part is "purchased". It could be only if it's not "production" or "fastener"."""
        is_purchased = True if not part.is_production and not part.is_fastener else False
        return is_purchased

    def _is_junk_by_keywords(self, part: BasePart) -> bool:
        """Function that checks if a part is "junk" based by provided keywords."""
        is_junk_by_keywords = False
        keywords_split = self.junk_part_keywords.split(',') if isinstance(self.junk_part_keywords, str) \
            else self.junk_part_keywords
        filtered_keywords = list(filter(None, keywords_split))
        keywords = [keyword.strip(' ') for keyword in filtered_keywords]

        if keywords:
            is_junk_by_keywords = any(
                f in (getattr(part, self.part_number_column) or getattr(part, self.part_name_column)) for f in keywords)
        return is_junk_by_keywords

    def _is_junk_by_empty_fields(self, part: BasePart) -> bool:
        """Function that sets a part as "junk" if all specified fields are empty."""
        is_junk_by_empty_fields = False
        fields_split = self.junk_part_empty_fields.split(',') if isinstance(self.junk_part_empty_fields,
                                                                            str) else self.junk_part_empty_fields
        filtered_fields = list(filter(None, fields_split))
        fields = [keyword.strip(' ') for keyword in filtered_fields]

        if fields:
            is_junk_by_empty_fields = not any(getattr(part, key) for key in fields)
        return is_junk_by_empty_fields

    def _is_junk_by_purchased_part_nesting(self, part: BasePart) -> bool:
        is_junk_by_purchased_part_nesting = False
        if self.set_junk_for_purchased_nests:
            if part.parent:
                parent_id = part.parent[-1]
                parent = self._get_parent_by_id(parent_id)
                is_junk_by_purchased_part_nesting = not self._is_production_part(parent)
        return is_junk_by_purchased_part_nesting

    @staticmethod
    def _is_junk(part: BasePart) -> bool:
        is_junk = True if part.is_junk_by_keywords or part.is_junk_by_empty_fields or \
                          part.is_junk_by_purchased_part_nesting else False
        return is_junk

    def _normalize_name(self, part: BasePart) -> BasePart:
        for key in self.normalized_columns:
            if hasattr(part, key):
                normalized_name = normalize_string(getattr(part, key))
                setattr(part, key, normalized_name)
        return part

    def _get_sub_bom(self, part: BasePart, part_list: list) -> list:
        name_split = getattr(part, self.part_position_column).split(self.part_position_delimiter)
        part_len = len(getattr(part, "parent")) + 1
        child_len = len(getattr(part, "parent")) + 2
        parts_order = "pfjabcdeghiklmnoqrstuvwxyz"
        # implemented for ordering parts as: "production, purchased, fastener, junk
        sub_bom = [item for item in part_list if len(getattr(item, "parent")) + 1 == child_len and
                   getattr(item, self.part_position_column).split(self.part_position_delimiter)[
                   :part_len] == name_split]
        sub_bom = sorted(sub_bom,
                         key=lambda word: ([parts_order.index(c) for c in word.type],
                                           getattr(word, self.part_number_column)), reverse=True)
        return sub_bom

    def _create_bom_tree_list(self, part_list: list) -> list:
        bom_tree_list = [part for part in part_list if
                         len(getattr(part, self.part_position_column).split(self.part_position_delimiter)) == 1]
        bom_tree_list = sorted(bom_tree_list, key=lambda d: getattr(d, self.part_number_column), reverse=False)
        last_generation = 20
        for generation in range(1, last_generation):
            for part in bom_tree_list:
                child_generation = len(getattr(part, self.part_position_column).split(self.part_position_delimiter))
                if child_generation == generation:
                    child_bom = sorted(self._get_sub_bom(part, part_list), key=lambda d: self.part_number_column,
                                       reverse=False)
                    for item in child_bom:
                        bom_tree_list.insert(bom_tree_list.index(part) + 1, item)
        return bom_tree_list


class BomProcessorValidator:
    def __init__(self):
        self.validation_succeded: bool = False
        self.error_messages: list[str] = []
        self.invalid_position_value_parts: list = []
        self.invalid_quantity_value_parts: list = []
        self.part_position_delimiter: str | None = None

    def run(
            self,
            part_list: list[BasePart],
            part_position_column: str,
            part_quantity_column: str,
    ) -> None:
        """  """
        print('Part list validation started...')
        validated_parts = []

        for part in part_list:
            part_validators = [
                self.is_position_delimiter_unique(part, part_position_column),
                self.is_quantity_a_number(part, part_quantity_column),
            ]
            is_part_valid = all(part_validators)
            validated_parts.append(is_part_valid)

            self.validation_succeded = all(validated_parts)

            if self.invalid_position_value_parts:
                self.error_messages.append(
                    f'Part position must be of integer type and use unique delimiter. Found '
                    f'{len(self.invalid_position_value_parts)} invalid parts.')
            if self.invalid_quantity_value_parts:
                self.error_messages.append(
                    f'Part quantity must be of integer type. Found '
                    f'{len(self.invalid_quantity_value_parts)} invalid parts.')
        print('Part list validation finished.')

    def is_position_delimiter_unique(self, part: BasePart, part_position_column: str) -> bool:
        """ Returns true if position column has at least one non-digit unique delimiter for all parts. """
        try:
            position_delimiter = get_position_delimiter(getattr(part, part_position_column))
            if not position_delimiter or position_delimiter is self.part_position_delimiter:
                return True
            elif position_delimiter and not self.part_position_delimiter:
                self.part_position_delimiter = position_delimiter
                return True
            else:
                self.invalid_position_value_parts.append(part)
                return False
        except ValueError:
            self.invalid_position_value_parts.append(part)
            return False

    def is_quantity_a_number(self, part: BasePart, column_name: str) -> bool:
        part_quantity = str(getattr(part, column_name))
        is_quantity_a_number = part_quantity.isdigit()
        if not is_quantity_a_number:
            self.invalid_quantity_value_parts.append(part)
            return is_quantity_a_number
        return is_quantity_a_number


class BaseBomExporter(ABC):
    def __init__(self):
        pass


class XlsxBomExporter(BaseBomExporter):
    def __init__(self):
        super().__init__()

    @staticmethod
    def save_to_xls(part_list: list, exported_columns: list, filename: str, export_folder_pathname: str):
        df = pd.DataFrame(map(vars, part_list), columns=exported_columns)
        df.columns = df.columns.str.replace('_', ' ').str.capitalize()
        exported_file_path = f'{export_folder_pathname}{filename}.xlsx'
        df.to_excel(exported_file_path, index=False, header=True)
        print(f"Exported {len(df)} parts to file: {filename}.")
        return exported_file_path, filename
