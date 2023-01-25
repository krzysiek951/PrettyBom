from abc import abstractmethod

from .bom_processor import AbstractBomProcessor
from ..functions import (get_parent_ids, get_child_ids, get_sets, get_to_order, get_type, is_production, is_fastener,
                         is_purchased, is_junk_by_keywords, is_junk_by_empty_fields, is_junk_by_purchased_part_nesting,
                         is_junk, get_parent_assembly, get_file_type, normalize_name, prepare_and_finish_processing)


class AbstractProcessorDirector:
    """Abstract class for managing processor steps."""

    def __init__(self, processor: AbstractBomProcessor):
        self.processor = processor

    @abstractmethod
    @prepare_and_finish_processing
    def run(self) -> None:
        """Runs Process Director processing steps."""
        ...


class FullFeatureProcessorDirector(AbstractProcessorDirector):
    """Class for Process Director to process the Part list with all available features."""

    def __init__(self, processor: AbstractBomProcessor):
        super().__init__(processor)

    @prepare_and_finish_processing
    def run(self) -> None:
        """Runs Processor with all available functionalities"""
        self.processor.update_parts_with(get_parent_ids)
        self.processor.update_parts_with(get_child_ids)
        self.processor.update_parts_with(get_sets)
        self.processor.update_parts_with(get_to_order)
        self.processor.update_parts_with(is_production)
        self.processor.update_parts_with(is_fastener)
        self.processor.update_parts_with(is_purchased)
        self.processor.update_parts_with(is_junk_by_keywords)
        self.processor.update_parts_with(is_junk_by_empty_fields)
        self.processor.update_parts_with(is_junk_by_purchased_part_nesting)
        self.processor.update_parts_with(is_junk)
        self.processor.update_parts_with(get_type)
        self.processor.update_parts_with(get_parent_assembly)
        self.processor.update_parts_with(get_file_type)
        self.processor.update_parts_with(normalize_name)
