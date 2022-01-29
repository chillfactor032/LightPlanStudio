#Python Imports
import json
from enum import Enum

#PySide6 Imports
from PySide6.QtCore import QRunnable, Signal, Slot, QObject, Qt, QAbstractTableModel
from PySide6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QHeaderView, QMenu, QAbstractItemView, QStyledItemDelegate, QStyle
from PySide6.QtGui import QAction, QCursor, QBrush

#LightPlan Imports
from pytube import YouTube

#Log Levels
class LogLevel(Enum):
    INFO = 0
    ERROR = 10
    DEBUG = 20
    
    @staticmethod
    def get(value):
        for level in LogLevel:
            if(value == level.value):
                return level
        return LogLevel.INFO

   
class YoutubeDownloader(QRunnable):

    class Signals(QObject):
        done = Signal(bool, dict)
        log = Signal(str, LogLevel)
        
    def __init__(self, youtube_url, save_dir):
        super(YoutubeDownloader, self).__init__()
        self.youtube_url = youtube_url
        self.save_dir = save_dir
        self.audio_path = ""
        self.image_path = ""
        self.result = {}
        self.signals = YoutubeDownloader.Signals()
        
    def result(self):
        return self.result
        
    @Slot()
    def run(self):
        try:
            self.youtube_obj = YouTube(self.youtube_url)
        except Exception as e:
            self.signals.log.emit(repr(e), LogLevel.ERROR)
        if(not self.youtube_obj):
            self.signals.log.emit("Error Creating Youtube Obj", LogLevel.ERROR)
            self.signals.done.emit(False, self.result)
            return
        stream = self.youtube_obj.streams.filter(only_audio=True)[0]
        if(not stream):
            self.signals.log.emit("No Audio Stream Found", LogLevel.ERROR)
            self.signals.done.emit(False, self.result)
            return
        try:
            self.audio_path = stream.download(self.save_dir) 
        except Exception as e:
            self.signals.log.emit("Error downloading audio stream", LogLevel.ERROR)
            self.signals.log.emit(repr(e), LogLevel.ERROR)
            self.signals.done.emit(False, self.result)
        self.audio_path = self.audio_path.replace("\\", "/")
        """
        filename = self.youtube_obj.thumbnail_url.split("/")[-1]
        if("?" in filename):
            filename = filename.split("?")[0]
        response = requests.get(self.youtube_obj.thumbnail_url)
        self.image_path = os.path.join(self.save_dir,filename)
        if(response.status_code==200):
            try:
                with open(self.image_path, "wb") as img:
                    img.write(response.content)
            except Exception as e:
                self.signals.log.emit(repr(e), LogLevel.ERROR)
        else:
            self.signals.log.emit("Error Downloading Youtube Thumbnail", LogLevel.ERROR)
            self.signals.log.emit(f"Status Code: {response.status_code}", LogLevel.DEBUG)
            self.signals.done.emit(False, self.result)
            return
        """
        self.result["youtube"] = self.youtube_obj
        self.result["audio_path"] = self.audio_path
        self.result["image_path"] = self.image_path
        self.signals.done.emit(True, self.result)
        

class LightPlanEvent():
    
    def __init__(self, commands=[], offset_ms=0, command="", comment="", ignore_delay=False):
        self.commands = commands
        self.offset_ms = offset_ms
        self.command = command
        self.comment = comment
        self.ignore_delay = ignore_delay
        
    def __lt__(self, other):
        return self.offset_ms < other.offset_ms
        
    @staticmethod
    def msToStr(ms):
        ms = ms / 1000
        mins, secs = divmod(ms, 60)
        return "{:02d}:{:06.3f}".format(int(mins), secs)
        
    @staticmethod
    def strToMs(offset_str):
        mins = 0
        secs = 0
        try:
            ms = 0
            split = offset_str.split(":")
            mins = int(split[0])
            secs = float(split[1])
        except Exception as e:
            return 0
        return (mins * 60 * 1000) + int(secs * 1000)
  
  
class LineEditDelegate(QStyledItemDelegate):
    
    def __init__(self, model):
        super().__init__(model)
        self.model = model
        
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setInputMask("99\:99\.999")
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        value_ms = LightPlanEvent.strToMs(value)
        model.setData(index, value_ms, Qt.EditRole)


class CheckBoxDelegate(QStyledItemDelegate):
    
    def __init__(self, model):
        super().__init__(model)
        self.model = model
        
    def createEditor(self, parent, option, index):
        editor = QCheckBox(parent)
        editor.setStyleSheet("margin-left:45%; margin-right:55%;");
        return editor

    def setEditorData(self, editor, index):
        row = index.row()
        if(row > 0 and row < len(self.model.events)):
            value = self.model.events[index.row()].ignore_delay
            editor.setChecked(value)

    def setModelData(self, editor, model, index):
        value = editor.isChecked()
        model.setData(index, value, Qt.EditRole)


class ComboBoxDelegate(QStyledItemDelegate):
        
    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.itemlist = None
        
    def createEditor(self, parent, option, index):
        if self.itemlist is None:
            self.itemlist = self.model.commands
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.addItems([""])
        editor.addItems(self.itemlist)
        editor.setCurrentIndex(0)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        ind = editor.findText(value)
        if(ind == -1):
            editor.setItemText(0, value)
            editor.setCurrentIndex(0)
        else:
            editor.setCurrentIndex(ind)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

        
