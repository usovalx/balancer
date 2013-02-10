from PyQt4 import QtCore, QtGui

from balancer import schema, db
from balancer.window_ui import Ui_MainWindow

class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = db.Db('t.db')

        self.ui.transactionsList.current = None
        self.show_accounts()

    def show_accounts(self):
        items = []
        for a in self.db.query(schema.Account).order_by(schema.Account.name):
            i = QtGui.QTreeWidgetItem([a.nick, a.number, a.name])
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
                i = QtGui.QTreeWidgetItem([str(t.amount), str(t.payee), str(t.date), str(t.category_id)])
                i.db_item = t
            else:
                i = QtGui.QTreeWidgetItem(['Balance', str(t.balance), str(t.date)])
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
        self.show_transactions(current.db_item.id)

if __name__ == '__main__':
    import sys
    sys.path.append('..')

    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())
