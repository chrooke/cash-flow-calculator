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

    def test_start_date_hits(self):
        d = date.today()
        self.assertEqual(self.once_today.amtOn(d), 1.00)
        d = date.today()+timedelta(days=1)
        self.assertEqual(self.once_today.amtOn(d), 0)

    def test_date_after_start_date_hits(self):
        d = date.today()
        self.assertEqual(self.once_two_days.amtOn(d), 0)

        d = date.today()+timedelta(days=1)
        self.assertEqual(self.once_two_days.amtOn(d), 0)

        d = date.today()+timedelta(days=2)
        self.assertEqual(self.once_two_days.amtOn(d), 1.01)

        d = date.today()+timedelta(days=3)
        self.assertEqual(self.once_two_days.amtOn(d), 0)

    def test_weekly_recurrence(self):
        d = date.today()
        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(1, 6):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.weekly.amtOn(d), 0)

        d = date.today()+timedelta(days=7)
        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(8, 13):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.weekly.amtOn(d), 0)

        d = date.today()+timedelta(days=14)
        self.assertEqual(self.weekly.amtOn(d), 1.02)

    def test_weekly_recurrence_with_stop_date(self):
        self.weekly.stop_date = date.today()+timedelta(days=8)

        d = date.today()
        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(1, 6):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.weekly.amtOn(d), 0)

        d = date.today()+timedelta(days=7)
        self.assertEqual(self.weekly.amtOn(d), 1.02)

        for i in range(8, 13):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.weekly.amtOn(d), 0)

        d = date.today()+timedelta(days=14)
        self.assertEqual(self.weekly.amtOn(d), 0)

    def test_biweekly_recurrence(self):
        d = date.today()
        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(1, 13):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.biweekly.amtOn(d), 0)

        d = date.today()+timedelta(days=14)
        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(15, 27):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.biweekly.amtOn(d), 0)

        d = date.today()+timedelta(days=28)
        self.assertEqual(self.biweekly.amtOn(d), 1.03)

    def test_biweekly_recurrence_with_stop_date(self):
        self.biweekly.stop_date = date.today()+timedelta(days=15)

        d = date.today()
        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(1, 13):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.biweekly.amtOn(d), 0)

        d = date.today()+timedelta(days=14)
        self.assertEqual(self.biweekly.amtOn(d), 1.03)

        for i in range(15, 27):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.biweekly.amtOn(d), 0)

        d = date.today()+timedelta(days=28)
        self.assertEqual(self.biweekly.amtOn(d), 0)

    def test_monthly_recurrence(self):
        d = date.today()
        nm = date.today()+relativedelta(months=1)
        nmm1 = (nm-d).days-1
        nmp1 = (nm-d).days+1
        man = date.today()+relativedelta(months=2)
        manm1 = (man-nm).days-1

        self.assertEqual(self.monthly.amtOn(d), 1.04)

        for i in range(1, nmm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.monthly.amtOn(d), 0)

        self.assertEqual(self.monthly.amtOn(nm), 1.04)

        for i in range(nmp1, manm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.monthly.amtOn(d), 0)

        self.assertEqual(self.monthly.amtOn(man), 1.04)

    def test_monthly_recurrence_with_stop_date(self):
        self.monthly.stop_date = date.today()+relativedelta(months=1, days=1)

        d = date.today()
        nm = date.today()+relativedelta(months=1)
        nmm1 = (nm-d).days-1
        nmp1 = (nm-d).days+1
        man = date.today()+relativedelta(months=2)
        manm1 = (man-nm).days-1

        self.assertEqual(self.monthly.amtOn(d), 1.04)

        for i in range(1, nmm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.monthly.amtOn(d), 0)

        self.assertEqual(self.monthly.amtOn(nm), 1.04)

        for i in range(nmp1, manm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.monthly.amtOn(d), 0)

        self.assertEqual(self.monthly.amtOn(man), 0)

    def test_quarterly_recurrence(self):
        d = date.today()
        nq = date.today()+relativedelta(months=3)
        nqm1 = (nq-d).days-1
        nqp1 = (nq-d).days+1
        qan = date.today()+relativedelta(months=6)
        qanm1 = (qan-nq).days-1

        self.assertEqual(self.quarterly.amtOn(d), 1.05)

        for i in range(1, nqm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.quarterly.amtOn(d), 0)

        self.assertEqual(self.quarterly.amtOn(nq), 1.05)

        for i in range(nqp1, qanm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.quarterly.amtOn(d), 0)

        self.assertEqual(self.quarterly.amtOn(qan), 1.05)

    def test_quarterly_recurrence_with_stop_date(self):
        self.quarterly.stop_date = date.today()+relativedelta(months=3, days=1)

        d = date.today()
        nq = date.today()+relativedelta(months=3)
        nqm1 = (nq-d).days-1
        nqp1 = (nq-d).days+1
        qan = date.today()+relativedelta(months=6)
        qanm1 = (qan-nq).days-1

        self.assertEqual(self.quarterly.amtOn(d), 1.05)

        for i in range(1, nqm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.quarterly.amtOn(d), 0)

        self.assertEqual(self.quarterly.amtOn(nq), 1.05)

        for i in range(nqp1, qanm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.quarterly.amtOn(d), 0)

        self.assertEqual(self.quarterly.amtOn(qan), 0)

    def test_annual_recurrence(self):
        d = date.today()
        ny = date.today()+relativedelta(years=1)
        nym1 = (ny-d).days-1
        nyp1 = (ny-d).days+1
        yan = date.today()+relativedelta(years=2)
        yanm1 = (yan-ny).days-1

        self.assertEqual(self.annually.amtOn(d), 1.06)

        for i in range(1, nym1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.annually.amtOn(d), 0)

        self.assertEqual(self.annually.amtOn(ny), 1.06)

        for i in range(nyp1, yanm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.annually.amtOn(d), 0)

        self.assertEqual(self.annually.amtOn(yan), 1.06)

    def test_annual_recurrence_with_stop_date(self):
        self.annual.stop_date = date.today()+relativedelta(years=1, days=1)

        d = date.today()
        ny = date.today()+relativedelta(years=1)
        nym1 = (ny-d).days-1
        nyp1 = (ny-d).days+1
        yan = date.today()+relativedelta(years=2)
        yanm1 = (yan-ny).days-1

        self.assertEqual(self.annually.amtOn(d), 1.06)

        for i in range(1, nym1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.annually.amtOn(d), 0)

        self.assertEqual(self.annually.amtOn(ny), 1.06)

        for i in range(nyp1, yanm1):
            d = date.today()+timedelta(days=i)
            self.assertEqual(self.annually.amtOn(d), 0)

        self.assertEqual(self.annually.amtOn(yan), 0)


if __name__ == '__main__':
    unittest.main()
