from __future__ import annotations

import copy
import math

from web_app.assets.data.data import *
from web_app.functions import *
from web_app.models.part import DefaultPart, AbstractPart
from web_app.models.processor_validator import BomProcessorValidator


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

    def _set_part_extra_keys(self, part: AbstractPart) -> None:
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

    def _get_parent_assembly(self, part: AbstractPart) -> str:
        parent = self._get_parent(part)
        if parent:
            parent_name = getattr(parent, self.part_number_column)
        else:
            parent_name = self.main_assembly_name
        return parent_name

    def _get_parent_ids(self, part: AbstractPart) -> list:
        position_split = getattr(part, self.part_position_column).split(self.part_position_delimiter)
        parents_count = len(position_split) - 1
        parents_id = [self.part_position_delimiter.join(position_split[:(num + 1)]) for num in range(parents_count)]
        return parents_id

    def _get_parent(self, part: AbstractPart) -> AbstractPart:
        parent = None
        if part.parent:
            parent_id = part.parent[-1]
            parent = self._get_parent_by_id(parent_id)
        return parent

    def _get_parent_by_id(self, part_id: str) -> AbstractPart:
        parent = [part for part in self.initial_part_list if getattr(part, self.part_position_column) == part_id][0]
        return parent

    def _get_child_ids(self, part: AbstractPart) -> list:
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
    def _get_file_type(part: AbstractPart) -> str:
        if len(part.child) > 0 and part.type == 'production':
            file_type = 'assembly'
        else:
            file_type = 'part'
        return file_type

    def _get_sets(self, part: AbstractPart) -> int:
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

    def _get_to_order(self, part: AbstractPart) -> int:
        part_quantity = int(getattr(part, self.part_quantity_column))
        to_order = part_quantity * part.sets
        return to_order

    @staticmethod
    def _get_type(part: AbstractPart) -> str:
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

    def _is_production_part(self, part: AbstractPart) -> bool:
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
    def _is_fastener(part: AbstractPart) -> bool:
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
    def _is_purchased(part: AbstractPart) -> bool:
        """Function that checks if a part is "purchased". It could be only if it's not "production" or "fastener"."""
        is_purchased = True if not part.is_production and not part.is_fastener else False
        return is_purchased

    def _is_junk_by_keywords(self, part: AbstractPart) -> bool:
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

    def _is_junk_by_empty_fields(self, part: AbstractPart) -> bool:
        """Function that sets a part as "junk" if all specified fields are empty."""
        is_junk_by_empty_fields = False
        fields_split = self.junk_part_empty_fields.split(',') if isinstance(self.junk_part_empty_fields,
                                                                            str) else self.junk_part_empty_fields
        filtered_fields = list(filter(None, fields_split))
        fields = [keyword.strip(' ') for keyword in filtered_fields]

        if fields:
            is_junk_by_empty_fields = not any(getattr(part, key) for key in fields)
        return is_junk_by_empty_fields

    def _is_junk_by_purchased_part_nesting(self, part: AbstractPart) -> bool:
        is_junk_by_purchased_part_nesting = False
        if self.set_junk_for_purchased_nests:
            if part.parent:
                parent_id = part.parent[-1]
                parent = self._get_parent_by_id(parent_id)
                is_junk_by_purchased_part_nesting = not self._is_production_part(parent)
        return is_junk_by_purchased_part_nesting

    @staticmethod
    def _is_junk(part: AbstractPart) -> bool:
        is_junk = True if part.is_junk_by_keywords or part.is_junk_by_empty_fields or \
                          part.is_junk_by_purchased_part_nesting else False
        return is_junk

    def _normalize_name(self, part: AbstractPart) -> AbstractPart:
        for key in self.normalized_columns:
            if hasattr(part, key):
                normalized_name = normalize_string(getattr(part, key))
                setattr(part, key, normalized_name)
        return part

    def _get_sub_bom(self, part: AbstractPart, part_list: list) -> list:
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
