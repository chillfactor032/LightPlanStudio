#Python Imports
import json
import time
from enum import Enum

#PySide6 Imports
from PySide6.QtCore import QRunnable, Signal, Slot, QObject, Qt, QAbstractTableModel
from PySide6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QHeaderView, QMenu, QAbstractItemView, QStyledItemDelegate, QStyle
from PySide6.QtGui import QAction, QCursor, QBrush

#LightPlan Imports
import irc.client
from twitchio.ext import commands
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


class LightPlanRunner(QRunnable):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        progress = Signal(int, float, str)
        done = Signal(str)

    def __init__(self, twitch=None, lightplan_dict=None, stream_delay=0, adjust=0, starting_index=0):
        super(LightPlanRunner, self).__init__()
        self.signals = self.Signals()
        self.lightplan_dict = lightplan_dict
        self.twitch = twitch
        self.events = self.lightplan_dict["events"].copy()
        self.stream_delay_ms = stream_delay
        self.runtime_adjust_ms = adjust
        self.running = False
        self.lp_stopped = False
        self.start_time = 0
        self.elapsed_time = 0
        self.cur_index = starting_index

    def update_runtime_adjustment(self, adjust_ms):
        self.recalculate = True
        self.runtime_adjust_ms = adjust_ms

    def stop(self):
        self.lp_stopped = True

    def is_running(self):
        return self.running

    def precalculate_offset(self):
        for evt in self.events:
            calculated_offset = evt["offset"]
            if(not evt["ignore_delay"]):
                calculated_offset -= self.stream_delay_ms
            evt["offset"] = calculated_offset

    def sort_events(self, evts):
        sorted_events = []
        min_ms = 99999999
        min_evt = None

        while len(evts) > 0:
            min_ms = 99999999
            min_evt = None
            for x in range(0, len(evts)):
                calculated_offset = evts[x]["offset"]
                if(not evts[x]["ignore_delay"]):
                    calculated_offset -= self.stream_delay_ms
                if(calculated_offset < min_ms):
                    min_ms = calculated_offset
                    min_evt = evts[x]
                    evts.pop(x)
                    break
            sorted_events.append(min_evt)
        return sorted_events


    def run(self):
        num_events = len(self.events) 
        if(num_events==0):
            self.done("No Events To Process")
            return

        self.start_time = time.time()
        self.running = True
        self.elapsed_time = 0
        self.current_event = None
        calculated_offset = 0
        played_event_count = 0
        self.log("LightPlan Started")
        
        #Sort the events chronologically based on offset and stream delay factoring in ignore_delay
        self.precalculate_offset()
        self.events = sorted(self.events, key = lambda i: i['offset'])
        self.current_event = self.events.pop(0)
        self.progress(0, round(self.current_event["offset"]/1000,1), self.current_event["command"])

        while self.running == True:
            # Check to see if LP has been stopped
            if(self.lp_stopped):
                self.done("LightPlan Stopped")
                return

            self.elapsed_time_ms = int((time.time()-self.start_time)*1000)

            if(self.elapsed_time_ms >= (self.current_event["offset"]+self.runtime_adjust_ms)):
                error = self.elapsed_time_ms - self.current_event['offset']
                sign = "+"
                if(error<0):
                    sign = "-"
                self.log(f"Fired: {self.elapsed_time_ms} {sign}{error}ms")
                played_event_count += 1
                if(len(self.events)>0):
                    self.current_event = self.events.pop(0)
                    self.progress(played_event_count, round(self.current_event["offset"]/1000,1), self.current_event["command"])
                else:
                    self.done("LightPlan Complete")
                    return
            time.sleep(0.0001)
                

    def progress(self, cur_evt_num, event_count, next_command):
        self.signals.progress.emit(cur_evt_num, event_count, next_command)

    def done(self, msg):
        self.running = False
        self.log(msg)
        self.signals.done.emit(msg)

    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)


