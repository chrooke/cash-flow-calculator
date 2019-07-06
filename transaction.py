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

    def __init__(self,
                 start_date=date.today(),
                 original_start_date=None,
                 end_date=None,
                 description="",
                 amount=0.00,
                 frequency=None,
                 skip_list=None,
                 scheduled=False,
                 cleared=False):
        self.start_date = start_date
        if original_start_date is None:
            original_start_date = self.start_date
        self.original_start_date = original_start_date
        self.end_date = end_date
        self.description = description
        self.amount = amount
        if frequency is None:
            frequency = Transaction.ONCE
        self.frequency = frequency
        if skip_list is None:
            skip_list = []
        self.skip_list = skip_list
        self.scheduled = scheduled
        self.cleared = cleared

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

    def amtOn(self, trans_date):
        date = self.start_date
        while(True):
            if date not in self.skip_list:
                if date == trans_date:
                    return self.amount
                if date > trans_date:
                    return 0
                if self.end_date and trans_date > self.end_date:
                    return 0
                if self.frequency == Transaction.ONCE:
                    return 0
            date = self._step_to_next_date(date)

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
