import unittest
import numpy as np
from ezcoach.range import Range, BoolRange, UnboundRange

int_ranges = ((0, 1),
              (-1, 0),
              (-1, 1),
              (10, 20),
              (-20, -10),
              (0, 1_000_000),
              (-1_000_000, 0),
              (-1_000_000, 1_000_000),
              )

float_ranges = ((0., 1.),
                (-1., 0.),
                (-1., 1.),
                (10., 20.),
                (-20., -10.),
                (0., 1_000_000.),
                (-1_000_000., 0.),
                (-1_000_000., 1_000_000.),
                (0., .1),
                (-.1, 0.),
                (-.1, .1),
                (.000001, .000005),
                (-.000005, -.000001),
                (-.000001, 1_000_000.),
                )

sizes = (1, 2, 5, 10, 20, 50, 100)

replays = 5


class TestRangeRandom(unittest.TestCase):

    def test_int_range_single_random_range(self):
        self._check_range_single_random_range(int_ranges)

    def test_float_range_single_random_range(self):
        self._check_range_single_random_range(float_ranges)

    def _check_range_single_random_range(self, ranges):
        for min, max in ranges:
            for i in range(replays):
                with self.subTest():
                    r = Range(min, max)
                    self.assertTrue(min <= r.random() <= max, 'Random not in range')

    def test_int_range_random_type(self):
        self._check_range_random_type(int_ranges, int)

    def test_float_range_random_type(self):
        self._check_range_random_type(float_ranges, float)

    def _check_range_random_type(self, ranges, t):
        for min, max in ranges:
            for i in range(replays):
                with self.subTest():
                    r = Range(min, max)
                    self.assertIsInstance(r.random(), t, 'Random wrong type')

    def test_int_range_multiple_random(self):
        self.check_range_multiple_random_range(int_ranges)

    def test_float_range_multiple_random(self):
        self.check_range_multiple_random_range(float_ranges)

    def check_range_multiple_random_range(self, ranges):
        for min, max in ranges:
            for size in sizes:
                for i in range(replays):
                    with self.subTest():
                        r = Range(min, max)
                        rand = r.random(size)
                        self.assertTrue(np.alltrue(min <= rand) and np.alltrue(rand <= max), 'Random not in range')

    def test_bool_range_single_random_shape(self):
        for size in sizes:
            for i in range(replays):
                with self.subTest():
                    r = BoolRange()
                    self.assertEqual(r.random(size).shape, (size, 1), 'Random wrong shape')

    def test_int_range_multiple_random_shape(self):
        self.check_range_multiple_random_shape(int_ranges)

    def test_float_range_multiple_random_shape(self):
        self.check_range_multiple_random_shape(float_ranges)

    def check_range_multiple_random_shape(self, ranges):
        for min, max in ranges:
            for size in sizes:
                for i in range(replays):
                    with self.subTest():
                        r = Range(min, max)
                        rand = r.random(size)
                        self.assertEqual(rand.shape, (size, 1), 'Random wrong shape')


class TestRangeNormalize(unittest.TestCase):

    def test_int_range_min_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(0, range.normalize(1, zero_centered=False), 'Normalization failed')

    def test_int_range_max_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(1, range.normalize(5, zero_centered=False), 'Normalization failed')

    def test_int_range_middle_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(.5, range.normalize(3, zero_centered=False), 'Normalization failed')

    def test_int_range_below_min_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(-0.5, range.normalize(-1, zero_centered=False), 'Normalization failed')

    def test_int_range_above_max_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(1.5, range.normalize(7, zero_centered=False), 'Normalization failed')

    def test_int_range_min_centered(self):
        range = Range(1, 5)
        self.assertEqual(-1, range.normalize(1, zero_centered=True), 'Zero centered normalization failed')

    def test_int_range_max_centered(self):
        range = Range(1, 5)
        self.assertEqual(1, range.normalize(5, zero_centered=True), 'Zero centered normalization failed')

    def test_int_range_middle_centered(self):
        range = Range(1, 5)
        self.assertEqual(0, range.normalize(3, zero_centered=True), 'Zero centered normalization failed')

    def test_int_range_below_min_centered(self):
        range = Range(1, 5)
        self.assertEqual(-2, range.normalize(-1, zero_centered=True), 'Zero centered normalization failed')

    def test_int_range_above_max_centered(self):
        range = Range(1, 5)
        self.assertEqual(2, range.normalize(7, zero_centered=True), 'Zero centered normalization failed')

    def test_float_range_min_not_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(0, range.normalize(.5, zero_centered=False), 'Normalization failed')

    def test_float_range_max_not_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(1, range.normalize(2.5, zero_centered=False), 'Normalization failed')

    def test_float_range_middle_not_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(.5, range.normalize(1.5, zero_centered=False), 'Normalization failed')

    def test_float_range_below_min_not_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(-0.5, range.normalize(-0.5, zero_centered=False), 'Normalization failed')

    def test_float_range_above_max_not_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(1.5, range.normalize(3.5, zero_centered=False), 'Normalization failed')

    def test_float_range_min_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(-1, range.normalize(.5, zero_centered=True), 'Zero centered normalization failed')

    def test_float_range_max_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(1, range.normalize(2.5, zero_centered=True), 'Zero centered normalization failed')

    def test_float_range_middle_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(0, range.normalize(1.5, zero_centered=True), 'Zero centered normalization failed')

    def test_float_range_below_min_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(-2, range.normalize(-0.5, zero_centered=True), 'Zero centered normalization failed')

    def test_float_range_above_max_centered(self):
        range = Range(.5, 2.5)
        self.assertEqual(2, range.normalize(3.5, zero_centered=True), 'Zero centered normalization failed')


