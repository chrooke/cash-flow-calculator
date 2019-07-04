#!/bin/env python

from datetime import date, timedelta


class Transaction(object):

    def __init__(self, start=date.today(), end=None, description="",
                 amt=0.00, frequency="O", skip=[]):
        self.start_date = start
        self.stop_date = end
        self.description = description
        self.amount = amt
        self.frequency = frequency
        self.skip_list = skip
        self.step_to_next_date = {
            "W": self._add_week,
            "2W": self._add_two_weeks,
            "M": self._add_month,
            "Q": self._add_quarter,
            "A": self._add_year
        }.get(self.frequency, None)

    def amtOn(self, transaction_date):
        date = self.start_date
        while(True):
            if date == transaction_date:
                return self.amount
            if (date > transaction_date) or (self.frequency == "O"):
                return 0
            date = self.step_to_next_date()

    def _add_week(self, d):
        return d+timedelta(days=7)

    def _add_two_weeks(self, d):
        return d+timedelta(days=14)

    def _add_month(self, d):
        return d.replace(month=d.month+1)

    def _add_quarter(self, d):
        return d.replace(month=d.month+3)

    def _add_year(self, d):
        return d.replace(year=d.year+1)