class LightPlanTableModel(QAbstractTableModel):
    
    headers = ["Offset", "Command", "Comment", "Ignore Delay"]
    column_width = [75, 125, 0, 100]
    persistent_editors = False
    
    def __init__(self, parent, events, commands, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.events = events
        self.commands = commands
        self.table_view = parent
        self.table_view.setModel(self)
        self.table_view.selectionModel().selectionChanged.connect(self.selection_changed)
        self.line_edit_delegate = LineEditDelegate(self)
        self.combo_box_delegate = ComboBoxDelegate(self)
        self.check_box_delegate = CheckBoxDelegate(self)
        self.table_view.setItemDelegateForColumn(0, self.line_edit_delegate)
        self.table_view.setItemDelegateForColumn(1, self.combo_box_delegate)
        self.table_view.setItemDelegateForColumn(3, self.check_box_delegate)
        self.selected_row = -1
        self.context_menu = QMenu()
        self.action_insert_event = QAction("Add Event")
        self.action_delete_event = QAction("Delete Selected Event")
        self.context_menu.addAction(self.action_insert_event)
        self.context_menu.addAction(self.action_delete_event)
        self.action_insert_event.triggered.connect(self.click_add_event)
        self.action_delete_event.triggered.connect(self.click_delete_event)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.check_table_width()
        
    def check_table_width(self):
        table_width = self.table_view.width()
        scroll_bar_width = self.table_view.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        horiz_header_width = sum(self.column_width)
        self.table_view.setColumnWidth(0,self.column_width[0])
        self.table_view.setColumnWidth(1,self.column_width[1])
        self.table_view.setColumnWidth(2,table_width-horiz_header_width-3-scroll_bar_width)
        self.table_view.setColumnWidth(3,self.column_width[3])
        
    def selection_changed(self, selected, deselected):
        #Since you can only select 1 row at a time, this becomes easier
        deselected_row = -1
        item_selection_range = selected.first()
        if(not item_selection_range or not item_selection_range.isValid() or item_selection_range.isEmpty()):
            self.selected_row = -1
            return
        self.selected_row = item_selection_range.top()
        if(deselected.count()>0):
            deselected_row = deselected.first().top()
        self.scrollToRow(self.selected_row)
    
    def show_context_menu(self):
        self.context_menu.popup(QCursor.pos())
        
    def click_add_event(self):
        evt = LightPlanEvent(self.commands, 0)
        self.insertEvent(evt)
        
    def click_delete_event(self):
        if(self.selected_row >= 0 and self.selected_row < len(self.events)):
            self.events.pop(self.selected_row)
            self.selected_row -= 1
            if(self.selected_row < 0):
                self.selected_row = 0
            self.table_view.selectRow(self.selected_row)
            top_left = self.createIndex(0, 0)
            bottom_right = self.createIndex(len(self.events)-1, len(self.headers))
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            self.layoutChanged.emit()
        
    def update_commands(self, commands):
        self.commands = commands
        
    def rowCount(self, parent):
        return len(self.events)

    def columnCount(self, parent):
        return len(self.headers)
    
    def insertEvent(self, event):
        row = len(self.events)
        self.events.append(event)
        if(self.persistent_editors):
            index = self.createIndex(row, 0)
            self.table_view.openPersistentEditor(index)
            index = self.createIndex(row, 1)
            self.table_view.openPersistentEditor(index)
        index = self.createIndex(row, 3)
        self.table_view.openPersistentEditor(index)
        self.layoutChanged.emit()
        self.scrollToRow(row)
        self.check_table_width()
        return True
    
    def setData(self, index, value, role):
        if(role != Qt.EditRole):
            return False
        if(index.column() == 0):
            self.events[index.row()].offset_ms = int(value)
        elif(index.column() == 1):
            self.events[index.row()].command = str(value)
        elif(index.column() == 2):
            self.events[index.row()].comment = str(value)
        elif(index.column() == 3):
            self.events[index.row()].ignore_delay = value
        return True
                
    def data(self, index, role):
        if(not index.isValid()):
            return None
        elif(role in [Qt.DisplayRole, Qt.EditRole]):           
            if(index.column() == 0):
                if(role == Qt.EditRole):
                    return  self.events[index.row()].offset_ms
                if(role == Qt.DisplayRole):
                    return  LightPlanEvent.msToStr(self.events[index.row()].offset_ms)
            elif(index.column() == 1):
                return  self.events[index.row()].command
            elif(index.column() == 2):
                return  self.events[index.row()].comment
            elif(index.column() == 3):
                return  ""
            return None
        return None
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col]
        return None

    def sort(self, col, order):
        if(col != 0):
            return False
        num_events = len(self.events)
        if(num_events<=1):
            return True
        top_left = self.createIndex(0, 0)
        bottom_right = self.createIndex(num_events-1, len(self.headers))
        if(order ==  Qt.AscendingOrder):
            self.events.sort(key=lambda x: x.offset_ms)
        else:
            self.events.sort(key=lambda x: x.offset_ms, reverse=True)
        self.layoutChanged.emit()
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
        self.scrollToRow(self.selected_row)
        return True
            
    def scrollToRow(self, row):
        if(row > 0 and row < len(self.events)):
            row_index = self.createIndex(row, 0)
            self.table_view.scrollTo(row_index)
    
    def exportJsonDict(self):
        evt_list = []
        for evt in self.events:
            obj = {
                "offset": evt.offset_ms,
                "command": evt.comment,
                "comment": self.comment,
                "ignore_delay": self.ignore_delay
            }
            evt_list.append(obj)
        return evt_list
    
    def importEvents(self, events):
        for evt in events:
            if(type(evt)==LightPlanEvent):
                self.events.append(evt)
        num_events = len(self.events)
        if(num_events>0):
            top_left = self.createIndex(0, 0)
            bottom_right = self.createIndex(num_events-1, len(self.headers))
            self.layoutChanged.emit()
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        