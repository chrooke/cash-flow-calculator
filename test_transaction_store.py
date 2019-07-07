#!/bin/env python
import unittest
import time
import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction
from transaction_store import TransactionStore


# CREATE
class TestCreate(unittest.TestCase):
    def test_add_single_transaction(self):
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
        t = next((t for t in ts.store if t.amount == 1.00),
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

        t = next((t for t in ts.store if t.amount == 1.00),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d)
        self.assertEqual(t.description, "Once, today")
        self.assertEqual(t.amount, 1.00)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in ts.store if t.amount == 1.01),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d+timedelta(days=2))
        self.assertEqual(t.description, "Once, in two days")
        self.assertEqual(t.amount, 1.01)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in ts.store if t.amount == 1.02),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start_date, d)
        self.assertEqual(t.description, "Weekly")
        self.assertEqual(t.amount, 1.02)
        self.assertEqual(t.frequency, transaction.Transaction.WEEKLY)


# READ
class TestRetrieveFromMultipleSingleTransactions(unittest.TestCase):
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

        self.ts.add(t1, t2)

    def test_retrieve_non_existent_transaction(self):
        t_list = self.ts.getTransaction("Transaction does not exist")
        self.assertEqual(len(t_list), 0)

    def test_retrieve_no_date_given(self):
        t_list = self.ts.getTransaction("Once, today")
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Once, today")

    def test_retrieve_good_date_given(self):
        retrieve_date = date.today()
        t_list = self.ts.getTransaction("Once, today",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Once, today")
        self.assertEqual(t_list[0].amount, 1.00)

    def test_retrieve_bad_date_given(self):
        retrieve_date = date.today() + timedelta(days=3)
        t_list = self.ts.getTransaction("Once, today",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 0)


class TestRetrieveFromMultipleDuplicateSingleTransactions(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        t1 = transaction.Transaction(
            start_date=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)

        t2 = transaction.Transaction(
            start_date=date.today()+timedelta(days=4),
            description="Once, today",
            amount=1.02,
            frequency=transaction.Transaction.ONCE)

        self.ts.add(t1, t2)

    def test_retrieve_no_date_given(self):
        t_list = self.ts.getTransaction("Once, today")
        self.assertEqual(len(t_list), 2)
        self.assertEqual(t_list[0].description, "Once, today")
        self.assertEqual(t_list[0].description, "Once, today")

    def test_retrieve_good_date_given(self):
        retrieve_date = date.today()
        t_list = self.ts.getTransaction("Once, today",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Once, today")
        self.assertEqual(t_list[0].amount, 1.00)

        retrieve_date = date.today()+timedelta(days=4)
        t_list = self.ts.getTransaction("Once, today",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Once, today")
        self.assertEqual(t_list[0].amount, 1.02)

    def test_retrieve_bad_date_given(self):
        retrieve_date = date.today() + timedelta(days=3)
        t_list = self.ts.getTransaction("Once, today",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 0)


# UPDATE
class TestUpdate(unittest.TestCase):
    pass


# DELETE
class TestDelete(unittest.TestCase):
    pass


# MISC
class TestConstructor(unittest.TestCase):
    def test_constructor(self):
        ts = TransactionStore()
        self.assertIsInstance(ts.store, list)


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.file = f'./test-{time.time()}'

        t1 = transaction.Transaction(
            start_date=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start_date=date.today(),
            original_start_date=date.today()-timedelta(days=1),
            end_date=date.today()+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip_list=[date.today()+timedelta(days=7)],
            scheduled=True,
            cleared=True)

        self.ts = TransactionStore()
        self.ts.store.append(t1)
        self.ts.store.append(t2)

    def tearDown(self):
        os.remove(self.file)

    def assertTransactionsEqual(self, t1, t2):
        self.assertEqual(t1.start_date, t2.start_date)
        self.assertEqual(t1.original_start_date, t2.original_start_date)
        self.assertEqual(t1.end_date, t2.end_date)
        self.assertEqual(t1.description, t2.description)
        self.assertEqual(t1.amount, t2.amount)
        self.assertEqual(t1.frequency, t2.frequency)
        self.assertEqual(sorted(t1.skip_list), sorted(t2.skip_list))
        self.assertEqual(t1.scheduled, t2.scheduled)
        self.assertEqual(t1.cleared, t2.cleared)

    def test_file_operations(self):
        self.assertEqual(len(self.ts.store), 2)

        t1 = next((t for t in self.ts.store if t.amount == 1.00),
                  None)
        self.assertIsNotNone(t1)

        t2 = next((t for t in self.ts.store if t.amount == 1.02),
                  None)
        self.assertIsNotNone(t2)

        self.ts.saveTransactions(self.file)

        ts = TransactionStore()
        ts.loadTransactions(self.file)

        self.assertEqual(len(ts.store), 2)

        t1_l = next((t for t in ts.store if t.amount == 1.00),
                    None)
        self.assertIsNotNone(t1_l)
        self.assertTransactionsEqual(t1_l, t1)

        t2_l = next((t for t in ts.store if t.amount == 1.02),
                    None)
        self.assertIsNotNone(t2_l)
        self.assertTransactionsEqual(t2_l, t2)


class TestUtilityFunctions(unittest.TestCase):
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

    def test_update_all_start_dates(self):
        pass

    def test_purge_outdated_single_transactions(self):
        pass
