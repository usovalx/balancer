#!/usr/bin/python2
from PyQt4 import QtCore, QtGui
from balancer import schema, db
from balancer.transactionsListModel import TransactionsListModel
from balancer.window_ui import Ui_MainWindow

class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = db.Db('t.db')

        self.ui.filters.setDb(self.db)

        self.model = TransactionsListModel(self.db, self.ui.filters)
        self.ui.transactionsList.setModel(self.model)

        # connect events
        self.ui.filters.filtersChanged.connect(self.model.on_filtersChanged)

        # load data
        self.model.updateTransactionsList()


if __name__ == '__main__':
    import sys
    sys.path.append('..')

    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())
