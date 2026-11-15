
import unittest

from src.fuzzy_system import (
    triangular_membership,
    interval_type2_triangular,
)


class TestFuzzyMembership(unittest.TestCase):

    def test_triangular_center(self):
        result = triangular_membership(
            0.5, 0.0, 0.5, 1.0
        )
        self.assertAlmostEqual(result, 1.0)

    def test_triangular_outside(self):
        result = triangular_membership(
            1.5, 0.0, 0.5, 1.0
        )
        self.assertEqual(result, 0.0)

    def test_interval_type2(self):
        lower, upper = interval_type2_triangular(
            0.3,
            (0.0, 0.5, 1.0),
            (0.2, 0.5, 0.8)
        )

        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)
        self.assertLessEqual(lower, upper)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            triangular_membership(
                0.5, 0.5, 0.5, 1.0
            )


if __name__ == "__main__":
    unittest.main()