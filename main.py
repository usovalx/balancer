from PyQt4 import QtCore, QtGui

from balancer import schema, db
from balancer.window_ui import Ui_MainWindow

class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = db.Db('t.db')

        self.show_accounts()

    def show_accounts(self):
        accounts = self.db.query(schema.Account).order_by(schema.Account.name)
        items = [QtGui.QTreeWidgetItem([a.nick, a.number, a.name]) for a in accounts]
        self.ui.accountsList.clear()
        self.ui.accountsList.addTopLevelItems(items)

if __name__ == '__main__':
    import sys
    sys.path.append('..')

    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())
