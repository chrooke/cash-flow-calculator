#!/bin/env python
import unittest
import time
import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction
from transaction_store import TransactionStore


# CREATE
class TestBasicCreate(unittest.TestCase):
    def test_add_single_transaction(self):
        d = date.today()
        ts = TransactionStore()
        self.assertEqual(len(ts.store), 0)
        t = transaction.Transaction(
            start=d,
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        ts.addTransactions(t)
        self.assertEqual(len(ts.store), 1)
        t = next((t for t in ts.store if t.amount == 1.00),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start, d)
        self.assertEqual(t.description, "Once, today")
        self.assertEqual(t.amount, 1.00)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

    def test_add_multiple_transactions(self):
        d = date.today()
        ts = TransactionStore()
        t1 = transaction.Transaction(
            start=d,
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start=d+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        t3 = transaction.Transaction(
            start=d,
            end=d+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip=set([d+timedelta(days=7)]),
            scheduled=True,
            cleared=True)

        self.assertEqual(len(ts.store), 0)

        ts.addTransactions(t1, t2, t3)

        t = next((t for t in ts.store if t.amount == 1.00),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start, d)
        self.assertEqual(t.description, "Once, today")
        self.assertEqual(t.amount, 1.00)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in ts.store if t.amount == 1.01),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start, d+timedelta(days=2))
        self.assertEqual(t.description, "Once, in two days")
        self.assertEqual(t.amount, 1.01)
        self.assertEqual(t.frequency, transaction.Transaction.ONCE)

        t = next((t for t in ts.store if t.amount == 1.02),
                 None)
        self.assertIsNotNone(t)
        self.assertEqual(t.start, d)
        self.assertEqual(t.description, "Weekly")
        self.assertEqual(t.amount, 1.02)
        self.assertEqual(t.frequency, transaction.Transaction.WEEKLY)


# READ
class TestRetrieveFromMultipleSingleTransactions(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        t1 = transaction.Transaction(
            start=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start=date.today()+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)

        self.ts.addTransactions(t1, t2)

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
            start=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)

        t2 = transaction.Transaction(
            start=date.today()+timedelta(days=4),
            description="Once, today",
            amount=1.02,
            frequency=transaction.Transaction.ONCE)

        self.ts.addTransactions(t1, t2)

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


class TestRetrieveFromMultipleRecurringTransactions(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        sd = date.today()
        skipd = date.today() + timedelta(days=14)
        t1 = transaction.Transaction(
            start=sd,
            description="Weekly",
            amount=1.00,
            frequency=transaction.Transaction.WEEKLY,
            skip=set([skipd]))
        t2 = transaction.Transaction(
            start=sd+timedelta(days=2),
            description="Monthly",
            amount=1.01,
            frequency=transaction.Transaction.MONTHLY)

        self.ts.addTransactions(t1, t2)

    def test_retrieve_non_existent_transaction(self):
        t_list = self.ts.getTransaction("Transaction does not exist")
        self.assertEqual(len(t_list), 0)

    def test_retrieve_no_date_given(self):
        t_list = self.ts.getTransaction("Weekly")
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Weekly")

    def test_retrieve_good_start_date_given(self):
        retrieve_date = date.today()
        t_list = self.ts.getTransaction("Weekly",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Weekly")
        self.assertEqual(t_list[0].amount, 1.00)

    def test_retrieve_good_future_date_given(self):
        retrieve_date = date.today() + timedelta(days=21)
        t_list = self.ts.getTransaction("Weekly",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 1)
        self.assertEqual(t_list[0].description, "Weekly")
        self.assertEqual(t_list[0].amount, 1.00)

    def test_retrieve_skip_date_given(self):
        retrieve_date = date.today() + timedelta(days=14)
        t_list = self.ts.getTransaction("Weekly",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 0)

    def test_retrieve_bad_date_given(self):
        retrieve_date = date.today() + timedelta(days=3)
        t_list = self.ts.getTransaction("Weekly",
                                        requested_date=retrieve_date)
        self.assertEqual(len(t_list), 0)


# UPDATE (replace old with new)
class TestBasicUpdate(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        t1 = transaction.Transaction(
            start=date.today(),
            description="Once",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)

        self.ts.addTransactions(t1)

    def test_replace(self):
        ts = self.ts.getTransaction("Once")
        self.assertEqual(len(ts), 1)
        t1 = ts[0]
        t2 = t1.duplicate()
        t2.description = "Once replaced"
        self.ts.replaceTransaction(t1, t2)
        t_old = self.ts.getTransaction("Once")
        self.assertEqual(len(t_old), 0)
        t_new = self.ts.getTransaction("Once replaced")
        self.assertEqual(len(t_new), 1)


# DELETE
class TestBasicDelete(unittest.TestCase):
    def setUp(self):
        self.ts = TransactionStore()

        t1 = transaction.Transaction(
            start=date.today(),
            description="Once",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start=date.today()+timedelta(days=2),
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        t3 = transaction.Transaction(
            start=date.today(),
            end=date.today()+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip=set([date.today()+timedelta(days=7)]),
            scheduled=True,
            cleared=True)

        self.ts.addTransactions(t1, t2, t3)

    def test_remove_existing_single_transaction(self):
        self.assertEqual(len(self.ts.store), 3)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 1)
        t1 = t_list[0]
        self.ts.removeTransactions(t1)
        self.assertEqual(len(self.ts.store), 2)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 0)

    def test_remove_existing_multiple_transactions(self):
        self.assertEqual(len(self.ts.store), 3)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 1)
        t1 = t_list[0]
        t_list = self.ts.getTransaction("Weekly")
        self.assertEqual(len(t_list), 1)
        t2 = t_list[0]
        self.ts.removeTransactions(t1, t2)
        self.assertEqual(len(self.ts.store), 1)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 0)
        t_list = self.ts.getTransaction("Weekly")
        self.assertEqual(len(t_list), 0)

    def test_remove_non_existent_single_transaction(self):
        t_missing = transaction.Transaction(
                start=date.today(),
                description="Missing",
                amount=1.00,
                frequency=transaction.Transaction.ONCE)
        self.assertEqual(len(self.ts.store), 3)
        self.ts.removeTransactions(t_missing)
        self.assertEqual(len(self.ts.store), 3)

    def test_remove_multiple_transactions_with_some_missing(self):
        t_missing = transaction.Transaction(
                start=date.today(),
                description="Missing",
                amount=1.00,
                frequency=transaction.Transaction.ONCE)

        self.assertEqual(len(self.ts.store), 3)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 1)
        t1 = t_list[0]
        t_list = self.ts.getTransaction("Weekly")
        self.assertEqual(len(t_list), 1)
        t2 = t_list[0]
        self.ts.removeTransactions(t1, t2, t_missing)
        self.assertEqual(len(self.ts.store), 1)
        t_list = self.ts.getTransaction("Once")
        self.assertEqual(len(t_list), 0)
        t_list = self.ts.getTransaction("Weekly")
        self.assertEqual(len(t_list), 0)


