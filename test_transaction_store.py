#!/bin/env python
import unittest
import time
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction
from transaction_store import TransactionStore


class TestTransactionStore(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()
        self.ts.add(
            start=date.today(),
            description="Once, today",
            amt=1.00,
            frequency=transaction.Transaction.ONCE)
        self.ts.add(
            start=date.today()+timedelta(days=2),
            description="Once, in two days",
            amt=1.01,
            frequency=transaction.Transaction.ONCE)
        self.ts.add(
            start=date.today(),
            end=date.today()+timedelta(days=56),
            description="Weekly",
            amt=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip=[date.today()+timedelta(days=7)],
            scheduled=True,
            cleared=True)

    def test_constructor(self):
        ts = TransactionStore()
        self.assertIsInstance(ts.store, list)

    def test_file_operations(self):
        file = f'test-{time.time()}'

        self.assertEqual(len(self.ts.store), 3)

        t_once_today = next((t for t in self.ts.store if t.amount == 1.00),
                            None)
        sd = date.today()
        self.assertIsNotNone(t_once_today)
        self.assertEqual(t_once_today.start_date, sd)
        self.assertEqual(t_once_today.original_start_date, sd)
        self.assertIsNone(t_once_today.end_date)
        self.assertEqual(t_once_today.description, "Once, today")
        self.assertEqual(t_once_today.amount, 1.00)
        self.assertEqual(t_once_today.frequency, transaction.Transaction.ONCE)
        self.assertEqual(len(t_once_today.skip_list), 0)
        self.assertFalse(t_once_today.scheduled)
        self.assertFalse(t_once_today.cleared)

        t_once_two = next((t for t in self.ts.store if t.amount == 1.01),
                          None)
        sd = date.today()+timedelta(days=2)
        self.assertIsNotNone(t_once_two)
        self.assertEqual(t_once_two.start_date, sd)
        self.assertEqual(t_once_two.original_start_date, sd)
        self.assertIsNone(t_once_two.end_date)
        self.assertEqual(t_once_two.description, "Once, in two days")
        self.assertEqual(t_once_two.amount, 1.01)
        self.assertEqual(t_once_two.frequency, transaction.Transaction.ONCE)
        self.assertEqual(len(t_once_two.skip_list), 0)
        self.assertFalse(t_once_two.scheduled)
        self.assertFalse(t_once_two.cleared)

        t_weekly = next((t for t in self.ts.store if t.amount == 1.02),
                        None)
        sd = date.today()
        ed = date.today()+timedelta(days=56)
        self.assertIsNotNone(t_weekly)
        self.assertEqual(t_weekly.start_date, sd)
        self.assertEqual(t_weekly.original_start_date, sd)
        self.assertEqual(t_weekly.end_date, ed)
        self.assertEqual(t_weekly.description, "Weekly")
        self.assertEqual(t_weekly.amount, 1.02)
        self.assertEqual(t_weekly.frequency, transaction.Transaction.WEEKLY)
        self.assertEqual(len(t_weekly.skip_list), 1)
        self.assertEqual(t_weekly.skip_list[0], date.today()+timedelta(days=7))
        self.assertTrue(t_weekly.scheduled)
        self.assertTrue(t_weekly.cleared)

        self.ts.saveTransactions(file)
        ts = TransactionStore()
        ts.loadTransactions(file)

        self.assertEqual(len(ts.store), 3)

        t_once_today = next((t for t in ts.store if t.amount == 1.00),
                            None)
        sd = date.today()
        self.assertIsNotNone(t_once_today)
        self.assertEqual(t_once_today.start_date, sd)
        self.assertEqual(t_once_today.original_start_date, sd)
        self.assertIsNone(t_once_today.end_date)
        self.assertEqual(t_once_today.description, "Once, today")
        self.assertEqual(t_once_today.amount, 1.00)
        self.assertEqual(t_once_today.frequency, transaction.Transaction.ONCE)
        self.assertEqual(len(t_once_today.skip_list), 0)
        self.assertFalse(t_once_today.scheduled)
        self.assertFalse(t_once_today.cleared)

        t_once_two = next((t for t in ts.store if t.amount == 1.01),
                          None)
        sd = date.today()+timedelta(days=2)
        self.assertIsNotNone(t_once_two)
        self.assertEqual(t_once_two.start_date, sd)
        self.assertEqual(t_once_two.original_start_date, sd)
        self.assertIsNone(t_once_two.end_date)
        self.assertEqual(t_once_two.description, "Once, in two days")
        self.assertEqual(t_once_two.amount, 1.01)
        self.assertEqual(t_once_two.frequency, transaction.Transaction.ONCE)
        self.assertEqual(len(t_once_two.skip_list), 0)
        self.assertFalse(t_once_two.scheduled)
        self.assertFalse(t_once_two.cleared)

        t_weekly = next((t for t in ts.store if t.amount == 1.02),
                        None)
        sd = date.today()
        self.assertIsNotNone(t_weekly)
        self.assertEqual(t_weekly.start_date, sd)
        self.assertEqual(t_weekly.original_start_date, sd)
        self.assertEqual(t_weekly.end_date, date.today()+timedelta(days=56))
        self.assertEqual(t_weekly.description, "Weekly")
        self.assertEqual(t_weekly.amount, 1.02)
        self.assertEqual(t_weekly.frequency, transaction.Transaction.WEEKLY)
        self.assertEqual(len(t_weekly.skip_list), 1)
        self.assertEqual(t_weekly.skip_list[0], date.today()+timedelta(days=7))
        self.assertTrue(t_weekly.scheduled)
        self.assertTrue(t_weekly.cleared)

    def test_add_transaction_to_store(self):
        d = date.today()
        t = TransactionStore()
        self.assertEqual(len(t.store), 0)
        t.add(
            start=d,
            description="Once, today",
            amt=1.00,
            frequency=transaction.Transaction.ONCE)
        self.assertEqual(len(t.store), 1)
        self.assertEqual(t.store[0].start_date, d)
        self.assertEqual(t.store[0].description, "Once, today")
        self.assertEqual(t.store[0].amount, 1.00)
        self.assertEqual(t.store[0].frequency, transaction.Transaction.ONCE)

    def test_remove_single_transaction_from_store(self):
        pass

    def test_remove_recurring_transaction_from_store(self):
        pass

    def test_make_override_transaction(self):
        pass

    def test_update_all_start_dates(self):
        pass

    def test_purge_outdated_single_transactions(self):
        pass
