#!/bin/env python
import unittest
import time
import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction
from transaction_store import TransactionStore


class TestTransactionStore(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        t1 = transaction.Transaction(
            start_date=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start_date=date.today()+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        t3 = transaction.Transaction(
            start_date=date.today(),
            end_date=date.today()+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip_list=[date.today()+timedelta(days=7)],
            scheduled=True,
            cleared=True)

        self.ts.add(t1, t2, t3)

    def test_constructor(self):
        ts = TransactionStore()
        self.assertIsInstance(ts.store, list)

    def test_add_single_transaction_to_store(self):
        d = date.today()
        ts = TransactionStore()
        self.assertEqual(len(ts.store), 0)
        t = transaction.Transaction(
            start_date=d,
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        ts.add(t)
        self.assertEqual(len(ts.store), 1)
        t = next((t for t in self.ts.store if t.amount == 1.00),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d)
        self.assertEqual(t.description, "Once, today")
        self.assertEqual(t.amount, 1.00)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

    def test_add_multiple_transactions(self):
        d = date.today()
        ts = TransactionStore()
        t1 = transaction.Transaction(
            start_date=d,
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start_date=d+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        t3 = transaction.Transaction(
            start_date=d,
            end_date=d+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip_list=[d+timedelta(days=7)],
            scheduled=True,
            cleared=True)

        self.assertEqual(len(ts.store), 0)

        ts.add(t1, t2, t3)

        t = next((t for t in self.ts.store if t.amount == 1.00),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d)
        self.assertEqual(t.description, "Once, today")
        self.assertEqual(t.amount, 1.00)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in self.ts.store if t.amount == 1.01),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d+timedelta(days=2))
        self.assertEqual(t.description, "Once, in two days")
        self.assertEqual(t.amount, 1.01)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in self.ts.store if t.amount == 1.02),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d)
        self.assertEqual(t.description, "Weekly")
        self.assertEqual(t.amount, 1.02)
        self.assertEqual(t.frequency, transaction.Transaction.WEEKLY)

    def test_file_operations(self):
        file = f'./test-{time.time()}'

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

        os.remove(file)

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
