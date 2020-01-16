import unittest
import numpy as np
from ezcoach.range import Range, BoolRange

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
        self.assertEqual(0, range.normalize(1), 'Normalization failed')

    def test_int_range_max_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(1, range.normalize(5), 'Normalization failed')

    def test_int_range_middle_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(.5, range.normalize(3), 'Normalization failed')

    def test_int_range_below_min_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(-0.5, range.normalize(-1), 'Normalization failed')

    def test_int_range_above_max_not_centered(self):
        range = Range(1, 5)
        self.assertEqual(1.5, range.normalize(7), 'Normalization failed')

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
