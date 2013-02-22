from PyQt4 import QtCore, QtGui
from . import schema

class TransactionsListModel(QtGui.QStandardItemModel):
    def __init__(self, db, filters):
        super(TransactionsListModel, self).__init__()
        self.db = db
        self.__txn_ids = []
        self.__filter = filters.getFilter(schema.Transaction)

    def on_filtersChanged(self):
        print "filtersChanged"
        self.updateTransactionsList()

    def updateTransactionsList(self):
        q = self.db.query(schema.Transaction.id)
        q = self.__filter(q)
        q = q.order_by(schema.Transaction.date.desc(), schema.Transaction.payee)
        self.__txn_ids = q.all()
        print "total txns: %d " % len(self.__txn_ids)
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
                for x in [txn.date, txn.payee, txn.amount, txn.account.nick]]
        return r

