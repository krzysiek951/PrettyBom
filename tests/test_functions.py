import pytest

from web_app.functions import (
    normalize_string,
    get_position_delimiter)


class TestGetPositionDelimiter:
    def test_common_csv_delimiters(self):
        """ Test whether the delimiter was found properly. """
        samples = {
            '1,1': ',',
            '1.1': '.',
            '1:1': ':',
            '1-1': '-',
            '1/1': '/',
            '1': None,
            '1.1.1': '.',
        }
        for sample, expected in samples.items():
            result = get_position_delimiter(sample)
            assert result == expected

    def test_bad_data(self):
        """ Test whether the bad data returns exception. """
        broken_data = ['1,1.1', 'lorem ipsum']
        for sample in broken_data:
            with pytest.raises(ValueError):
                get_position_delimiter(sample)


def test_normalize_string():
    """ Test whether the string was normalized properly. """
    samples = {
        'Elesa-ganter': 'Elesa Ganter',
        '   Elesa-ganter   ': 'Elesa Ganter',
        'elesa ganter': 'Elesa Ganter',
        'elesa-ganter': 'Elesa Ganter',
        'elesa - ganter': 'Elesa Ganter',
        'ELESA-GANTER': 'Elesa Ganter',
    }
    for sample, expected in samples.items():
        result = normalize_string(sample)
        assert result == expected
