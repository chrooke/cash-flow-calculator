#!/bin/env python

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from cash_flow.transaction import Transaction
from cash_flow.transaction_store import TransactionStore


class CashFlow(object):
    def __init__(self, start_date, start_balance, transaction_store):
        self.start_date = start_date
        self.start_balance = start_balance
        self.transaction_store = transaction_store
        self.current_date = start_date
        self.current_balance = start_balance

    def getTodaysTransactions(self):
        while(True):
            daily_transactions = []
            for trans in self.transaction_store.store:
                amt = trans.amtOn(self.current_date)
                if amt != 0:
                    daily_transactions.append(trans)
                    self.current_balance += amt
            yield (self.current_date, self.current_balance, daily_transactions)
            self.current_date += timedelta(days=1)
