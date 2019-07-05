#!/bin/env python
import unittest
from datetime import date, timedelta
import transaction


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.once_today = transaction.Transaction(
            start=date.today(),
            description="Once, today",
            amt=1.00,
            frequency=transaction.Transaction.ONCE)
        self.once_two_days = transaction.Transaction(
            start=date.today()+timedelta(days=2),
            description="Once, in two days",
            amt=1.01,
            frequency=transaction.Transaction.ONCE)
        self.weekly = transaction.Transaction(
            start=date.today(),
            description="Weekly",
            amt=1.02,
            frequency=transaction.Transaction.WEEKLY)
        self.biweekly = transaction.Transaction(
            start=date.today(),
            description="Biweekly",
            amt=1.03,
            frequency=transaction.Transaction.BIWEEKLY)
        self.monthly = transaction.Transaction(
            start=date.today(),
            description="Monthly",
            amt=1.04,
            frequency=transaction.Transaction.MONTHLY)
        self.quarterly = transaction.Transaction(
            start=date.today(),
            description="Quarterly",
            amt=1.05,
            frequency=transaction.Transaction.QUARTERLY)
        self.annually = transaction.Transaction(
            start=date.today(),
            description="Biweekly",
            amt=1.06,
            frequency=transaction.Transaction.ANNUALLY)

    def test_class_constants(self):
        self.assertEqual(transaction.Transaction.ONCE, "O")
        self.assertEqual(transaction.Transaction.WEEKLY, "W")
        self.assertEqual(transaction.Transaction.BIWEEKLY, "2W")
        self.assertEqual(transaction.Transaction.MONTHLY, "M")
        self.assertEqual(transaction.Transaction.QUARTERLY, "Q")
        self.assertEqual(transaction.Transaction.ANNUALLY, "A")

    def test_constructor_empty(self):
        self.t = transaction.Transaction()
        self.assertIsInstance(self.t, transaction.Transaction)
        self.assertIsInstance(self.t.start_date, date)
        self.assertEqual(self.t.start_date, date.today())
        self.assertIsNone(self.t.stop_date)
        self.assertIsInstance(self.t.description, str)
        self.assertEqual(self.t.description, "")
        self.assertIsInstance(self.t.amount, float)
        self.assertEqual(self.t.amount, 0.0)
        self.assertIsInstance(self.t.frequency, str)
        self.assertEqual(self.t.frequency, transaction.Transaction.ONCE)
        self.assertEqual(len(self.t.skip_list), 0)

    def test_constructor_full(self):
        start_date = date.today()
        skip_date = start_date + timedelta(days=14)
        stop_date = start_date.replace(month=start_date.month+1)
        descr = "Test transaction"
        amt = 1.00
        freq = transaction.Transaction.WEEKLY
        self.t = transaction.Transaction(
            start=start_date,
            end=stop_date,
            description=descr,
            amt=amt,
            frequency=freq,
            skip=[skip_date])
        self.assertIsInstance(self.t, transaction.Transaction)
        self.assertIsInstance(self.t.start_date, date)
        self.assertEqual(self.t.start_date, start_date)
        self.assertIsInstance(self.t.stop_date, date)
        self.assertEqual(self.t.stop_date, stop_date)
        self.assertIsInstance(self.t.description, str)
        self.assertEqual(self.t.description, descr)
        self.assertIsInstance(self.t.amount, float)
        self.assertEqual(self.t.amount, amt)
        self.assertIsInstance(self.t.frequency, str)
        self.assertEqual(self.t.frequency, freq)
        self.assertEqual(len(self.t.skip_list), 1)
        self.assertEqual(self.t.skip_list[0], skip_date)

    def test_once_today_only(self):
        d = date.today()
        self.assertEqual(self.once_today.amtOn(d), 1.00)
        d = date.today()+timedelta(days=1)
        self.assertEqual(self.once_today.amtOn(d), 0)

    def test_once_two_days(self):
        d = date.today()
        self.assertEqual(self.once_two_days.amtOn(d), 0)
        d = date.today()+timedelta(days=1)
        self.assertEqual(self.once_two_days.amtOn(d), 0)
        d = date.today()+timedelta(days=2)
        self.assertEqual(self.once_two_days.amtOn(d), 1.01)
        d = date.today()+timedelta(days=3)
        self.assertEqual(self.once_two_days.amtOn(d), 0)


if __name__ == '__main__':
    unittest.main()
