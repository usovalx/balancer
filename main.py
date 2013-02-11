#!/usr/bin/python2
from PyQt4 import QtCore, QtGui

from balancer import schema, db
from balancer.window_ui import Ui_MainWindow

class TransactionsViewModel(QtCore.QAbstractTableModel):
    def __init__(self, db):
        super(TransactionsViewModel, self).__init__()

        self.acc = None
        self.db = db
        self.cols = ['trn_type', 'amount', 'payee', 'date', 'category_id']
        self.tids = []
        self.trns = {}

    def load_data(self, acc):
        if self.acc == acc:
            return

        self.acc = acc
        tn = schema.Transaction
        self.tids = self.db.query(tn.id).filter_by(account_id = acc)\
                .order_by(tn.date.desc(), tn.payee, tn.amount).all()
        self.trns = {}
        self.modelReset.emit()

    def rowCount(self, parent):
        return len(self.tids) if not parent.isValid() else 0

    def columnCount(self, parent):
        return len(self.cols) if not parent.isValid() else 0

    def data(self, idx, role):
        if not idx.isValid() or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if not self.trns.has_key(idx.row()):
            self.trns[idx.row()] = self.db.query(schema.Transaction).get(self.tids[idx.row()])
        t = self.trns[idx.row()]
        return QtCore.QVariant(unicode(getattr(t, self.cols[idx.column()])))

    def headerData(self, sect, orient, role):
        if orient != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.cols[sect])

class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = db.Db('t.db')

        self.model = TransactionsViewModel(self.db)
        self.ui.transactionsList.setModel(self.model)
        #self.ui.transactionsList.current = None
        self.show_accounts()

    def show_accounts(self):
        items = []
        for a in self.db.query(schema.Account).order_by(schema.Account.name):
            i = QtGui.QTreeWidgetItem(map(str, [a.nick, a.number, a.name]))
            i.db_item = a
            items.append(i)

        self.ui.accountsList.clear()
        self.ui.accountsList.addTopLevelItems(items)

    def show_transactions(self, acc):
        if acc == self.ui.transactionsList.current:
            return
        self.ui.transactionsList.current = acc
        items = []
        for t in self.get_data(acc):
            if hasattr(t, 'amount'):
                i = QtGui.QTreeWidgetItem(
                        map(unicode, [t.amount, t.payee, t.date, t.category_id]))
                i.db_item = t
            else:
                i = QtGui.QTreeWidgetItem(
                        map(unicode, ['Balance', t.balance, t.date]))
            items.append(i)

        self.ui.transactionsList.clear()
        self.ui.transactionsList.addTopLevelItems(items)

    def get_data(self, acc):
        tn = schema.Transaction
        bn = schema.Balance
        tns = self.db.query(tn).filter_by(account_id = acc)\
                .order_by(tn.date.desc(), tn.payee, tn.amount).all()
        bns = self.db.query(bn).filter_by(account_id = acc)\
                .order_by(bn.date.desc()).all()
        while len(tns) != 0 or len(bns) != 0:
            if len(tns) == 0:
                yield bns.pop(0)
            elif len(bns) == 0:
                yield tns.pop(0)
            elif bns[0].date >= tns[0].date:
                yield bns.pop(0)
            else:
                yield tns.pop(0)

    def on_accountsList_currentItemChanged(self, current=None, prev=None):
        if current is None:
            return
        #self.show_transactions(current.db_item.id)
        self.model.load_data(current.db_item.id)

if __name__ == '__main__':
    import sys
    sys.path.append('..')

    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())
