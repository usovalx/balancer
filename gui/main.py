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

        self.ui.editor.hide()

        self.db = todo.initDB()
        # FIXME: dirty
        self.ui.editor.db = self.db

        for task in self.db.query(todo.Task).order_by(todo.Task.id):
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
        if checked is None: return
        i = self.ui.list.currentItem()
        
        if not i:
            return

        self.db.delete(i.task)
        self.ui.list.takeTopLevelItem(self.ui.list.indexOfTopLevelItem(i))
        self.db.commit()

    def on_list_currentItemChanged(self, current=None, prev=None):
        self.ui.actionDelete_task.setEnabled(bool(current))

    def on_actionNew_Task_triggered(self, checked=None):
        if checked is None: return

        task = todo.Task(text = "New task")

        item = QtGui.QTreeWidgetItem([task.text, str(task.date), ''])
        item.setCheckState(0, False)
        item.task = task

        self.ui.list.addTopLevelItem(item)
        self.ui.list.setCurrentItem(item)

        self.db.add(task)
        self.ui.editor.edit(item)

    def on_actionEdit_Task_triggered(self, checked = None):
        if checked is None: return

        item = self.ui.list.currentItem()
        if item:
            self.ui.editor.edit(item)


def main():
    app = QtGui.QApplication(sys.argv)
    win = Main()
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
