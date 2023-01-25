from functools import wraps


def prepare_and_finish_processing(director_processing_steps):
    """Processing decorator to prepare initial data and update BOM with processed Part list."""

    @wraps(director_processing_steps)
    def wrapper(self, *args, **kwargs):
        self.processor.run_initialization()

        part_list_processing = director_processing_steps(self, *args, **kwargs)

        self.processor.finish_processing()

        return part_list_processing

    return wrapper
