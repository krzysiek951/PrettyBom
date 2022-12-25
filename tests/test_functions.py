import unittest

from web_app.functions import normalize_string, get_position_delimiter


class TestFunctions(unittest.TestCase):
    def test_normalize_string(self):
        """
        Test if string was normalized properly.
        """
        samples = ['Elesa-ganter', 'elesa ganter', 'elesa-ganter', 'elesa - ganter', 'ELESA-GANTER']
        expected = 'Elesa Ganter'
        for sample in samples:
            result = normalize_string(sample)
            self.assertEqual(result, expected)

    def test_get_position_delimiter(self):
        """
        Test if delimiter was found properly.
        """
        samples = {
            '1,1': ',',
            '1.1': '.',
            '1:1': ':',
            '1-1': '-',
            '1/1': '/',
            '1': None,
            '1.1.1': '.',
        }
        broken_data = ['1,1.1', 'lorem ipsum']
        for sample, expected in samples.items():
            result = get_position_delimiter(sample)
            self.assertEqual(result, expected)
        for sample in broken_data:
            self.assertRaises(ValueError, get_position_delimiter, sample)


if __name__ == '__main__':
    unittest.main()
