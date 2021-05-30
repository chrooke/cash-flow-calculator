#!/bin/env python
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from cash_flow.transaction import Transaction


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
        try:
            with open(file, "w") as f:
                yaml.dump(self.store, f)
        except:
            print(f"Failed to save transactions to {file}.")

    def loadTransactions(self, file):
        try:
            with open(file, "r") as f:
                self.store = yaml.load(f, Loader=yaml.Loader)
        except:
            print(f"Failed to load transaction store from {file}.")

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

    def getTransactions(self, frequency=None):
        # TODO: will need to change this when overrides are added
        # Overrides should not be returned with ONCE
        if frequency is None:
            return self.store
        else:
            return [t for t in self.store if t.frequency == frequency]

    def updateRecurringStartDates(self, new_date):
        recurring_trans = [x for x in self.store
                           if x.frequency != Transaction.ONCE]
        for t in recurring_trans:
            t.updateStartDate(new_date)

    def purgeSingleBefore(self, purge_date):
        single_trans = [x for x in self.store
                        if x.frequency == Transaction.ONCE]
        for t in single_trans:
            if t.start < purge_date:
                self.removeTransactions(t)
