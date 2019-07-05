#!/bin/env python

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class Transaction(object):
    ONCE = "O"
    WEEKLY = "W"
    BIWEEKLY = "2W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    ANNUALLY = "A"

    def __init__(self, start=date.today(), end=None, description="",
                 amt=0.00, frequency=None, skip=None):
        self.start_date = start
        self.end_date = end
        self.description = description
        self.amount = amt
        if frequency is None:
            frequency = Transaction.ONCE
        self.frequency = frequency
        self.skip_list = skip
        self.step_to_next_date = {
            Transaction.WEEKLY: self._add_week,
            Transaction.BIWEEKLY: self._add_two_weeks,
            Transaction.MONTHLY: self._add_month,
            Transaction.QUARTERLY: self._add_quarter,
            Transaction.ANNUALLY: self._add_year
        }.get(self.frequency, None)

    def amtOn(self, trans_date):
        date = self.start_date
        while(True):
            if date == trans_date:
                return self.amount
            if date > trans_date:
                return 0
            if self.end_date and trans_date > self.end_date:
                return 0
            if self.frequency == Transaction.ONCE:
                return 0
            date = self.step_to_next_date(date)

    def _add_week(self, d):
        return d+timedelta(days=7)

    def _add_two_weeks(self, d):
        return d+timedelta(days=14)

    def _add_month(self, d):
        return d+relativedelta(months=1)

    def _add_quarter(self, d):
        return d+relativedelta(months=3)

    def _add_year(self, d):
        return d+relativedelta(years=1)
