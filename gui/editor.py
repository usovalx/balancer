from PyQt4 import QtCore, QtGui
from editorUi import Ui_Form
import todo
import datetime

class editor(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

    def edit(self, item):
        self.item = item
        self.ui.task.setText(item.task.text)
        self.ui.finished.setChecked(bool(item.task.done))
        dt = item.task.date
        if dt:
            self.ui.dueDate.setDate(QtCore.QDate(dt.year, dt.month, dt.day))
            self.ui.dueDate.setTime(QtCore.QTime(dt.hour, dt.minute))
        else:
            self.ui.dueDate.setDateTime(QtCore.QDateTime())
        #self.ui.tags.setText(','.join(t.name for t in item.task.tags))
        self.show()

    def save(self):
        if self.item is None: return

        d = self.ui.dueDate.date()
        t = self.ui.dueDate.time()
        self.item.task.date = datetime.datetime(
                d.year(), d.month(), d.day(), t.hour(), t.minute())
        self.item.task.text=unicode(self.ui.task.text())

        tags = [s.strip() for s in unicode(self.ui.tags.text()).split(',')]
        t = []
        for tag in tags:
            dt = self.db.query(todo.Tag).filter_by(name = tag).first()
            if dt:
                t.append(dt)
            else:
                dt = todo.Tag(name=tag)
                self.db.add(dt)
                t.append(dt)
        self.item.task.tags = t

        self.item.setText(0, self.item.task.text)
        self.item.setText(1, str(self.item.task.date))
        self.item.setText(2, ','.join(t.name for t in self.item.task.tags))
        self.db.commit()
