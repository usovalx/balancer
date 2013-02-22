from PyQt4 import QtCore, QtGui
from . import schema
from . import util
from .filter_ui import Ui_filters

class FiltersWidget(QtGui.QWidget):
    # my signals
    filtersChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(FiltersWidget, self).__init__(parent)

        self.__selectedAccounts = dict()
        self.__payeeFilter = None

        self.ui = Ui_filters()
        self.ui.setupUi(self)

        self.ui.dateTo.setDate(QtCore.QDate.currentDate())
        self.ui.dateFrom.setDate(QtCore.QDate.currentDate().addMonths(-3))

        # connect event handlers
        self.ui.accounts.itemChanged.connect(self.accountsSelection)

        @self.ui.selectAll.clicked.connect
        def handle():
            with util.block_signals(self.ui.accounts):
                for i in range(self.ui.accounts.count()):
                    self.ui.accounts.item(i).setCheckState(QtCore.Qt.Checked)
            self.accountsSelection()

        @self.ui.selectNone.clicked.connect
        def handle():
            with util.block_signals(self.ui.accounts):
                for i in range(self.ui.accounts.count()):
                    self.ui.accounts.item(i).setCheckState(QtCore.Qt.Unchecked)
            self.accountsSelection()

        @self.ui.payeeFilter.editingFinished.connect
        def handle():
            x = unicode(self.ui.payeeFilter.text())
            x = x if x else None
            if self.__payeeFilter != x:
                self.__payeeFilter = x
                self.filtersChanged.emit()

    def getFilter(self, obj):
        def f(query):
            if self.__selectedAccounts:
                query = query.filter(obj.account_id.in_(self.__selectedAccounts))
            else:
                query = query.filter(obj.account_id == -1)
            if self.__payeeFilter:
                query = query.filter(obj.payee.like(self.__payeeFilter))
            return query
        return f

    def setDb(self, db):
        self.db = db
        self.updateAccountList()

    def sizeHint(self):
        return self.minimumSizeHint() + QtCore.QSize(10, 0)

    def updateAccountList(self):
        # FIXME: remember previously selected accounts and restore selection
        # FIXME: suppress signals while refilling
        self.ui.accounts.clear()
        for a in self.db.query(schema.Account).order_by(schema.Account.nick):
            itm = QtGui.QListWidgetItem(a.nick)
            itm.setCheckState(QtCore.Qt.Checked)
            itm.accnt = a
            self.ui.accounts.addItem(itm)
        self.accountsSelection()

    def accountsSelection(self):
        selected = set()
        for i in range(self.ui.accounts.count()):
            itm = self.ui.accounts.item(i)
            if itm.checkState() == QtCore.Qt.Checked:
                selected.add(itm.accnt.id)
        if selected != self.__selectedAccounts:
            self.__selectedAccounts = selected
            self.filtersChanged.emit()

