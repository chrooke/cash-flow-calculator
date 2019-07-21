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
    INTERVALS = [ONCE, WEEKLY, BIWEEKLY, MONTHLY, QUARTERLY, ANNUALLY]

    def __init__(self,
                 start=date.today(),
                 original_start=None,
                 end=None,
                 description="<Description>",
                 amount=0.00,
                 frequency=None,
                 skip=None,
                 scheduled=False,
                 cleared=False):
        self.start = start
        if original_start is None:
            original_start = self.start
        self.original_start = original_start
        self.end = end
        self.description = description
        self.amount = amount
        if frequency is None:
            frequency = Transaction.ONCE
        self.frequency = frequency
        if skip is None:
            skip = set()
        self.skip = skip
        self.scheduled = scheduled
        self.cleared = cleared

    def amtOn(self, trans_date):
        date = self.start
        while(True):
            if date not in self.skip:
                if date == trans_date:
                    return float(self.amount)
                if date > trans_date:
                    return 0.0
                if self.end and trans_date > self.end:
                    return 0.0
                if self.frequency == Transaction.ONCE:
                    return 0.0
            date = self._step_to_next_date(date)

    def updateStartDate(self, base_date):
        if (self.frequency == Transaction.ONCE):
            date = base_date
        else:
            date = self.start
            while date < base_date:
                date = self._step_to_next_date(date)
        self.start = date

    def duplicate(self):
        return Transaction(
            start=self.start,
            original_start=self.original_start,
            end=self.end,
            description=self.description,
            amount=self.amount,
            frequency=self.frequency,
            skip=self.skip,
            scheduled=self.scheduled,
            cleared=self.cleared)

    def _step_to_next_date(self, date):
        skip_func = {
            Transaction.WEEKLY: self._add_week,
            Transaction.BIWEEKLY: self._add_two_weeks,
            Transaction.MONTHLY: self._add_month,
            Transaction.QUARTERLY: self._add_quarter,
            Transaction.ANNUALLY: self._add_year
        }.get(self.frequency, None)

        if skip_func is not None:
            return skip_func(date)

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
