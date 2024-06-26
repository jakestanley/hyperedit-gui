import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QTableView, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QGroupBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QValidator
from PySide6.QtCore import Qt

from hyperedit_gui.controller import Controller
from hyperedit_gui.model.srt import Srt, GetSrts


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

class SrtWindow(QWidget):

    def __init__(self, parent, controller=None):
        super().__init__(parent)

        self.controller = controller
        self.controller.AddSrtChangeObserver(self)

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
        sideLayout.addWidget(self.create_stats_groupbox())
        sideLayout.addWidget(self.create_deaggress_groupbox())
        sideLayout.addWidget(self.create_multiselect_groupbox())
        sideLayout.addWidget(self.create_render_groupbox())
        sideLayout.addStretch(1)
        mainLayout.addLayout(sideLayout)

        mainLayout.setStretch(0, 7.5)  # 80% to the table view
        mainLayout.setStretch(1, 2.5)  # 20% to the vertical layout

        self.layout.addLayout(mainLayout)
        self.layout.addLayout(self.create_back_next_buttons())

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

        backButton.clicked.connect(lambda: self.parent().setCurrentIndex(1))

        return buttonLayout
    
    def create_stats_groupbox(self):

        stats_layout = QVBoxLayout()
        
        row = QHBoxLayout()
        self.stats_label = QLabel("Minutes")
        self.stats_line_edit = QLineEdit("0")
        row.addWidget(self.stats_label)
        row.addWidget(self.stats_line_edit)
        stats_layout.addLayout(row)
        stats_group_box = QGroupBox("Stats")
        stats_group_box.setLayout(stats_layout)

        return stats_group_box

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
    
    def create_multiselect_groupbox(self):

        multiselect_layout = QVBoxLayout()

        enable_button = QPushButton("Enable")
        disable_button = QPushButton("Disable")

        enable_button.clicked.connect(self.controller.EnableSelected)
        disable_button.clicked.connect(self.controller.DisableSelected)

        multiselect_layout.addWidget(enable_button)
        multiselect_layout.addWidget(disable_button)

        multiselect_group_box = QGroupBox("Multi-select")
        multiselect_group_box.setLayout(multiselect_layout)

        return multiselect_group_box

    def create_render_groupbox(self):
        
        render_layout = QVBoxLayout()
        
        row = QHBoxLayout()
        preview_checkbox = QCheckBox("Preview")
        preview_checkbox.setChecked(True) # default (for now)
        preview_checkbox.stateChanged.connect(lambda s: self.controller.SetRenderPreview(s == Qt.Checked.value))
        row.addWidget(preview_checkbox)

        play_after_render_checkbox = QCheckBox("Play after render")
        play_after_render_checkbox.stateChanged.connect(lambda s: self.controller.SetPlayAfterRender(s == Qt.Checked.value))
        row.addWidget(play_after_render_checkbox)
        render_layout.addLayout(row)
        
        row = QHBoxLayout()
        render_all_button = QPushButton("Render all")
        render_all_button.clicked.connect(self.controller.RenderAll)
        render_all_button.setEnabled(True)
        row.addWidget(render_all_button)
        render_layout.addLayout(row)

        row = QHBoxLayout()
        render_enabled_button = QPushButton("Render enabled")
        render_enabled_button.clicked.connect(self.controller.RenderEnabled)
        render_enabled_button.setEnabled(True)
        row.addWidget(render_enabled_button)
        render_layout.addLayout(row)

        row = QHBoxLayout()
        self.render_selection_button = QPushButton("Render enabled selection")
        self.render_selection_button.clicked.connect(self.controller.RenderEnabledSelection)
        self.render_selection_button.setEnabled(True) # TODO make this conditional programmatically based on selection
        row.addWidget(self.render_selection_button)
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

    def DeaggressZero(self):
        self.deaggress_seconds_line_edit.setText("0")
        self.controller.DeaggressZero()

    def onSelectionChanged(self):
        selection_model = self.tableView.selectionModel()
        selected_indexes = selection_model.selectedRows()

        # Print the row numbers of selected rows
        selected_rows = sorted([index.row() for index in selected_indexes])
        print("Selected rows:", selected_rows)
        self.controller.SetSelectedSrtRows(selected_rows)
        # TODO must reset this value in controller when SRT changes

    def populateTable(self):
        for entry in GetSrts():
            idItem = QStandardItem(entry.id)
            idItem.setFlags(~Qt.ItemIsEditable)
            enabledItem = QStandardItem() # Empty, will hold the checkbox
            # TODO use edit start/end times if available 
            startItem = QStandardItem(str(entry.original_start_time))
            startItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            endItem = QStandardItem(str(entry.original_end_time))
            endItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            actionItem = QStandardItem()  # Empty, will hold the button
            actionItem.setFlags(~Qt.ItemIsSelectable)
            self.model.appendRow([idItem, enabledItem, startItem, endItem, actionItem])
            self.model.itemChanged.connect(self.onItemChanged)

            enabledCell = EnabledCell(id=entry.id, enabled=entry.enabled, controller=self.controller)
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

    def onItemChanged(self, item):
        if item.column() == _COL_INDEX_START:
            GetSrts()[item.row()].edited_start_time = float(item.text())
        elif item.column() == _COL_INDEX_END:
            GetSrts()[item.row()].edited_end_time = float(item.text())

    def OnSrtChange(self):
        self.resetModel()
        self.tableView.setModel(self.model)
        self.populateTable()
        total_seconds = 0
        # TODO: if SRT has an edit, hint as such in the table view
        for srt in GetSrts():

            # if this SRT is enabled, calculate time for it
            if srt.enabled:
                start_time = srt.original_start_time
                end_time = srt.original_end_time
                # if either start or end times have been edited, use them for the calculation
                if srt.edited_start_time:
                    start_time = srt.edited_start_time
                if srt.edited_end_time:
                    end_time = srt.edited_end_time
                total_seconds = total_seconds + (end_time - start_time)
        self.stats_line_edit.setText(str(total_seconds / 60).split(".")[0])

if __name__ == "__main__":
    from hyperedit_gui.model.srt import LoadSrts
    app = QApplication(sys.argv)
    LoadSrts("data/test.srt")
    window = SrtWindow(parent=None, controller=Controller())
    # 4:3 default
    window.resize(960, 720)
    window.show()
    sys.exit(app.exec())