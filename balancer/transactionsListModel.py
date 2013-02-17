from PyQt4 import QtCore, QtGui
from . import schema

class TransactionsListModel(QtGui.QStandardItemModel):
    def __init__(self, db):
        super(TransactionsListModel, self).__init__()

        self.db = db
        self.__enabled_accounts = set()
        self.__payee_filter = None
        self.__txn_ids = []

    # Event handlers for filters
    def on_accountsChanged(self, accounts):
        print "accts: %s" % accounts
        self.__enabled_accounts = set(accounts)
        self.updateTransactionsList()

    def on_payeeChanged(self, payeeStr):
        self.__payee_filter = '%{}%'.format(unicode(payeeStr)) if payeeStr else None
        self.updateTransactionsList()

    def applyFilters(self, query):
        if self.__enabled_accounts:
            query = query.filter(schema.Transaction.account_id.in_(self.__enabled_accounts))
        else:
            query = query.filter(schema.Transaction.account_id == -1)

        if self.__payee_filter:
            query = query.filter(schema.Transaction.payee.like(self.__payee_filter))

        return query

    def updateTransactionsList(self):
        q = self.db.query(schema.Transaction.id)
        q = self.applyFilters(q)
        q = q.order_by(schema.Transaction.date.desc(), schema.Transaction.payee)
        self.__txn_ids = q.all()
        print "total: %d " % len(self.__txn_ids)
        self.clear()

    def canFetchMore(self, index):
        if index.isValid():
            return False
        return self.rowCount() < len(self.__txn_ids)

    def fetchMore(self, index):
        c1 = self.rowCount()
        print "loading: %d" % c1
        for tid in self.__txn_ids[c1:c1+100]:
            self.appendRow(self.formatRow(self.db.get(schema.Transaction, tid)))

    def formatRow(self, txn):
        r = [QtGui.QStandardItem(unicode(x))
                for x in [txn.date, txn.payee, txn.amount, txn.account_id]]
        return r

