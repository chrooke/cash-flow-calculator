#!/bin/env python
import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.once_today = transaction.Transaction(
            start=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        self.once_two_days = transaction.Transaction(
            start=date.today()+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        self.weekly = transaction.Transaction(
            start=date.today(),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY)
        self.biweekly = transaction.Transaction(
            start=date.today(),
            description="Biweekly",
            amount=1.03,
            frequency=transaction.Transaction.BIWEEKLY)
        self.monthly = transaction.Transaction(
            start=date.today(),
            description="Monthly",
            amount=1.04,
            frequency=transaction.Transaction.MONTHLY)
        self.quarterly = transaction.Transaction(
            start=date.today(),
            description="Quarterly",
            amount=1.05,
            frequency=transaction.Transaction.QUARTERLY)
        self.annually = transaction.Transaction(
            start=date.today(),
            description="Annually",
            amount=1.06,
            frequency=transaction.Transaction.ANNUALLY)

    def test_class_constants(self):
        self.assertEqual(transaction.Transaction.ONCE, "O")
        self.assertEqual(transaction.Transaction.WEEKLY, "W")
        self.assertEqual(transaction.Transaction.BIWEEKLY, "2W")
        self.assertEqual(transaction.Transaction.MONTHLY, "M")
        self.assertEqual(transaction.Transaction.QUARTERLY, "Q")
        self.assertEqual(transaction.Transaction.ANNUALLY, "A")

    def test_constructor_empty(self):
        t = transaction.Transaction()
        self.assertIsInstance(t, transaction.Transaction)
        self.assertIsInstance(t.start, date)
        self.assertEqual(t.start, date.today())
        self.assertIsInstance(t.original_start, date)
        self.assertEqual(t.original_start, t.start)
        self.assertIsNone(t.end,
                          f"end not None: {t.end}")
        self.assertIsInstance(t.description, str)
        self.assertEqual(t.description, "")
        self.assertIsInstance(t.amount, float)
        self.assertEqual(t.amount, 0.0)
        self.assertIsInstance(t.frequency, str)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)
        self.assertIsInstance(t.skip, set)
        self.assertEqual(len(t.skip), 0,
                         f"non-empty skip : {t.skip}")
        self.assertIsInstance(t.scheduled, bool)
        self.assertFalse(t.scheduled)
        self.assertIsInstance(t.cleared, bool)
        self.assertFalse(t.cleared)

    def test_constructor_full(self):
        start = date.today()
        original_start = date.today()-timedelta(days=7)
        skip = start + timedelta(days=14)
        end = start+relativedelta(months=1)
        descr = "Test transaction"
        amt = 1.00
        freq = transaction.Transaction.WEEKLY
        t = transaction.Transaction(
            start=start,
            original_start=original_start,
            end=end,
            description=descr,
            amount=amt,
            frequency=freq,
            skip=set([skip]),
            scheduled=True,
            cleared=True)
        self.assertIsInstance(t, transaction.Transaction)
        self.assertIsInstance(t.start, date)
        self.assertEqual(t.start, start)
        self.assertIsInstance(t.original_start, date)
        self.assertEqual(t.original_start, original_start)
        self.assertIsInstance(t.end, date)
        self.assertEqual(t.end, end)
        self.assertIsInstance(t.description, str)
        self.assertEqual(t.description, descr)
        self.assertIsInstance(t.amount, float)
        self.assertEqual(t.amount, amt)
        self.assertIsInstance(t.frequency, str)
        self.assertEqual(t.frequency, freq)
        self.assertIsInstance(t.skip, set)
        self.assertEqual(len(t.skip), 1)
        self.assertIn(skip, t.skip)
        self.assertIsInstance(t.scheduled, bool)
        self.assertTrue(t.scheduled)
        self.assertIsInstance(t.cleared, bool)
        self.assertTrue(t.cleared)

    def test_start_date_hits(self):
        d = date.today()
        self.assertEqual(self.once_today.amtOn(d), 1.00)
        self.assertEqual(self.once_today.amtOn(d+timedelta(days=1)), 0)

    def test_date_after_start_date_hits(self):
        d = date.today()
        self.assertEqual(self.once_two_days.amtOn(d), 0)
        self.assertEqual(self.once_two_days.amtOn(d+timedelta(days=1)), 0)
        self.assertEqual(self.once_two_days.amtOn(d+timedelta(days=2)), 1.01)
        self.assertEqual(self.once_two_days.amtOn(d+timedelta(days=3)), 0)

    def test_weekly_recurrence(self):
        d = date.today()

        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(1, 6):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=7)), 1.02)

        for i in range(8, 13):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=14)), 1.02)

    def test_weekly_recurrence_with_end(self):
        d = date.today()
        self.weekly.end = d+timedelta(days=8)

        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(1, 6):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=7)), 1.02)

        for i in range(8, 13):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=14)), 0)

    def test_weekly_recurrence_with_skip(self):
        d = date.today()
        self.weekly.skip.add(d+timedelta(days=7))

        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(1, 6):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=7)), 0)

        for i in range(8, 13):
            self.assertEqual(self.weekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.weekly.amtOn(d+timedelta(days=14)), 1.02)

    def test_biweekly_recurrence(self):
        d = date.today()

        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(1, 13):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=14)), 1.03)

        for i in range(15, 27):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=28)), 1.03)

    def test_biweekly_recurrence_with_end(self):
        d = date.today()
        self.biweekly.end = d+timedelta(days=15)

        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(1, 13):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=14)), 1.03)

        for i in range(15, 27):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=28)), 0)

    def test_biweekly_recurrence_with_skip(self):
        d = date.today()
        self.biweekly.skip.add(d+timedelta(days=14))

        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(1, 13):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=14)), 0)

        for i in range(15, 27):
            self.assertEqual(self.biweekly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.biweekly.amtOn(d+timedelta(days=28)), 1.03)

    def test_monthly_recurrence(self):
        d = date.today()
        nm = date.today()+relativedelta(months=1)
        nmm1 = (nm-d).days-1
        nmp1 = (nm-d).days+1
        man = date.today()+relativedelta(months=2)
        manm1 = (man-nm).days-1

        self.assertEqual(self.monthly.amtOn(d), 1.04)

        for i in range(1, nmm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(nm), 1.04)

        for i in range(nmp1, manm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(man), 1.04)

    def test_monthly_recurrence_with_end(self):
        d = date.today()
        nm = d+relativedelta(months=1)
        nmm1 = (nm-d).days-1
        nmp1 = (nm-d).days+1
        man = d+relativedelta(months=2)
        manm1 = (man-nm).days-1
        self.monthly.end = nm+relativedelta(days=10)

        self.assertEqual(self.monthly.amtOn(d), 1.04)

        for i in range(1, nmm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(nm), 1.04)

        for i in range(nmp1, manm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(man), 0)

    def test_monthly_recurrence_with_skip_date(self):
        d = date.today()
        nm = d+relativedelta(months=1)
        nmm1 = (nm-d).days-1
        nmp1 = (nm-d).days+1
        man = d+relativedelta(months=2)
        manm1 = (man-nm).days-1
        self.monthly.skip.add(nm)

        self.assertEqual(self.monthly.amtOn(d), 1.04)

        for i in range(1, nmm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(nm), 0)

        for i in range(nmp1, manm1):
            self.assertEqual(self.monthly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.monthly.amtOn(man), 1.04)

    def test_quarterly_recurrence(self):
        d = date.today()
        nq = d+relativedelta(months=3)
        nqm1 = (nq-d).days-1
        nqp1 = (nq-d).days+1
        qan = d+relativedelta(months=6)
        qanm1 = (qan-nq).days-1

        self.assertEqual(self.quarterly.amtOn(d), 1.05)

        for i in range(1, nqm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(nq), 1.05)

        for i in range(nqp1, qanm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(qan), 1.05)

    def test_quarterly_recurrence_with_end(self):
        d = date.today()
        nq = date.today()+relativedelta(months=3)
        nqm1 = (nq-d).days-1
        nqp1 = (nq-d).days+1
        qan = date.today()+relativedelta(months=6)
        qanm1 = (qan-nq).days-1
        self.quarterly.end = d+relativedelta(months=3, days=10)

        self.assertEqual(self.quarterly.amtOn(d), 1.05)

        for i in range(1, nqm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(nq), 1.05)

        for i in range(nqp1, qanm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(qan), 0)

    def test_quarterly_recurrence_with_skip(self):
        d = date.today()
        nq = date.today()+relativedelta(months=3)
        nqm1 = (nq-d).days-1
        nqp1 = (nq-d).days+1
        qan = date.today()+relativedelta(months=6)
        qanm1 = (qan-nq).days-1
        self.quarterly.skip.add(nq)

        self.assertEqual(self.quarterly.amtOn(d), 1.05)

        for i in range(1, nqm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(nq), 0)

        for i in range(nqp1, qanm1):
            self.assertEqual(self.quarterly.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.quarterly.amtOn(qan), 1.05)

    def test_annual_recurrence(self):
        d = date.today()
        ny = d+relativedelta(years=1)
        nym1 = (ny-d).days-1
        nyp1 = (ny-d).days+1
        yan = d+relativedelta(years=2)
        yanm1 = (yan-ny).days-1

        self.assertEqual(self.annually.amtOn(d), 1.06)

        for i in range(1, nym1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(ny), 1.06)

        for i in range(nyp1, yanm1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(yan), 1.06)

    def test_annual_recurrence_with_end(self):
        d = date.today()
        ny = d+relativedelta(years=1)
        nym1 = (ny-d).days-1
        nyp1 = (ny-d).days+1
        yan = d+relativedelta(years=2)
        yanm1 = (yan-ny).days-1
        self.annually.end = d+relativedelta(years=1, days=10)

        self.assertEqual(self.annually.amtOn(d), 1.06)

        for i in range(1, nym1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(ny), 1.06)

        for i in range(nyp1, yanm1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(yan), 0)

    def test_annual_recurrence_with_skip(self):
        d = date.today()
        ny = d+relativedelta(years=1)
        nym1 = (ny-d).days-1
        nyp1 = (ny-d).days+1
        yan = d+relativedelta(years=2)
        yanm1 = (yan-ny).days-1
        self.annually.skip.add(ny)

        self.assertEqual(self.annually.amtOn(d), 1.06)

        for i in range(1, nym1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(ny), 0)

        for i in range(nyp1, yanm1):
            self.assertEqual(self.annually.amtOn(d+timedelta(days=i)), 0)

        self.assertEqual(self.annually.amtOn(yan), 1.06)

    def test_start_date_change_non_recurring(self):
        d = date.today()
        new_base = d + timedelta(days=16)

        self.assertEqual(self.once_today.frequency,
                         transaction.Transaction.ONCE)
        self.assertEqual(self.once_today.start, d)
        self.assertEqual(self.once_today.original_start, d)

        self.once_today.updateStartDate(new_base)

        self.assertEqual(self.once_today.start, new_base)
        self.assertEqual(self.once_today.original_start, d)

    def test_start_date_change_recurring(self):
        d = date.today()
        new_base = d + timedelta(days=16)
        new_start = d + timedelta(days=21)

        self.assertEqual(self.weekly.frequency,
                         transaction.Transaction.WEEKLY)
        self.assertEqual(self.weekly.start, d)
        self.assertEqual(self.weekly.original_start, d)

        self.weekly.updateStartDate(new_base)

        self.assertEqual(self.weekly.start, new_start)
        self.assertEqual(self.weekly.original_start, d)


if __name__ == '__main__':
    unittest.main()
