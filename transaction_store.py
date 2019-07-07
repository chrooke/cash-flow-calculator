#!/bin/env python
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction


class TransactionStore(object):
    def __init__(self):
        self.store = []

    def addTransactions(self, first_transaction, *remaining_transactions):
        self.store.append(first_transaction)
        self.store = self.store + list(remaining_transactions)

    def replaceTransaction(self, old, new):
        self.removeTransactions(old)
        self.addTransactions(new)

    def removeTransactions(self, first_transaction, *remaining_transactions):
        try:
            self.store.remove(first_transaction)
            for t in remaining_transactions:
                self.store.remove(t)
        except ValueError:
            pass

    def saveTransactions(self, file):
        with open(file, "w") as f:
            yaml.dump(self.store, f)

    def loadTransactions(self, file):
        with open(file, "r") as f:
            self.store = yaml.full_load(f)

    def getTransaction(self, description, requested_date=None):
        # Currently does not handle recurring/overridden transactions
        if requested_date is None:
            transactions = [t for t in self.store
                            if t.description == description]
        else:
            transactions = [t for t in self.store
                            if t.description == description and
                            t.amtOn(requested_date) != 0]
        return transactions

    def updateRecurringStartDates(self, new_date):
        recurring_trans = [x for x in self.store
                           if x.frequency != transaction.Transaction.ONCE]
        for t in recurring_trans:
            t.updateStartDate(new_date)

    def purgeSingleBefore(self, purge_date):
        single_trans = [x for x in self.store
                        if x.frequency == transaction.Transaction.ONCE]
        for t in single_trans:
            if t.start < purge_date:
                self.removeTransactions(t)
