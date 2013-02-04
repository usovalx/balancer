import datetime
from decimal import Decimal

class Transaction:
    def __init__(self, amount, date, payee):
        # minimal set of attributes
        self.tid = None
        self.amount = Decimal(amount)
        self.date = date
        assert(type(self.date) is datetime.datetime)
        self.payee = payee

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
        self.balance = Decimal(balance)
        self.date = date
        assert(type(self.date) is datetime.datetime)

    def __str__(self):
        return "{:8} @ {}".format(self.balance, self.date)

    def __repr__(self):
        return "<Balance: {0}>".format(self)

class Account:
    def __init__(self, number):
        self.number = str(number)

        # various misc info about account
        self.bank = None
        self.name = None
        self.nick = None
        self.iban = None
        self.bic  = None

    def __str__(self):
        return self.number

    def __repr__(self):
        return "<Account: {0}>".format(self)
