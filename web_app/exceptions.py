class InvalidPartSetsValue(Exception):
    def __init__(self, sets):
        self.sets = sets
        self.msg = f"'{sets}' is invalid value for 'main assembly sets'. Please enter an integer value."
        super().__init__(self.msg)


class ObjectNotFound(Exception):
    def __init__(self, missing_object, container):
        self.missing_object = missing_object
        self.container = container
        self.msg = f"\n{missing_object}" \
                   f"\nwas not found in:" \
                   f"\n{container}."
        super().__init__(self.msg)


class AttrNotSetException(Exception):
    ...


class QuantityColumnIsNotDigit(Exception):
    def __init__(self, part, qty_column_name):
        self.part = part
        self.qty_column_name = qty_column_name
        self.msg = f'Quantity column "{qty_column_name}" must be with numbers! Check following part:\n {part}'
        super().__init__(self.msg)


class DelimiterNotUnique(Exception):
    def __init__(self, current_set_delimiter, delimiter, part=None):
        self.current_set_delimiter = current_set_delimiter
        self.part = part
        self.delimiter = delimiter
        self.msg = f'Found not unique delimiter: "{delimiter}" while checking the following Part:' \
                   f'\n{part}\n' \
                   f'Current set delimiter: "{current_set_delimiter}"'
        super().__init__(self.msg)
