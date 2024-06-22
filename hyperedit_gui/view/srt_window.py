import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QTableView, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QGroupBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QValidator
from PySide6.QtCore import Qt

from hyperedit.srt import parse_srt

from hyperedit_gui.controller import Controller

_COL_INDEX_ID = 0
_COL_INDEX_CHECKED = 1
_COL_INDEX_START = 2
_COL_INDEX_END = 3
_COL_INDEX_ACTION = 4

# TODO this should go into hyperedit$
class EnabledCell(QWidget):
    def __init__(self, parent=None, id=None, enabled=True, controller=None):
        super().__init__(parent)

        self.id = id
        self.enabled = enabled
        self.controller = controller

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.checkbox = QCheckBox();
        self.checkbox.setChecked(self.enabled)
        self.checkbox.stateChanged.connect(self.Toggle)
        self.layout.addWidget(self.checkbox)

    def Toggle(self, state):
        self.controller.SetSrtRowEnabled(self.id, state == Qt.Checked.value)

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

        self.layout = QVBoxLayout(self)

        self.model = None
        self.resetModel()

        mainLayout = QHBoxLayout()
        self.tableView = QTableView()
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setModel(self.model)
        self.tableView.setColumnWidth(_COL_INDEX_ACTION, 200)

        mainLayout.addWidget(self.tableView)
        sideLayout = QVBoxLayout()
        sideLayout.addWidget(self.create_deaggress_groupbox())
        sideLayout.addWidget(self.create_render_groupbox())
        sideLayout.addStretch(1)
        mainLayout.addLayout(sideLayout)

        mainLayout.setStretch(0, 7.5)  # 80% to the table view
        mainLayout.setStretch(1, 2.5)  # 20% to the vertical layout

        self.layout.addLayout(mainLayout)

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
    
    def create_deaggress_groupbox(self):
        
        deaggress_layout = QVBoxLayout()
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

        # reset to zero
        self.zero_button = QPushButton("Zero")
        self.zero_button.clicked.connect(self.DeaggressZero)

        row = QHBoxLayout()
        row.addWidget(QLabel("Leading seconds"))
        row.addWidget(self.deaggress_seconds_line_edit)
        row.addWidget(self.deaggress_button)
        deaggress_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(self.zero_button)
        deaggress_layout.addLayout(row)
        deaggress_layout.addStretch(1)

        deaggress_group_box = QGroupBox("Deaggress")
        deaggress_group_box.setLayout(deaggress_layout)
        
        return deaggress_group_box
    
    def create_render_groupbox(self):
        
        render_layout = QVBoxLayout()
        
        row = QHBoxLayout()
        preview_checkbox = QCheckBox("Preview")
        preview_checkbox.stateChanged.connect(self.SetRenderPreview)
        row.addWidget(preview_checkbox)
        render_layout.addLayout(row)
        
        row = QHBoxLayout()
        render_button = QPushButton("Render")
        # render_button.clicked.connect(self.controller.Render)
        render_button.setEnabled(False)
        row.addWidget(render_button)

        render_layout.addLayout(row)

        render_group_box = QGroupBox("Rendering")
        render_group_box.setLayout(render_layout)

        return render_group_box
    
    def resetModel(self):
        if self.model:
            self.model.clear()

        self.model = QStandardItemModel(0, 5)  # 4 columns
        self.model.setHeaderData(_COL_INDEX_ID, Qt.Horizontal, "ID")
        self.model.setHeaderData(_COL_INDEX_CHECKED, Qt.Horizontal, "")
        self.model.setHeaderData(_COL_INDEX_START, Qt.Horizontal, "Start")
        self.model.setHeaderData(_COL_INDEX_END, Qt.Horizontal, "End")
        self.model.setHeaderData(_COL_INDEX_ACTION, Qt.Horizontal, "Actions")

    def ToggleEdit(self, id, state):
        self.controller.ToggleEdit(id, state == Qt.Checked.value)

    def SetRenderPreview(self, state):
        self.controller.SetRenderPreview(state == Qt.Checked.value)

    def DeaggressZero(self):
        self.deaggress_seconds_line_edit.setText("0")
        self.controller.DeaggressZero()

    def onSelectionChanged(self):
        selection_model = self.tableView.selectionModel()
        selected_indexes = selection_model.selectedRows()

        # Print the row numbers of selected rows
        selected_rows = sorted([index.row() for index in selected_indexes])
        print("Selected rows:", selected_rows)

    def populateTable(self):
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

            enabledCell = EnabledCell(id=entry.id, enabled=True, controller=self.controller)
            actionPanel = ActionPanel(id=entry.id, enabled=True, controller=self.controller)
            current_row = self.model.rowCount() - 1
            self.tableView.setIndexWidget(self.model.index(current_row, _COL_INDEX_CHECKED), enabledCell)
            self.tableView.setIndexWidget(self.model.index(current_row, _COL_INDEX_ACTION), actionPanel)
            
            
        # selects: Set selection behavior and mode
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.ExtendedSelection)
        selection_model = self.tableView.selectionModel()
        selection_model.selectionChanged.connect(self.onSelectionChanged)
        # self.tableView.resizeColumnsToContents()
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    def OnSrtChange(self):
        self.srts = self.controller.GetSrt()
        self.resetModel()
        self.tableView.setModel(self.model)
        self.populateTable()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    srts = parse_srt("data/test.srt")
    window = SrtWindow(parent=None, srts=srts, controller=Controller())
    # 4:3 default
    window.resize(960, 720)
    window.show()
    sys.exit(app.exec())