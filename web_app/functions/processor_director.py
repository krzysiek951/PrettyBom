from functools import wraps


def prepare_and_finish_processing(f):
    """Processing decorator to prepare initial data and update BOM with processed Part list."""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.processor.run_initialization()
        f(self, *args, **kwargs)
        self.processor.finish_processing()

    return wrapper