class TwitchIRC(QRunnable):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        irc_disconnect = Signal()
        irc_connect = Signal()

    def __init__(self, nickname, token, channel, server="irc.chat.twitch.tv", port=6667):
        super(TwitchIRC, self).__init__()
        self.stop = False
        self.signals = self.Signals()
        self.connection = False
        self.server = server
        self.port = port
        self.nickname = nickname
        self.token = "oauth:"+token
        if(len(channel) > 0 and channel[0] != "#"):
            channel = "#"+channel
        self.channel = channel
        self.reactor = irc.client.Reactor()
        
    def connected(self):
        if(self.connection):
            return self.connection.is_connected()
        return False
        
    def on_connect(self, connection, event):
        self.log("Connected to irc.chat.twitch.tv")
        connection.join(self.channel)
        self.signals.irc_connect.emit()

    def on_join(self, connection, event):
        self.log(f"Joined channel {self.channel}")

    def on_disconnect(self, connection, event):
        self.log("Disconnected from irc.chat.twitch.tv")
        self.stop = True
        self.signals.irc_disconnect.emit()

    def privmsg(self, text):
        if(self.connected()):
            self.connection.privmsg(self.channel, text)
    
    def disconnect(self):
        self.reactor.disconnect_all()
    
    def run(self):
        try:
            self.connect()
        except irc.client.ServerConnectionError as err:
            self.log(str(err), LogLevel.ERROR)

        while not self.stop:
            self.reactor.process_once()
        self.disconnect()

    def die(self):
        self.stop = True

    def connect(self):
        try:
            self.connection = self.reactor.server().connect(self.server, self.port, self.nickname, self.token)
        except irc.client.ServerConnectionError as err:
            raise
        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("join", self.on_join)
        self.connection.add_global_handler("disconnect", self.on_disconnect)

    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)


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
            self.signals.log.emit(f"Youtube URL [{self.youtube_url}]", LogLevel.DEBUG)
            self.youtube_obj = YouTube(self.youtube_url)
        except Exception as e:
            self.signals.log.emit(repr(e), LogLevel.ERROR)
        if(self.youtube_obj is None):
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
    
    def __init__(self, offset_ms=0, command="", comment="", ignore_delay=False):
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
        if(row >= 0 and row < len(self.model.events)):
            value = self.model.events[row].ignore_delay
            editor.setChecked(value)

    def setModelData(self, editor, model, index):
        value = editor.isChecked()
        row = index.row()
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
        self.action_set_start_event = QAction("Set Start Event")
        self.action_delete_event = QAction("Delete Selected Event")
        self.context_menu.addAction(self.action_insert_event)
        self.context_menu.addAction(self.action_set_start_event)
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
        evt = LightPlanEvent(0)
        self.insert_event(evt)

    def get_selected_event(self):
        if(self.selected_row >= 0 and self.selected_row < len(self.events)):
            return self.events[self.selected_row]

    def click_delete_event(self):
        if(self.selected_row >= 0 and self.selected_row < len(self.events)):
            evt = self.events.pop(self.selected_row)
            self.selected_row -= 1
            if(self.selected_row < 0):
                self.selected_row = 0
            self.table_view.selectRow(self.selected_row)
            top_left = self.createIndex(0, 0)
            bottom_right = self.createIndex(len(self.events)-1, len(self.headers))
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            self.layoutChanged.emit()
            return evt

    def clear_events(self):
        self.events.clear()
        top_left = self.createIndex(0, 0)
        self.dataChanged.emit(top_left, top_left)
        self.layoutChanged.emit()

    def update_commands(self, commands):
        self.commands = commands
        
    def rowCount(self, parent):
        return len(self.events)

    def columnCount(self, parent):
        return len(self.headers)
    
    def insert_event(self, event):
        row = len(self.events)
        self.events.append(event)
        if(self.persistent_editors):
            index = self.createIndex(row, 0)
            self.table_view.openPersistentEditor(index)
            index = self.createIndex(row, 1)
            self.table_view.openPersistentEditor(index)
        index = self.createIndex(row, 3)
        self.table_view.openPersistentEditor(index)
        top_left = self.createIndex(0, 0)
        bottom_right = self.createIndex(len(self.events)-1, len(self.headers))
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
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
                "command": evt.command,
                "comment": evt.comment,
                "ignore_delay": evt.ignore_delay
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
        