class TestRangeContains(unittest.TestCase):

    def test_int_range_contains_min_border(self):
        range = Range(1, 5)
        self.assertTrue(range.contains(1), 'Contains failed')

    def test_int_range_contains_max_border(self):
        range = Range(1, 5)
        self.assertTrue(range.contains(5), 'Contains failed')

    def test_int_range_contains_middle(self):
        range = Range(1, 5)
        self.assertTrue(range.contains(3), 'Contains failed')

    def test_int_range_not_contains_min_border(self):
        range = Range(1, 5)
        self.assertFalse(range.contains(.9999), 'Contains failed')

    def test_int_range_not_contains_max_border(self):
        range = Range(1, 5)
        self.assertFalse(range.contains(5.0001), 'Contains failed')

    def test_int_range_not_contains_min_large(self):
        range = Range(1, 5)
        self.assertFalse(range.contains(-9999999), 'Contains failed')

    def test_int_range_not_contains_max_large(self):
        range = Range(1, 5)
        self.assertFalse(range.contains(9999999), 'Contains failed')

    def test_float_range_contains_min_border(self):
        range = Range(.5, 2.5)
        self.assertTrue(range.contains(.5), 'Contains failed')

    def test_float_range_contains_max_border(self):
        range = Range(.5, 2.5)
        self.assertTrue(range.contains(2.5), 'Contains failed')

    def test_float_range_contains_middle(self):
        range = Range(.5, 2.5)
        self.assertTrue(range.contains(1.5), 'Contains failed')

    def test_float_range_not_contains_min_border(self):
        range = Range(.5, 2.5)
        self.assertFalse(range.contains(.49999), 'Contains failed')

    def test_float_range_not_contains_max_border(self):
        range = Range(.5, 2.5)
        self.assertFalse(range.contains(2.50001), 'Contains failed')

    def test_float_range_not_contains_min_large(self):
        range = Range(.5, 2.5)
        self.assertFalse(range.contains(-9999999), 'Contains failed')

    def test_float_range_not_contains_max_large(self):
        range = Range(.5, 2.5)
        self.assertFalse(range.contains(9999999), 'Contains failed')


class TestBoolRangeContains(unittest.TestCase):

    def test_contains_true(self):
        range = BoolRange()
        self.assertTrue(range.contains(True), 'Contains failed')

    def test_contains_false(self):
        range = BoolRange()
        print('range contains false', range.contains(False))
        self.assertTrue(range.contains(False), 'Contains failed')

    def test_contains_int(self):
        range = BoolRange()
        self.assertFalse(range.contains(5), 'Contains failed')

    def test_contains_float(self):
        range = BoolRange()
        self.assertFalse(range.contains(2.5), 'Contains failed')

    def test_contains_zero(self):
        range = BoolRange()
        self.assertFalse(range.contains(0), 'Contains failed')


class TestUnboundRangeContains(unittest.TestCase):

    def test_contains_true(self):
        range = UnboundRange()
        self.assertTrue(range.contains(True), 'Contains failed')

    def test_contains_false(self):
        range = UnboundRange()
        self.assertTrue(range.contains(False), 'Contains failed')

    def test_contains_int(self):
        range = UnboundRange()
        self.assertTrue(range.contains(5), 'Contains failed')

    def test_contains_float(self):
        range = UnboundRange()
        self.assertTrue(range.contains(2.5), 'Contains failed')

    def test_contains_zero(self):
        range = UnboundRange()
        self.assertTrue(range.contains(0), 'Contains failed')


class TestUnboundRangeNormalize(unittest.TestCase):

    def test_normalize_true(self):
        range = UnboundRange()
        value = True
        self.assertEqual(value, range.normalize(value), 'Normalize failed')

    def test_normalize_false(self):
        range = UnboundRange()
        value = False
        self.assertEqual(value, range.normalize(value), 'Normalize failed')

    def test_normalize_int(self):
        range = UnboundRange()
        value = 5
        self.assertEqual(value, range.normalize(value), 'Normalize failed')

    def test_normalize_float(self):
        range = UnboundRange()
        value = 2.5
        self.assertEqual(value, range.normalize(value), 'Normalize failed')

    def test_normalize_zero(self):
        range = UnboundRange()
        value = 0
        self.assertEqual(value, range.normalize(value), 'Normalize failed')
