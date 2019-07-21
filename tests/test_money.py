#!/bin/env python
import unittest
from decimal import Decimal
import context
from cash_flow.money import Money


class TestConstructor(unittest.TestCase):
    def test_empty_constructor(self):
        m = Money()
        self.assertIsInstance(m, Money)
        self.assertEqual(m.value, Decimal(0.0))

    def test_received_float(self):
        m = Money(1.54)
        self.assertIsInstance(m, Money)
        self.assertEqual(m.value, Decimal('1.54'))

    def test_received_string(self):
        m = Money('1.54')
        self.assertIsInstance(m, Money)
        self.assertEqual(m.value, Decimal('1.54'))

    def test_received_money(self):
        m = Money(Money('1.54'))
        self.assertIsInstance(m, Money)
        self.assertEqual(m.value, Decimal('1.54'))


class TestRepresentation(unittest.TestCase):
    def test_repr_no_decimals(self):
        m = Money('1')
        self.assertEqual(repr(m), "1.00")

    def test_repr_one_decimal(self):
        m = Money('1.2')
        self.assertEqual(repr(m), "1.20")

    def test_repr_two_decimals(self):
        m = Money('1.23')
        self.assertEqual(repr(m), "1.23")

    def test_str_no_decimals(self):
        m = Money('1')
        self.assertEqual(str(m), "1.00")

    def test_str_one_decimal(self):
        m = Money('1.2')
        self.assertEqual(str(m), "1.20")

    def test_str_two_decimals(self):
        m = Money('1.23')
        self.assertEqual(str(m), "1.23")


class TestAddition(unittest.TestCase):
    def test_add_money_and_money(self):
        m1 = Money(1.25)
        m2 = Money(1.26)
        m3 = m1 + m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "2.51")

    def test_add_money_and_float(self):
        m1 = Money(1.25)
        m2 = 1.26
        m3 = m1 + m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "2.51")

    def test_add_money_and_string(self):
        m1 = Money(1.25)
        m2 = '1.26'
        m3 = m1 + m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "2.51")


class TestSubtraction(unittest.TestCase):
    def test_subtract_money_and_money(self):
        m1 = Money(2.51)
        m2 = Money(1.26)
        m3 = m1 - m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "1.25")

    def test_subtract_money_and_float(self):
        m1 = Money(2.51)
        m2 = 1.26
        m3 = m1 - m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "1.25")

    def test_subtract_money_and_string(self):
        m1 = Money(2.51)
        m2 = '1.26'
        m3 = m1 - m2
        self.assertIsInstance(m3, Money)
        self.assertEqual(repr(m3), "1.25")


class TestEquality(unittest.TestCase):
    def test_money_eq_money(self):
        m1 = Money(1.25)
        m2 = Money(1.25)
        self.assertEqual(m1, m2)

    def test_money_neq_money(self):
        m1 = Money(1.25)
        m2 = Money(1.26)
        self.assertNotEqual(m1, m2)

    def test_money_eq_float(self):
        m1 = Money(1.25)
        m2 = 1.25
        self.assertEqual(m1, m2)

    def test_money_neq_float(self):
        m1 = Money(1.25)
        m2 = 1.26
        self.assertNotEqual(m1, m2)

    def test_money_eq_string(self):
        m1 = Money(1.25)
        m2 = '1.25'
        self.assertEqual(m1, m2)

    def test_money_neq_string(self):
        m1 = Money(1.25)
        m2 = '1.26'
        self.assertNotEqual(m1, m2)


class TestComparision(unittest.TestCase):
    def setUp(self):
        self.m1 = Money(1.25)
        self.m2 = Money(1.26)
        self.m3 = Money(1.25)
        self.f1 = 1.25
        self.f2 = 1.26
        self.f3 = 1.25
        self.s1 = '1.25'
        self.s2 = '1.26'
        self.s3 = '1.25'

    def test_money_lt_money(self):
        self.assertLess(self.m1, self.m2)

    def test_money_le_money(self):
        self.assertLessEqual(self.m1, self.m2)
        self.assertLessEqual(self.m1, self.m3)

    def test_money_gt_money(self):
        self.assertGreater(self.m2, self.m1)

    def test_money_ge_money(self):
        self.assertGreaterEqual(self.m2, self.m1)
        self.assertGreaterEqual(self.m3, self.m1)

    def test_money_lt_float(self):
        self.assertLess(self.m1, self.f2)

    def test_money_le_float(self):
        self.assertLessEqual(self.m1, self.f2)
        self.assertLessEqual(self.m1, self.f3)

    def test_money_gt_float(self):
        self.assertGreater(self.m2, self.f1)

    def test_money_ge_float(self):
        self.assertGreaterEqual(self.m2, self.f1)
        self.assertGreaterEqual(self.m3, self.f1)

    def test_money_lt_string(self):
        self.assertLess(self.m1, self.s2)

    def test_money_le_string(self):
        self.assertLessEqual(self.m1, self.s2)
        self.assertLessEqual(self.m1, self.s3)

    def test_money_gt_string(self):
        self.assertGreater(self.m2, self.s1)

    def test_money_ge_string(self):
        self.assertGreaterEqual(self.m2, self.s1)
        self.assertGreaterEqual(self.m3, self.s1)


if __name__ == '__main__':
    unittest.main()