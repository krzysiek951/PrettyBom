import unittest

from web_app.functions import normalize_string


class TestNormalizeString(unittest.TestCase):
    def test_normalize_string(self):
        """
        Test
        """
        data = ['Elesa-ganter', 'elesa ganter', 'elesa-ganter', 'elesa - ganter', 'ELESA-GANTER']
        expected = ['Elesa Ganter', 'Elesa Ganter', 'Elesa Ganter', 'Elesa Ganter', 'Elesa Ganter']
        result = [normalize_string(x.title()) for x in data]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()

    # .assertEqual(a, b) -- a == b
    # .assertTrue(x) -- bool(x) is True
    # .assertFalse(x)
    # bool(x) is False
    # .assertIs(a, b)
    # a is b
    # .assertIsNone(x)
    # x is None
    # .assertIn(a, b)
    # a in b
    # .assertIsInstance(a, b)
    # isinstance(a, b)
