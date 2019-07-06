#!/bin/env python
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import transaction


class TransactionStore(object):
    def __init__(self):
        self.store = []

    def add(self, start=date.today(), end=None, description="",
            amt=0.00, frequency=None, skip=None,
            scheduled=False, cleared=False):
        self.store.append(transaction.Transaction(start, end, description,
                          amt, frequency, skip,
                          scheduled, cleared))
