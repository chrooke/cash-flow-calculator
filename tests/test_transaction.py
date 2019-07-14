#!/bin/env python
import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import context
from cash_flow.transaction import Transaction


class TestConstructor(unittest.TestCase):

    def test_class_constants(self):
        self.assertEqual(Transaction.ONCE, "O")
        self.assertEqual(Transaction.WEEKLY, "W")
        self.assertEqual(Transaction.BIWEEKLY, "2W")
        self.assertEqual(Transaction.MONTHLY, "M")
        self.assertEqual(Transaction.QUARTERLY, "Q")
        self.assertEqual(Transaction.ANNUALLY, "A")
        self.assertEqual(len(Transaction.INTERVALS), 6)
        self.assertTrue(Transaction.ONCE in Transaction.INTERVALS)
        self.assertTrue(Transaction.WEEKLY in Transaction.INTERVALS)
        self.assertTrue(Transaction.BIWEEKLY in Transaction.INTERVALS)
        self.assertTrue(Transaction.MONTHLY in Transaction.INTERVALS)
        self.assertTrue(Transaction.QUARTERLY in Transaction.INTERVALS)        
        self.assertTrue(Transaction.ANNUALLY in Transaction.INTERVALS)

    def test_constructor_empty(self):
        t = Transaction()
        self.assertIsInstance(t, Transaction)
        self.assertIsInstance(t.start, date)
        self.assertEqual(t.start, date.today())
        self.assertIsInstance(t.original_start, date)
        self.assertEqual(t.original_start, t.start)
        self.assertIsNone(t.end,
                          f"end not None: {t.end}")
        self.assertIsInstance(t.description, str)
        self.assertEqual(t.description, "<Description>")
        self.assertIsInstance(t.amount, float)
        self.assertEqual(t.amount, 0.0)
        self.assertIsInstance(t.frequency, str)
        self.assertEqual(t.frequency, Transaction.ONCE)
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
        freq = Transaction.WEEKLY
        t = Transaction(
            start=start,
            original_start=original_start,
            end=end,
            description=descr,
            amount=amt,
            frequency=freq,
            skip=set([skip]),
            scheduled=True,
            cleared=True)
        self.assertIsInstance(t, Transaction)
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


class TestDuplicateTransaction(unittest.TestCase):
    def setUp(self):
        sd = date.today()
        self.t1 = Transaction(
            start=sd,
            original_start=sd-timedelta(days=1),
            end=sd+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=Transaction.WEEKLY,
            skip=set([sd+timedelta(days=7)]),
            scheduled=True,
            cleared=True)

    def test_duplicate_transaction(self):
        t2 = self.t1.duplicate()
        self.assertEqual(self.t1.start, t2.start)
        self.assertEqual(self.t1.original_start, t2.original_start)
        self.assertEqual(self.t1.end, t2.end)
        self.assertEqual(self.t1.description, t2.description)
        self.assertEqual(self.t1.amount, t2.amount)
        self.assertEqual(self.t1.frequency, t2.frequency)
        self.assertEqual(self.t1.skip.symmetric_difference(t2.skip), set())
        self.assertEqual(self.t1.scheduled, t2.scheduled)
        self.assertEqual(self.t1.cleared, t2.cleared)


class TestRecurrence(unittest.TestCase):
    def assertRecurrence(self, t,
                         start_date, start_value,
                         gap1_end,
                         middle_date, middle_value,
                         gap2_start, gap2_end,
                         final_date, final_value):
        self.assertEqual(t.amtOn(start_date), start_value)

        for i in range(1, gap1_end):
            self.assertEqual(t.amtOn(start_date+timedelta(days=i)), 0)

        self.assertEqual(t.amtOn(middle_date), middle_value)

        for i in range(gap2_start, gap2_end):
            self.assertEqual(t.amtOn(start_date+timedelta(days=i)), 0)