# MISC
class TestConstructor(unittest.TestCase):
    def test_constructor(self):
        ts = TransactionStore()
        self.assertIsInstance(ts.store, list)


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.file = f'./test-{time.time()}'

        t1 = transaction.Transaction(
            start=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        t2 = transaction.Transaction(
            start=date.today(),
            original_start=date.today()-timedelta(days=1),
            end=date.today()+timedelta(days=56),
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip=set([date.today()+timedelta(days=7)]),
            scheduled=True,
            cleared=True)

        self.ts = TransactionStore()
        self.ts.store.append(t1)
        self.ts.store.append(t2)

    def tearDown(self):
        os.remove(self.file)

    def assertTransactionsEqual(self, t1, t2):
        self.assertEqual(t1.start, t2.start)
        self.assertEqual(t1.original_start, t2.original_start)
        self.assertEqual(t1.end, t2.end)
        self.assertEqual(t1.description, t2.description)
        self.assertEqual(t1.amount, t2.amount)
        self.assertEqual(t1.frequency, t2.frequency)
        self.assertEqual(t1.skip.symmetric_difference(t2.skip), set())
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

        origsd1 = date.today()
        origsd2 = date.today()+timedelta(days=2)
        self.t1 = transaction.Transaction(
            start=origsd1,
            description="Once, today",
            amount=1.00,
            frequency=transaction.Transaction.ONCE)
        self.t2 = transaction.Transaction(
            start=origsd2,
            description="Once, in two days",
            amount=1.01,
            frequency=transaction.Transaction.ONCE)
        self.t3 = transaction.Transaction(
            start=origsd1,
            description="Weekly",
            amount=1.02,
            frequency=transaction.Transaction.WEEKLY,
            skip=set([date.today()+timedelta(days=7)]),
            scheduled=True,
            cleared=True)
        self.t4 = transaction.Transaction(
            start=origsd2,
            description="Monthly",
            amount=1.03,
            frequency=transaction.Transaction.MONTHLY)

        self.ts.addTransactions(self.t1, self.t2, self.t3, self.t4)

    def test_update_all_recurring_start_dates(self):
        origsd1 = date.today()
        origsd2 = date.today()+timedelta(days=2)
        new_sd = date.today() + timedelta(days=10)
        new_weekly_sd = origsd1 + timedelta(days=14)
        new_monthly_sd = origsd2 + relativedelta(months=1)

        self.ts.updateRecurringStartDates(new_sd)

        self.assertEqual(self.t1.start, origsd1)
        self.assertEqual(self.t1.original_start, origsd1)
        self.assertEqual(self.t2.start, origsd2)
        self.assertEqual(self.t2.original_start, origsd2)
        self.assertEqual(self.t3.start, new_weekly_sd)
        self.assertEqual(self.t3.original_start, origsd1)
        self.assertEqual(self.t4.start, new_monthly_sd)
        self.assertEqual(self.t4.original_start, origsd2)

    def test_purge_outdated_single_transactions(self):
        purge_date = date.today() + timedelta(days=1)

        self.assertEqual(len(self.ts.store), 4)
        self.ts.purgeSingleBefore(purge_date)
        self.assertEqual(len(self.ts.store), 3)
        exp_set = set([self.t2, self.t3, self.t4])
        act_set = set(self.ts.store)
        self.assertEqual(exp_set.symmetric_difference(act_set), set())
        t_list = self.ts.getTransaction("Once, in two days")
        self.assertEqual(len(t_list), 1)


if __name__ == '__main__':
    unittest.main()
