import unittest
import numpy as np
from ezcoach.value import BoolValue, IntValue, FloatValue, BoolList, IntList, FloatList
from ezcoach.range import Range, UnboundRange


class TestBoolValueContains(unittest.TestCase):

    def test_contains_true(self):
        value = BoolValue()
        self.assertTrue(value.contains(True), 'Contains failed')

    def test_contains_false(self):
        value = BoolValue()
        self.assertTrue(value.contains(False), 'Contains failed')

    def test_contains_int(self):
        value = BoolValue()
        self.assertFalse(value.contains(5), 'Contains failed')

    def test_contains_float(self):
        value = BoolValue()
        self.assertFalse(value.contains(2.5), 'Contains failed')

    def test_contains_zero(self):
        value = BoolValue()
        self.assertFalse(value.contains(0), 'Contains failed')


class TestIntValueContains(unittest.TestCase):

    def test_int_range_contains_min_border(self):
        value = IntValue(Range(1, 5))
        self.assertTrue(value.contains(1), 'Contains failed')

    def test_int_range_contains_max_border(self):
        value = IntValue(Range(1, 5))
        self.assertTrue(value.contains(5), 'Contains failed')

    def test_int_range_contains_middle(self):
        value = IntValue(Range(1, 5))
        self.assertTrue(value.contains(3), 'Contains failed')

    def test_int_range_not_contains_min_border(self):
        value = IntValue(Range(1, 5))
        self.assertFalse(value.contains(.9999), 'Contains failed')

    def test_int_range_not_contains_max_border(self):
        value = IntValue(Range(1, 5))
        self.assertFalse(value.contains(5.0001), 'Contains failed')

    def test_int_range_not_contains_min_large(self):
        value = IntValue(Range(1, 5))
        self.assertFalse(value.contains(-9999999), 'Contains failed')

    def test_int_range_not_contains_max_large(self):
        value = IntValue(Range(1, 5))
        self.assertFalse(value.contains(9999999), 'Contains failed')

    def test_unbound_range_contains_int(self):
        value = IntValue(UnboundRange())
        self.assertTrue(value.contains(5), 'Contains failed')

    def test_unbound_range_contains_float(self):
        value = IntValue(UnboundRange())
        self.assertFalse(value.contains(2.5), 'Contains failed')

    def test_unbound_range_contains_zero(self):
        value = IntValue(UnboundRange())
        self.assertTrue(value.contains(0), 'Contains failed')