class TestWeeklyRecurrence(TestRecurrence):
    def setUp(self):
        self.t = Transaction(
            start=date.today(),
            description="Weekly",
            amount=1.02,
            frequency=Transaction.WEEKLY)
        self.sd = self.t.start
        self.nw = self.sd + timedelta(days=7)
        self.nw_days = (self.nw-self.sd).days
        self.nwp1_days = self.nw_days+1
        self.wan = self.sd + timedelta(days=14)
        self.wan_days = (self.wan-self.sd).days

    def test_recurrence(self):
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nw_days,
                              self.nw, self.t.amount,
                              self.nwp1_days, self.wan_days,
                              self.wan, self.t.amount)

    def test_recurrence_with_end(self):
        self.t.end = self.nw+timedelta(days=1)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nw_days,
                              self.nw, self.t.amount,
                              self.nwp1_days, self.wan_days,
                              self.wan, 0)

    def test_recurrence_with_skip(self):
        self.t.skip.add(self.nw)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nw_days,
                              self.nw, 0,
                              self.nwp1_days, self.wan_days,
                              self.wan, self.t.amount)


class TestBiweeklyRecurrence(TestRecurrence):
    def setUp(self):
        self.t = Transaction(
            start=date.today(),
            description="Biweekly",
            amount=1.03,
            frequency=Transaction.BIWEEKLY)
        self.sd = self.t.start
        self.nbw = self.sd + timedelta(days=14)
        self.nbw_days = (self.nbw-self.sd).days
        self.nbwp1_days = self.nbw_days+1
        self.bwan = self.sd + timedelta(days=28)
        self.bwan_days = (self.bwan-self.sd).days

    def test_recurrence(self):
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nbw_days,
                              self.nbw, self.t.amount,
                              self.nbwp1_days, self.bwan_days,
                              self.bwan, self.t.amount)

    def test_recurrence_with_end(self):
        self.t.end = self.nbw+timedelta(days=1)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nbw_days,
                              self.nbw, self.t.amount,
                              self.nbwp1_days, self.bwan_days,
                              self.bwan, 0)

    def test_recurrence_with_skip(self):
        self.t.skip.add(self.nbw)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nbw_days,
                              self.nbw, 0,
                              self.nbwp1_days, self.bwan_days,
                              self.bwan, self.t.amount)


class TestMonthlyRecurrence(TestRecurrence):
    def setUp(self):
        self.t = Transaction(
            start=date.today(),
            description="Monthly",
            amount=1.04,
            frequency=Transaction.MONTHLY)
        self.sd = self.t.start
        self.nm = self.sd + relativedelta(months=1)
        self.nm_days = (self.nm-self.sd).days
        self.nmp1_days = self.nm_days+1
        self.man = self.sd+relativedelta(months=2)
        self.man_days = (self.man-self.sd).days

    def test_recurrence(self):
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nm_days,
                              self.nm, self.t.amount,
                              self.nmp1_days, self.man_days,
                              self.man, self.t.amount)

    def test_recurrence_with_end(self):
        self.t.end = self.nm+relativedelta(days=10)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nm_days,
                              self.nm, self.t.amount,
                              self.nmp1_days, self.man_days,
                              self.man, 0)

    def test_recurrence_with_skip(self):
        self.t.skip.add(self.nm)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nm_days,
                              self.nm, 0,
                              self.nmp1_days, self.man_days,
                              self.man, self.t.amount)


class TestQuarterlyRecurrence(TestRecurrence):
    def setUp(self):
        self.t = Transaction(
            start=date.today(),
            description="Quarterly",
            amount=1.05,
            frequency=Transaction.QUARTERLY)
        self.sd = self.t.start
        self.nq = self.sd + relativedelta(months=3)
        self.nq_days = (self.nq-self.sd).days
        self.nqp1_days = self.nq_days+1
        self.qan = self.sd+relativedelta(months=6)
        self.qan_days = (self.qan-self.sd).days

    def test_recurrence(self):
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nq_days,
                              self.nq, self.t.amount,
                              self.nqp1_days, self.qan_days,
                              self.qan, self.t.amount)

    def test_recurrence_with_end(self):
        self.t.end = self.nq+relativedelta(days=10)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nq_days,
                              self.nq, self.t.amount,
                              self.nqp1_days, self.qan_days,
                              self.qan, 0)

    def test_recurrence_with_skip(self):
        self.t.skip.add(self.nq)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.nq_days,
                              self.nq, 0,
                              self.nqp1_days, self.qan_days,
                              self.qan, self.t.amount)


