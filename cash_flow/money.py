#!/bin/env python

from decimal import Decimal


class Money():
    def __init__(self, value=None):
        if not value:
            value = 0.0
        if type(value) is Money:
            value = value.value
        else:
            value = float(value)
        self.value = Decimal(value).quantize(Decimal('1.00'))

    def __repr__(self):
        return '{}'.format(self.value)

    def __str__(self):
        return '{}'.format(self.value)

    def __add__(self, other):
        if type(other) is not Money:
            other = Money(other)
        value = self.value + other.value
        return Money(value)

    def __sub__(self, other):
        if type(other) is not Money:
            other = Money(other)
        value = self.value - other.value
        return Money(value)

    def __eq__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value == other.value

    def __ne__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value != other.value

    def __lt__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value < other.value

    def __le__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value <= other.value

    def __gt__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value > other.value

    def __ge__(self, other):
        if type(other) is not Money:
            other = Money(other)
        return self.value >= other.value
