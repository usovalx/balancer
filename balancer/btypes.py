import datetime
from decimal import Decimal

class Transaction:
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
        return "{:8} @ {} to: {}".format(self.amount, self.date, self.payee)

    def __repr__(self):
        return "<Transaction: {0}>".format(self)

class Balance:
    def __init__(self, balance, date):
        self.id = None
        self.balance = Decimal(balance)
        self.date = date
        assert(type(self.date) is datetime.datetime)
        self.import_id = None

    def __str__(self):
        return "{:8} @ {}".format(self.balance, self.date)

    def __repr__(self):
        return "<Balance: {0}>".format(self)

class Account:
    def __init__(self, number, name = None, nick = None, description = None):
        self.id = None
        self.number = str(number)

        # various misc info about account
        self.name = name
        self.nick = nick
        self.description = description

    def __str__(self):
        return self.number

    def __repr__(self):
        return "<Account: {0}>".format(self)

class ImportInfo:
    def __init__(self, date, description, raw_data_name, raw_data):
        self.id = None
        self.date = date
        self.description = description
        self.raw_data_name = raw_data_name
        self.raw_data = raw_data

