"""
Sample tests
"""
from django.test import SimpleTestCase


from app import calc


class CalcTests(SimpleTestCase):
    """Test the calc module"""

    def test_add(self):
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract(self):
        res = calc.subtract(10, 6)

        self.assertEqual(res, 4)

    def test_multiply(self):
        res = calc.multiply(5, 5)

        self.assertEqual(res, 25)

    def test_divide(self):
        res = calc.divide(10, 5)

        self.assertEqual(res, 2)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            calc.divide(10, 0)

    def test_squared(self):
        res = calc.square(5)

        self.assertEqual(res, 25)
