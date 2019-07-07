#!/bin/env python
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction


class TransactionStore(object):
    def __init__(self):
        self.store = []

    def add(self, first_transaction, *remaining_transactions):
        self.store.append(first_transaction)
        self.store = self.store + list(remaining_transactions)

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
                            t.start == requested_date]
        return transactions
