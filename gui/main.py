import os, sys
from PyQt4 import QtCore, QtGui

from windowUi import Ui_MainWindow
import todo

class Main(QtGui.QMainWindow):
    def __init__(self):
        ##QtGui.QMainWindow.__init__(self)
        super(Main, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = todo.initDB()

        for task in self.db.query(todo.Task):
            tags = ', '.join([t.name for t in task.tags])
            
            item = QtGui.QTreeWidgetItem([task.text, str(task.date), tags])
            item.setCheckState(0, QtCore.Qt.Checked if task.done else QtCore.Qt.Unchecked)
            item.task = task

            self.ui.list.addTopLevelItem(item)

    # autoconnected to self.list.itemChanged
    def on_list_itemChanged(self, item, column):
        item.task.done = bool(item.checkState(0))
        self.db.commit()

    def on_actionDelete_task_triggered(self, checked=None):
        if checked is not None:
            i = self.ui.list.currentItem()
            
            if not i:
                return

            self.db.delete(i.task)
            self.ui.list.takeTopLevelItem(self.ui.list.indexOfTopLevelItem(i))
            self.db.commit()

    def on_list_currentItemChanged(self, current=None, prev=None):
        print '=== changed: ' + str(current)
        self.ui.actionDelete_task.setEnabled(bool(current))


def main():
    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
