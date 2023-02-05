from abc import abstractmethod

from .bom_processor import BomProcessor
from ..functions import (prepare_and_finish_processing)


class AbstractProcessorDirector:
    """Abstract class for managing processor steps."""

    def __init__(self, processor: BomProcessor):
        self.processor = processor

    @abstractmethod
    @prepare_and_finish_processing
    def run_processing(self) -> None:
        """Runs Process Director processing steps."""
        ...


class FullFeatureProcessorDirector(AbstractProcessorDirector):
    """Class for Process Director to process the Part list with all available features."""

    def __init__(self, processor: BomProcessor):
        super().__init__(processor)

    @prepare_and_finish_processing
    def run_processing(self) -> None:
        """Runs Processor with all available functionalities"""

        self.processor.bom_modifiers.set_parent()
        self.processor.bom_modifiers.set_child()
        self.processor.bom_modifiers.set_sets()
        self.processor.bom_modifiers.set_to_order()
        self.processor.bom_modifiers.set_is_production()
        self.processor.bom_modifiers.set_is_fastener()
        self.processor.bom_modifiers.set_is_purchased()
        self.processor.bom_modifiers.set_is_junk_by_keywords()
        self.processor.bom_modifiers.set_is_junk_by_empty_fields()
        self.processor.bom_modifiers.set_is_junk_by_purchased_part_nesting()
        self.processor.bom_modifiers.set_is_junk()
        self.processor.bom_modifiers.set_type()
        self.processor.bom_modifiers.set_parent_assembly()
        self.processor.bom_modifiers.set_file_type()
        self.processor.bom_modifiers.set_normalized_names()
        self.processor.bom_modifiers.set_tree_sorting()
