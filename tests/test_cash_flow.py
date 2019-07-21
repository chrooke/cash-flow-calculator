#!/bin/env python
import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import context
from cash_flow.transaction import Transaction
from cash_flow.transaction_store import TransactionStore
from cash_flow.cash_flow import CashFlow


class TestConstructor(unittest.TestCase):
    def test_contructor_float_balance(self):
        sd = date.today()
        sb = 100.00
        ts = TransactionStore()
        cf = CashFlow(sd, sb, ts)
        self.assertIsInstance(cf.start_date, date)
        self.assertEqual(cf.start_date, sd)
        self.assertIsInstance(cf.start_balance, float)
        self.assertEqual(cf.start_balance, sb)
        self.assertIsInstance(cf.transaction_store, TransactionStore)
        self.assertEqual(len(cf.transaction_store.getTransactions()), 0)
        self.assertIsInstance(cf.current_date, date)
        self.assertEqual(cf.current_date, sd)
        self.assertIsInstance(cf.current_balance, float)
        self.assertEqual(cf.current_balance, sb)

    def test_contructor_string_balance(self):
        sd = date.today()
        sb = '100.00'
        ts = TransactionStore()
        cf = CashFlow(sd, sb, ts)
        self.assertIsInstance(cf.start_date, date)
        self.assertEqual(cf.start_date, sd)
        self.assertIsInstance(cf.start_balance, float)
        self.assertEqual(cf.start_balance, float(sb))
        self.assertIsInstance(cf.transaction_store, TransactionStore)
        self.assertEqual(len(cf.transaction_store.getTransactions()), 0)
        self.assertIsInstance(cf.current_date, date)
        self.assertEqual(cf.current_date, sd)
        self.assertIsInstance(cf.current_balance, float)
        self.assertEqual(cf.current_balance, float(sb))


class TestGenerator(unittest.TestCase):
    def setUp(self):
        sd = date.today()
        sb = 100.00
        ts = TransactionStore()
        self.cf = CashFlow(sd, sb, ts)

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

    def test_generate_from_nonrecurring_today(self):
        st = Transaction(
            start=date.today(),
            description="Once, today",
            amount=1.00,
            frequency=Transaction.ONCE)
        self.cf.transaction_store.addTransactions(st)
        day = self.cf.getTodaysTransactions()
        (d, bal, t_list) = next(day)
        self.assertEqual(d, self.cf.start_date)
        self.assertEqual(d, self.cf.current_date)
        self.assertEqual(bal, self.cf.current_balance)
        self.assertEqual(len(t_list), 1)
        t = t_list[0]
        self.assertTransactionsEqual(t, st)
        self.assertEqual(bal, self.cf.start_balance + st.amount)
        for i in range(1, 100):
            (d, bal, t_list) = next(day)
            self.assertEqual(d, self.cf.current_date)
            self.assertEqual(d, self.cf.start_date + timedelta(days=i))
            self.assertEqual(bal, self.cf.current_balance)
            self.assertEqual(len(t_list), 0)
            self.assertEqual(bal, self.cf.start_balance + st.amount)


if __name__ == '__main__':
    unittest.main()
