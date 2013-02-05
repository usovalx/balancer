import datetime
from decimal import Decimal

_scale = 1000

class Transaction(object):
    def __init__(self, amount, date, payee):
        # minimal set of attributes
        self.id = None
        self.amount = Decimal(amount)
        self.date = date
        assert(type(self.date) is datetime.datetime)
        self.payee = payee
        self.import_id = None

        # classification
        self.category = None
        # user comment
        self.comment = None

        # misc supplementary info
        self.bank_memo = None
        self.bank_id = None
        self.trn_type = None

    def __str__(self):
        return '{:8} @ {} to: {}'.format(self.amount, self.date, self.payee)

    def __repr__(self):
        return '<Transaction: {0}>'.format(self)

class Balance(object):
    def __init__(self, balance, date):
        self.id = None
        self.balance = Decimal(balance)
        self.date = date
        assert(type(self.date) is datetime.datetime)
        self.import_id = None

    def __str__(self):
        return '{:8} @ {}'.format(self.balance, self.date)

    def __repr__(self):
        return '<Balance: {0}>'.format(self)

class Account(object):
    def __init__(self, number, nick = None, name = None, comments = None):
        self.id = None
        self.number = str(number)
        self.nick = nick
        self.name = name
        self.comments = comments

    @classmethod
    def fromdb(cls, row):
        i = cls.__new__(cls)
        i.__dict__ = dict(row)
        return i

    def __str__(self):
        if self.nick:
            return '{} ({})'.format(self.number, self.nick)
        else:
            return str(self.number)

    def __repr__(self):
        return '<Account: {0}>'.format(self)

class ImportInfo(object):
    def __init__(self, date, description, raw_data_name, raw_data):
        self.id = None
        self.date = date
        assert(type(self.date) is datetime.datetime)
        self.description = description
        self.raw_data_name = raw_data_name
        self.raw_data = raw_data

    def __str__(self):
        return '{}: {}'.format(self.date, self.description)

    def __repr__(self):
        return '<ImportInfo: {}>'.format(self)