class TestAnnualRecurrence(TestRecurrence):
    def setUp(self):
        self.t = Transaction(
            start=date.today(),
            description="Annually",
            amount=1.06,
            frequency=Transaction.ANNUALLY)
        self.sd = self.t.start
        self.ny = self.sd + relativedelta(years=1)
        self.ny_days = (self.ny-self.sd).days
        self.nyp1_days = self.ny_days+1
        self.yan = self.sd + relativedelta(years=2)
        self.yan_days = (self.yan-self.sd).days

    def test_recurrence(self):
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.ny_days,
                              self.ny, self.t.amount,
                              self.nyp1_days, self.yan_days,
                              self.yan, self.t.amount)

    def test_recurrence_with_end(self):
        self.t.end = self.ny+relativedelta(days=10)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.ny_days,
                              self.ny, self.t.amount,
                              self.nyp1_days, self.yan_days,
                              self.yan, 0)

    def test_recurrence_with_skip(self):
        self.t.skip.add(self.ny)
        self.assertRecurrence(self.t,
                              self.sd, self.t.amount,
                              self.ny_days,
                              self.ny, 0,
                              self.nyp1_days, self.yan_days,
                              self.yan, self.t.amount)


class TestOneTimeTransactionHits(unittest.TestCase):
    def setUp(self):
        self.sd = date.today()
        self.sdp1 = self.sd + timedelta(days=1)
        self.sdp2 = self.sd + timedelta(days=2)
        self.sdp3 = self.sd + timedelta(days=3)
        self.t1 = Transaction(
            start=self.sd,
            description="Once, today",
            amount=1.00,
            frequency=Transaction.ONCE)
        self.t2 = Transaction(
            start=self.sdp2,
            description="Once, in two days",
            amount=1.01,
            frequency=Transaction.ONCE)

    def test_start_date_hits(self):
        self.assertEqual(self.t1.amtOn(self.sd), self.t1.amount)
        self.assertEqual(self.t1.amtOn(self.sdp1), 0)

    def test_date_after_start_date_hits(self):
        self.assertEqual(self.t2.amtOn(self.sd), 0)
        self.assertEqual(self.t2.amtOn(self.sdp1), 0)
        self.assertEqual(self.t2.amtOn(self.sdp2), self.t2.amount)
        self.assertEqual(self.t2.amtOn(self.sdp3), 0)


class TestStartDateChange(unittest.TestCase):

    def setUp(self):
        self.sd = date.today()
        self.t1 = Transaction(
            start=self.sd,
            description="Once, today",
            amount=1.00,
            frequency=Transaction.ONCE)
        self.t2 = Transaction(
            start=self.sd,
            description="Weekly",
            amount=1.02,
            frequency=Transaction.WEEKLY)

    def test_start_date_change_non_recurring(self):
        new_base = self.sd + timedelta(days=16)

        self.assertEqual(self.t1.frequency,
                         Transaction.ONCE)
        self.assertEqual(self.t1.start, self.sd)
        self.assertEqual(self.t1.original_start, self.sd)

        self.t1.updateStartDate(new_base)

        self.assertEqual(self.t1.start, new_base)
        self.assertEqual(self.t1.original_start, self.sd)

    def test_start_date_change_recurring(self):
        new_base = self.sd + timedelta(days=16)
        new_start = self.sd + timedelta(days=21)

        self.assertEqual(self.t2.frequency,
                         Transaction.WEEKLY)
        self.assertEqual(self.t2.start, self.sd)
        self.assertEqual(self.t2.original_start, self.sd)

        self.t2.updateStartDate(new_base)

        self.assertEqual(self.t2.start, new_start)
        self.assertEqual(self.t2.original_start, self.sd)


if __name__ == '__main__':
    unittest.main()
