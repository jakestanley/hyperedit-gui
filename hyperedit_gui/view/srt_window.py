import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QVBoxLayout, QPushButton, QWidget, QTableView, QStyledItemDelegate, QHBoxLayout, QLabel, QListWidgetItem, QListWidget, QGridLayout, QCheckBox, QLineEdit
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem, QDoubleValidator, QValidator
from PySide6.QtCore import QCoreApplication, Qt

from hyperedit.srt import parse_srt

from hyperedit_gui.controller import Controller

_COL_INDEX_ID = 0
_COL_INDEX_CHECKED = 1
_COL_INDEX_START = 2
_COL_INDEX_END = 3
_COL_INDEX_ACTION = 4

# TODO this should go into hyperedit$
class ActionPanel(QWidget):
    def __init__(self, parent=None, id=None, enabled=True, controller=None):
        super().__init__(parent)

        self.id = id
        self.controller = controller # TODO controller should REALLY be a singleton
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)
        self.revertButton = QPushButton("Revert")
        self.revertButton.setEnabled(False)
        self.previewButton = QPushButton("Preview")
        self.layout.addWidget(self.revertButton)
        self.layout.addWidget(self.previewButton)

        self.revertButton.clicked.connect(self.revert)
        self.previewButton.clicked.connect(self.preview)

        self.setLayout(self.layout)

    def revert(self):
        print(f"Reverting {self.id}")

    # TODO: next deaggress, edit tree :o
    # TODO: oh and render previews?
    def preview(self):
        print(f"Previewing {self.id}")
        self.controller.PreviewSrt(self.id)
    
class SrtEntry:
    def __init__(self, entry) -> None:
        self.id = entry[0]
        self.start_time = entry[1]
        self.end_time = entry[2]

    def to_primitive(self):
        return (self.id, self.start_time, self.end_time)

class SrtWindow(QWidget):

    def __init__(self, parent, srts, controller=None):
        super().__init__(parent)

        self.controller = controller
        self.controller.AddSrtChangeObserver(self)
        self.srts = srts

        self.resize(600, 400)

        self.layout = QVBoxLayout(self)

        self.model = QStandardItemModel(0, 5)  # 4 columns
        self.model.setHeaderData(_COL_INDEX_ID, Qt.Horizontal, "ID")
        self.model.setHeaderData(_COL_INDEX_CHECKED, Qt.Horizontal, "")
        self.model.setHeaderData(_COL_INDEX_START, Qt.Horizontal, "Start")
        self.model.setHeaderData(_COL_INDEX_END, Qt.Horizontal, "End")
        self.model.setHeaderData(_COL_INDEX_ACTION, Qt.Horizontal, "Actions")

        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setColumnWidth(_COL_INDEX_ACTION, 200)

        self.layout.addWidget(self.tableView)

        # deaggress layout
        hlayout = self.create_deaggress_hlayout()
        self.layout.addLayout(hlayout)

        self.layout.addLayout(self.create_back_next_buttons())

        self.populateTable()

    def update_deaggress(self, text):
        if self.deaggress_validator.validate(text, 0)[0] == QValidator.Acceptable:
            self.controller.SetDeaggressSeconds(float(self.deaggress_seconds_line_edit.text()))
            self.deaggress_button.setEnabled(True)
        else:
            self.deaggress_button.setEnabled(False)

    def create_back_next_buttons(self):

        buttonLayout = QHBoxLayout()
        backButton = QPushButton('Tracks', self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addStretch(1)
        # buttonLayout.addWidget(nextButton)

        backButton.clicked.connect(lambda: self.parent().setCurrentIndex(1))
        # nextButton.clicked.connect(lambda: self.parent().setCurrentIndex(3))

        return buttonLayout
    
    def create_deaggress_hlayout(self):
        hlayout = QHBoxLayout()

        self.deaggress_button = QPushButton("Deaggress")
        self.deaggress_button.clicked.connect(self.controller.Deaggress)
        self.deaggress_button.setEnabled(self.controller.GetDeaggressSeconds() > 0)

        # deaggress seconds
        self.deaggress_seconds_line_edit = QLineEdit(self)
        self.deaggress_seconds_line_edit.setText(str(self.controller.GetDeaggressSeconds()))
        # validator
        self.deaggress_validator = QDoubleValidator(0.1, 60.0, 1, self)
        self.deaggress_validator.setNotation(QDoubleValidator.StandardNotation)
        self.deaggress_seconds_line_edit.setValidator(self.deaggress_validator)
        self.deaggress_seconds_line_edit.textChanged.connect(lambda x: self.update_deaggress(x))

        hlayout.addWidget(self.deaggress_button)
        hlayout.addWidget(QLabel("by seconds"))
        hlayout.addWidget(self.deaggress_seconds_line_edit)
        return hlayout

    def populateTable(self):
        # self.model.clear()
        self.model.clear()
        for e in self.srts:
            entry = SrtEntry(e)
            idItem = QStandardItem(entry.id)
            idItem.setFlags(~Qt.ItemIsEditable)
            enabledItem = QStandardItem() # Empty, will hold the checkbox
            startItem = QStandardItem(str(entry.start_time))
            startItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            endItem = QStandardItem(str(entry.end_time))
            endItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            actionItem = QStandardItem()  # Empty, will hold the button
            actionItem.setFlags(~Qt.ItemIsSelectable)
            self.model.appendRow([idItem, enabledItem, startItem, endItem, actionItem])

            enabledCheckbox = QCheckBox()
            actionPanel = ActionPanel(id=entry.id, enabled=True, controller=self.controller)
            current_row = self.model.rowCount() - 1
            self.tableView.setIndexWidget(self.model.index(current_row, _COL_INDEX_CHECKED), enabledCheckbox)
            self.tableView.setIndexWidget(self.model.index(current_row, _COL_INDEX_ACTION), actionPanel)

    def OnSrtChange(self):
        self.srts = self.controller.GetSrt()
        self.populateTable()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    srts = parse_srt("data/test.srt")
    window = SrtWindow(parent=None, srts=srts, controller=Controller())
    window.show()
    sys.exit(app.exec())