class TestFloatValueContains(unittest.TestCase):

    def test_int_range_contains_min_border(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertTrue(value.contains(.5), 'Contains failed')

    def test_int_range_contains_max_border(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertTrue(value.contains(2.5), 'Contains failed')

    def test_int_range_contains_middle(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertTrue(value.contains(1.5), 'Contains failed')

    def test_int_range_not_contains_min_border(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertFalse(value.contains(.49999), 'Contains failed')

    def test_int_range_not_contains_max_border(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertFalse(value.contains(2.50001), 'Contains failed')

    def test_int_range_not_contains_min_large(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertFalse(value.contains(-9999999.), 'Contains failed')

    def test_int_range_not_contains_max_large(self):
        value = FloatValue(Range(.5, 2.5))
        self.assertFalse(value.contains(9999999.), 'Contains failed')

    def test_unbound_range_contains_int(self):
        value = FloatValue(UnboundRange())
        self.assertFalse(value.contains(5), 'Contains failed')

    def test_unbound_range_contains_float(self):
        value = FloatValue(UnboundRange())
        self.assertTrue(value.contains(2.5), 'Contains failed')

    def test_unbound_range_contains_zero(self):
        value = FloatValue(UnboundRange())
        self.assertTrue(value.contains(0.), 'Contains failed')

    def test_unbound_range_contains_zero_int(self):
        value = FloatValue(UnboundRange())
        self.assertFalse(value.contains(0), 'Contains failed')


class TestBoolListValueContains(unittest.TestCase):

    def test_size_1_contains_true(self):
        value = BoolList(1)
        self.assertFalse(value.contains(True), 'Contains failed')

    def test_size_1_contains_false(self):
        value = BoolList(1)
        self.assertFalse(value.contains(False), 'Contains failed')

    def test_size_1_contains_true_list(self):
        value = BoolList(1)
        self.assertTrue(value.contains([True]), 'Contains failed')

    def test_size_1_contains_false_list(self):
        value = BoolList(1)
        self.assertTrue(value.contains([False]), 'Contains failed')

    def test_size_2_contains_true_list(self):
        value = BoolList(2)
        self.assertTrue(value.contains([True, True]), 'Contains failed')

    def test_size_2_contains_false_list(self):
        value = BoolList(2)
        self.assertTrue(value.contains([False, False]), 'Contains failed')

    def test_size_2_contains_true_false_list(self):
        value = BoolList(2)
        self.assertTrue(value.contains([True, False]), 'Contains failed')

    def test_size_10_contains_true_list(self):
        value = BoolList(10)
        self.assertTrue(value.contains([True for __ in range(10)]), 'Contains failed')

    def test_size_10_contains_false_list(self):
        value = BoolList(10)
        self.assertTrue(value.contains([False for __ in range(10)]), 'Contains failed')

    def test_size_10_contains_true_false_list(self):
        value = BoolList(10)
        bool_list = [True, False, True, False, True, False, True, False, True, False]
        self.assertTrue(value.contains(bool_list), 'Contains failed')


class TestIntListValueContains(unittest.TestCase):

    def test_size_1_contains_in(self):
        value = IntList([Range(1, 5)])
        self.assertFalse(value.contains(2), 'Contains failed')

    def test_size_1_contains_out(self):
        value = IntList([Range(1, 5)])
        self.assertFalse(value.contains(6), 'Contains failed')

    def test_size_1_contains_in_list(self):
        value = IntList([Range(1, 5)])
        self.assertTrue(value.contains([2]), 'Contains failed')

    def test_size_1_contains_out_list(self):
        value = IntList([Range(1, 5)])
        self.assertFalse(value.contains([6]), 'Contains failed')

    def test_size_2_contains_in_list(self):
        value = IntList([Range(1, 5), Range(1, 5)])
        self.assertTrue(value.contains([2, 3]), 'Contains failed')

    def test_size_2_contains_out_list(self):
        value = IntList([Range(1, 5), Range(1, 5)])
        self.assertFalse(value.contains([6, 7]), 'Contains failed')

    def test_size_2_contains_in_out_list(self):
        value = IntList([Range(1, 5), Range(1, 5)])
        self.assertFalse(value.contains([2, 7]), 'Contains failed')

    def test_size_10_contains_in_list(self):
        value = IntList([Range(1, 5) for __ in range(10)])
        v = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        self.assertTrue(value.contains(v), 'Contains failed')

    def test_size_10_contains_out_list(self):
        value = IntList([Range(1, 5) for __ in range(10)])
        v = [-5, -4, -3, -2, -1, 6, 7, 8, 9, 10]
        self.assertFalse(value.contains(v), 'Contains failed')

    def test_size_10_contains_in_out_list(self):
        value = IntList([Range(1, 5) for __ in range(10)])
        v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertFalse(value.contains(v), 'Contains failed')

    def test_size_10_contains_wrong_len_list(self):
        value = IntList([Range(1, 5) for __ in range(10)])
        self.assertFalse(value.contains([2, 3]), 'Contains failed')


class TestFloatListValueContains(unittest.TestCase):

    def test_size_1_contains_in(self):
        value = FloatList([Range(.5, 2.5)])
        self.assertFalse(value.contains(1.), 'Contains failed')

    def test_size_1_contains_out(self):
        value = FloatList([Range(.5, 2.5)])
        self.assertFalse(value.contains(3.), 'Contains failed')

    def test_size_1_contains_in_list(self):
        value = FloatList([Range(.5, 2.5)])
        self.assertTrue(value.contains([1.]), 'Contains failed')

    def test_size_1_contains_out_list(self):
        value = FloatList([Range(.5, 2.5)])
        self.assertFalse(value.contains([3.]), 'Contains failed')

    def test_size_2_contains_in_list(self):
        value = FloatList([Range(.5, 2.5), Range(.5, 2.5)])
        self.assertTrue(value.contains([1., 1.5]), 'Contains failed')

    def test_size_2_contains_out_list(self):
        value = FloatList([Range(.5, 2.5), Range(.5, 2.5)])
        self.assertFalse(value.contains([3., 3.5]), 'Contains failed')

    def test_size_2_contains_in_out_list(self):
        value = FloatList([Range(.5, 2.5), Range(.5, 2.5)])
        self.assertFalse(value.contains([2, 7]), 'Contains failed')

    def test_size_10_contains_in_list(self):
        value = FloatList([Range(.5, 2.5) for __ in range(10)])
        v = [.5, 1., 1.5, 2., 2.5, .5, 1., 1.5, 2., 2.5]
        self.assertTrue(value.contains(v), 'Contains failed')

    def test_size_10_contains_out_list(self):
        value = FloatList([Range(.5, 2.5) for __ in range(10)])
        v = [-2.5, -2., -1.5, -1., -.5, 3., 3.5, 4., 4.5, 5.]
        self.assertFalse(value.contains(v), 'Contains failed')

    def test_size_10_contains_in_out_list(self):
        value = FloatList([Range(.5, 2.5) for __ in range(10)])
        v = [.5, 1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5.]
        self.assertFalse(value.contains(v), 'Contains failed')

    def test_size_10_contains_wrong_len_list(self):
        value = FloatList([Range(.5, 2.5) for __ in range(10)])
        self.assertFalse(value.contains([1.5, 2.]), 'Contains failed')
