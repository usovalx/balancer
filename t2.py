#!/usr/bin/python2
from PyQt4 import QtCore, QtGui

from balancer import schema, db
from balancer.window_ui import Ui_MainWindow

import random

class MyModel(QtGui.QStandardItemModel):
    def __init__(self, parent = None):
        super(MyModel, self).__init__(parent)

        self.m = 10
        for i in xrange(0, self.m):
            self.appendRow([
                QtGui.QStandardItem(str(i)),
                QtGui.QStandardItem(str(random.randint(1,1000)))])

        self.modelReset.connect(self.logreset)

    def logreset(self):
        print "== reset happened"

    def canFetchMore(self, idx):
        if not idx.isValid():  ## only root level can fetch more
            return True
        return False

    def fetchMore(self, idx):
        if not idx.isValid():
            print "fetching %s -> + X" % self.m
            chunk = 100
            #no need to begin/end insert rows -- QStandardItemModel will do it itself
            for i in xrange(self.m, self.m + chunk):
                self.appendRow([
                    QtGui.QStandardItem(str(i)),
                    QtGui.QStandardItem(str(random.randint(1,1000)))])
            self.m += chunk

    def sort(self, col, order):
        print "sorting"
        super(MyModel, self).sort(col, order)

    def doreset(self):
        print "reset, m  %s -> 0" % self.m
        self.m = 0
        self.clear()

class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.mymodel = MyModel()
        self.sortModel = QtGui.QSortFilterProxyModel()
        self.sortModel.setDynamicSortFilter(True)
        self.sortModel.setSourceModel(self.mymodel)
        self.ui.transactionsList.setModel(self.sortModel)
        self.ui.transactionsList.setSortingEnabled(True)

    def on_payeeFilter_editingFinished(self):
        self.mymodel.doreset()





if __name__ == '__main__':
    import sys
    sys.path.append('..')

    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())
