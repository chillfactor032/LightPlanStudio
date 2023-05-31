# Python Imports
import os
import sys
import datetime
import json
import time
from urllib import response
from urllib.parse import ParseResultBytes
import requests
from pytube import YouTube
from pathlib import Path
from enum import Enum
import hashlib
import unicodedata
import re
import shutil

# PySide6 Imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QStyle, 
                            QDialog, QInputDialog, QSplashScreen, 
                            QMessageBox,QAbstractItemView, 
                            QLineEdit, QFileDialog, QMenu, QTableWidgetItem, QTreeWidgetItem)
from PySide6.QtCore import (QFile, Slot, Signal, QObject, QStandardPaths,
                            QSettings, QTextStream, Qt, QTimer, QThreadPool, QFileSystemWatcher, \
                            QUrl, QSize)
from PySide6.QtGui import (QStandardItem, QPixmap, QIcon, QMovie, 
                            QDesktopServices, QCursor, QAction, QIntValidator)
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

# LightPlanStudio Imports
import Resources
import UI_Components as UI
from LightPlanStudioLib import *

class LightPlanStudio(QMainWindow, UI.Ui_LPS_MainWindow):
    def __init__(self, app_name, version, app):
        super(LightPlanStudio, self).__init__()

        self.app = app

        #Read Version File From Resources
        version_file = QFile(":version.json")
        version_file.open(QFile.ReadOnly)
        text_stream = QTextStream(version_file)
        version_file_text = text_stream.readAll()
        self.version_dict = json.loads(version_file_text)
        self.app_name = self.version_dict["product_name"]
        self.version = self.version_dict["version"]
        self.repo = "https://github.com/chillfactor032/LightPlanStudio"
        self.lightplan_studio_key = "a1a33b06"
        self.youtube_key_url = "http://lightplanstudio.com/api/youtube_get_key.php"
        self.youtube_api_key = None

        #Load UI Components
        self.setupUi(self)
        self.setWindowTitle(f"{self.app_name} {self.version}")

        # About Text
        self.about_text = f"Light Plan Studio v{self.version}\n\nAuthor: ChillFacToR032\nContact: chill@chillaspect.com\n\n{self.repo}"

        ## Get Directories to Store Files
        self.documents_dir =  QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        self.temp_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.TempLocation), "LightPlanStudio")
        self.config_dir = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
        
        os.makedirs(self.config_dir, exist_ok=True)
        if(not os.path.isdir(self.config_dir)):
            QMessageBox.critical(self, "LightPlan Studio", f"Could not create config directory!\n\n{self.config_dir}")
            return

        self.ini_path = os.path.join(self.config_dir, "LightPlanStudio.ini").replace("\\", "/")
        self.default_lightplan_dir = os.path.join(self.config_dir, "LightPlans").replace("\\", "/")
        self.audio_dir = os.path.join(self.config_dir, "Audio").replace("\\", "/")
        self.lp_db_path = os.path.join(self.config_dir, "lightplan.db").replace("\\", "/")

        os.makedirs(self.default_lightplan_dir, exist_ok=True)
        if(not os.path.isdir(self.default_lightplan_dir)):
            QMessageBox.critical(self, "LightPlan Studio", f"Could not create default LightPlan directory!\n\n{self.default_lightplan_dir}")
            return
        
        os.makedirs(self.audio_dir, exist_ok=True)
        if(not os.path.isdir(self.audio_dir)):
            QMessageBox.critical(self, "LightPlan Studio", f"Could not create audio cache directory!\n\n{self.audio_dir}")
            return

        #Get Settings
        self.settings = QSettings(self.ini_path, QSettings.IniFormat)
        self.log_level = LogLevel.get(self.settings.value("LightPlanStudio/LogLevel", LogLevel.INFO, int))
        if(self.settings):
            self.log("Settings Loaded")
        self.lightplan_dir = self.settings.value("LightPlanStudio/LightPlanDir", self.default_lightplan_dir)
        if(not os.path.isdir(self.lightplan_dir)):
            os.mkdir(self.lightplan_dir)

        self.defaultCommands = [
            "!hypelights",
            "!dim",
            "!spring",
            "!tropical",
            "!arctic",
            "!sunset",
            "!aurora",
            "!deep",
            "!police",
            "!normal",
            "!bright",
            "!blackout",
            "!darkroom",
            "!toxic",
            "!mystic",
            "!limelight",
            "!rainbow",
            "!starry"
        ] 

        # UI Attributes
        self.height = 800
        self.defaultWidth = 800
        self.expandedWidth = 1250
        
        self.log(f"Config File:{self.ini_path}", LogLevel.DEBUG)

        ## Setup UI
        self.loading_pixmap = QPixmap(":resources/img/loading.gif")
        self.loading_movie = QMovie(":resources/img/loading.gif")
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.ui.loading_label.setFixedSize(self.loading_pixmap.size())
        self.loading_dialog.setFixedSize(self.loading_pixmap.size())
        self.loading_dialog.setMovie(self.loading_movie)
        self.loading_dialog.hide()
        self.connected_movie = QMovie(":resources/img/connected.gif")
        self.connected_movie.setScaledSize(QSize(40,40))
        self.connected_label.setText("")
        self.connected_label.setMovie(self.connected_movie)
        self.connected_movie.start()
        self.connected_label.setHidden(True)
        
        style = self.style()
        self.search_icon = style.standardIcon(QStyle.SP_FileDialogContentsView)
        self.check_icon = style.standardIcon(QStyle.SP_DialogApplyButton)
        self.x_icon = style.standardIcon(QStyle.SP_DialogCloseButton)
        self.dir_icon = style.standardIcon(QStyle.SP_DirIcon)
        self.connected_icon = style.standardIcon(QStyle.SP_DialogYesButton)
        self.play_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaPlay))
        self.pause_icon = QIcon.fromTheme("media-playback-pause.png", style.standardIcon(QStyle.SP_MediaPause))
        self.stop_icon = QIcon.fromTheme("media-playback-stop.png", style.standardIcon(QStyle.SP_MediaStop))
        self.volume_icon = style.standardIcon(QStyle.SP_MediaVolume)
        self.play_button.setIcon(self.play_icon)
        self.stop_button.setIcon(self.stop_icon)
        self.ssl_lookup_button.setIcon(self.search_icon)
        self.song_loaded_status_icon.setPixmap(self.x_icon.pixmap(self.song_loaded_status_icon.width(), self.song_loaded_status_icon.height()))
        self.vol_label.setPixmap(self.volume_icon.pixmap(self.vol_label.width(), self.vol_label.height()))
        self.current_time_lcd.display("00:00.000")
        self.green_button_css = 'QPushButton {background-color: #A3C1DA; color: green;}'
        self.red_button_css = 'QPushButton {background-color: #A3C1DA; color: red;}'
        self.default_button_css = self.twitch_connect_button.styleSheet()
        self.calc_delay_button.setEnabled(False)
        self.control_startlp_button.setEnabled(False)
        self.delay_lcd.display("0")
        self.start_event_edit.setInputMask("99\:99\.999")
        self.event_table_view.setStyleSheet("QTableView:disabled {background-color:#ffffff;}")
        self.twitch_connect_button.setCheckable(True)
        self.control_startlp_button.setCheckable(True)
        self.lp_tree_context_delete_action = QAction("Delete LightPlan")
        self.lp_tree_context_delete_action.triggered.connect(self.lp_tree_delete_clicked)
        self.lp_tree_context_move_action = QAction("Move Item")
        self.lp_tree_context_move_action.triggered.connect(self.lp_tree_move_clicked)
        self.lp_tree_context_create_action = QAction("Create Root Folder")
        self.lp_tree_context_create_action.triggered.connect(self.lp_tree_create_clicked)
        self.lp_tree_context_createroot_action = QAction("Create Top Level Folder")
        self.lp_tree_context_createroot_action.triggered.connect(self.lp_tree_createroot_clicked)
        self.lp_tree_context_rename_action = QAction("Rename Folder")
        self.lp_tree_context_rename_action.triggered.connect(self.lp_tree_rename_clicked)
        self.lp_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lp_tree_view.customContextMenuRequested.connect(self.lptree_show_context_menu)
        int_validator = QIntValidator(self)
        self.lp_sslid_edit.setValidator(int_validator)

        #Set window Icon
        default_icon_pixmap = QStyle.StandardPixmap.SP_FileDialogListView
        self.lps_icon_pixmap = QPixmap(":resources/img/icon.ico")
        self.lightplan_icon = QIcon(self.lps_icon_pixmap)
        default_icon = self.style().standardIcon(default_icon_pixmap)
        if(self.lightplan_icon):
            self.setWindowIcon(self.lightplan_icon)
        else:
            self.setWindowIcon(default_icon)
            self.lightplan_icon = default_icon
        
        ## Setup Audio Player
        self.video_output = QVideoWidget(self)
        #Maybe Show the video somewhere in the future. For now, hide it
        self.video_output.hide()
        self.audio_output = QAudioOutput()
        self.audio_player = QMediaPlayer()
        self.audio_player.setAudioOutput(self.audio_output)
        self.audio_player.setVideoOutput(self.video_output)
        self.audio_player.errorOccurred.connect(self.audio_player_error)
        self.audio_player.positionChanged.connect(self.positionChanged)
        self.audio_player.durationChanged.connect(self.durationChanged)
        self.audio_player.playbackStateChanged.connect(self.playbackStateChanged)
        
        # Init Variables
        self.duration_ms = 0
        self.stream_delay_ms = 0
        self.delay_adjust_ms = 0
        self.resume_on_release = False
        self.lightplan_files = []
        self.file_watcher = None
        self.status_msg = "Welcome to LightPlan Studio"
        self.lightplan_start_timer = QTimer()
        self.lightplan_start_timer.timeout.connect(self.update_lightplan_elapsed)
        self.lightplan_start_time = None
        self.next_event_secs = 0
        self.key_listener = None
        self.lightplan_runner = None
        self.keyevent_eater = KeyEventEater()
        self.insert_event_button.installEventFilter(self.keyevent_eater)
        self.expanded_tree_items = []
        self.custom_cmds = []
        self.ssl_queue_buttons = []

        # Check for updated commands if UpdateCmdsOnStart = True
        update_cmds = valueToBool(self.settings.value("LightPlanStudio/UpdateCmdsOnStart", False))
        if(update_cmds):
            cmds = self.fetch_commands()
            if(cmds["commands"] is not None):
                self.defaultCommands = cmds["commands"]
                self.log("Updated Commands")
            else:
                self.log("Could not update commands")
        self.custom_cmds = self.settings.value("LightPlanStudio/UpdateCmdsOnStart", False)

        #Get Youtube API Key
        self.get_youtube_api_key()

        ## Event Table ##
        self.lp_table_model = LightPlanTableModel(self.event_table_view, [], self.get_commands())
        self.lp_table_model.action_set_start_event.triggered.connect(self.click_set_start_event)
        self.lp_table_model.dataChanged.connect(self.update_progressbar)
        self.control_lp_progressbar.valueChanged.connect(self.update_progressbar)
        self.update_progressbar()

        ## Setup UI Signals ##
        # Menu Signals
        self.action_new_lp.triggered.connect(self.menu_click)
        self.action_open_lp.triggered.connect(self.menu_click)
        self.action_save_lp.triggered.connect(self.menu_click)
        self.action_import_lp.triggered.connect(self.menu_click)
        self.action_export_lp.triggered.connect(self.menu_click)
        self.action_open_lpdir.triggered.connect(self.menu_click)
        self.action_open_configdir.triggered.connect(self.menu_click)
        self.action_backup.triggered.connect(self.menu_click)
        self.action_exit.triggered.connect(self.menu_click)
        self.action_settings.triggered.connect(self.menu_click)
        self.action_show_log.triggered.connect(self.menu_click)
        self.action_help_about.triggered.connect(self.menu_click)
        self.action_help_oauth.triggered.connect(self.menu_click)
        self.action_help_docs.triggered.connect(self.menu_click)
        self.action_help_checkcmds.triggered.connect(self.menu_click)
        self.statusbar.messageChanged.connect(self.status_msg_changed)

        # Button Signals
        self.ssl_lookup_button.clicked.connect(self.show_ssl_match_dialog)
        self.debug_hidelog_button.clicked.connect(self.click_hidelog_button)
        self.load_song_button.clicked.connect(self.load_youtube)
        self.insert_event_button.pressed.connect(self.insert_event)
        self.play_button.clicked.connect(self.click_play_button)
        self.stop_button.clicked.connect(self.click_stop_button)
        self.song_slider.sliderMoved.connect(self.song_slider_moved)
        self.song_slider.sliderPressed.connect(self.song_slider_pressed)
        self.song_slider.sliderReleased.connect(self.song_slider_released)
        self.calc_delay_button.clicked.connect(self.show_calc_delay_dialog)
        self.set_delay_button.clicked.connect(self.set_delay_dialog)
        self.twitch_connect_button.clicked.connect(self.click_twitch_connect_button)
        self.delay_adjust_spinner.valueChanged.connect(self.delay_spinner_changed)
        self.delay_adjust_slider.sliderMoved.connect(self.delay_slider_moved)
        self.delay_adjust_slider.sliderReleased.connect(self.delay_slider_released)
        self.lp_save_button.clicked.connect(self.click_save_button)
        self.control_startlp_button.clicked.connect(self.click_start_lightplan)
        self.volume_slider.valueChanged.connect(self.volume_changed)
        self.volume_slider.sliderReleased.connect(self.volume_change_event)
        self.volume_changed()

        ## ThreadPool
        self.threadpool = QThreadPool()
        
        ## Twitch Chat 
        self.twitch = None

        # Setup UI Based on Config
        self.check_showlog()
        self.set_status(self.status_msg)

        #Create Connection to LightPlan SQLite DB
        self.lightplan_db = LightPlanDB(self.version, self.lp_db_path)
        self.lightplan_db.signals.log.connect(self.log)

        # LightPlan Explorer Tab
        self.lp_tree_model = LightPlanTreeModel()
        self.lp_tree_model.setHorizontalHeaderLabels(['LightPlans'])
        self.lp_tree_view.setModel(self.lp_tree_model)
        self.lp_tree_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.lp_tree_view.viewport().setAcceptDrops(True)
        self.lp_tree_view.setAcceptDrops(True)
        self.lp_tree_view.setDropIndicatorShown(True)
        self.lp_tree_view.setIndentation(12)
        self.lp_tree_view.doubleClicked.connect(self.lp_tree_doubleclicked)

        #New code for SQLite
        self.update_lightplan_explorer()

        # StreamerSongList Integration
        self.streamer_song_list = StreamerSongList(0)

        #Set initial lightplan
        self.current_lightplan = {
            "id": 0,
            "folder_id": 0
        }
        self.current_lightplan["lightplan"] = self.lightplan_gui_to_dict()
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()

        # Initialize Window Geometry
        geometry = self.settings.value("LightPlanStudio/geometry")
        window_state = self.settings.value("LightPlanStudio/windowState")
        if geometry and window_state:
            self.restoreGeometry(geometry)
            self.restoreState(window_state)
        self.refresh_ssl_layout()

    ### Menu Signals #####
    def menu_click(self):
        sender = self.sender()
        if(sender == self.action_new_lp):
            self.new_lp_clicked()
        elif(sender == self.action_open_lp):
            self.show_file_dialog()
        elif(sender == self.action_save_lp):
            self.click_save_button()
        elif(sender == self.action_import_lp):
            self.import_lightplans()
            self.update_lightplan_explorer()
        elif(sender == self.action_export_lp):
            self.log("Ohhh a new feature is coming!", LogLevel.INFO)
            self.log("Export LightPlan - not implemented yet", LogLevel.DEBUG)
        elif(sender == self.action_backup):
            self.generate_backup_file()
        elif(sender == self.action_open_configdir):
            os.startfile(self.config_dir)
        elif(sender == self.action_exit):
            self.close()
        elif(sender == self.action_settings):
            self.show_settings_dialog()
        elif(sender == self.action_show_log):
            self.toggle_logvisible()
        elif(sender == self.action_help_about):
            self.update_lightplan_explorer()
            QMessageBox.about(self, "LightPlan Studio", self.about_text)
        elif(sender == self.action_help_oauth):
            QDesktopServices.openUrl(QUrl("https://www.twitchapps.com/tmi/"))
        elif(sender == self.action_help_docs):
            QDesktopServices.openUrl(QUrl("https://lightplanstudio.com/wiki/doku.php"))
        elif(sender == self.action_help_checkcmds):
            cmds = self.fetch_commands()
            if(cmds["commands"] is not None and cmds["commands"] != self.defaultCommands):
                self.defaultCommands = cmds["commands"]
                self.lp_table_model.update_commands(self.defaultCommands)
                QMessageBox.information(self, "LightPlan Studio", "Commands have been updated.")
            else:
                QMessageBox.information(self, "LightPlan Studio", "Commands are up to date.")
    
    def generate_backup_file(self):
        now = int(time.time())
        suggested_filename = f"LPSBackup_{self.version}_{now}.lps"
        backup_file_path = os.path.join(self.config_dir, suggested_filename).replace("\\", "/")
        folders = self.lightplan_db.fetch_all_folders()
        lightplans = self.lightplan_db.fetch_all_lightplans()
        backup_dict = {
            "version": self.version,
            "date": datetime.datetime.timestamp(datetime.datetime.now()),
            "folders": [],
            "lightplans": [],
        }
        for folder in folders:
            backup_dict["folders"].append(folder)
        for lp in lightplans:
            backup_dict["lightplans"].append(lp)
        with open(backup_file_path, "w") as file:
            json.dump(backup_dict, file)
        QMessageBox.information(self, "Backup File", f"Backup file created in config directory:\n\n{backup_file_path}")
        self.log(f"Created Backup File {suggested_filename}", LogLevel.INFO)
        self.log(f"Created Backup File {backup_file_path}", LogLevel.DEBUG)

    def restore_backup_file(self):
        now = int(time.time())
        suggested_filename = f"LPSBackup_{self.version}_{now}.lps"
        backup_file_path = os.path.join(self.config_dir, suggested_filename).replace("\\", "/")
        folders = self.lightplan_db.fetch_all_folders()
        lightplans = self.lightplan_db.fetch_all_lightplans()
        backup_dict = {
            "version": self.version,
            "date": datetime.datetime.timestamp(datetime.datetime.now()),
            "folders": [],
            "lightplans": [],
        }
        for folder in folders:
            backup_dict["folders"].append(folder)
        for lp in lightplans:
            backup_dict["lightplans"].append(lp)
        with open(backup_file_path, "w") as file:
            json.dump(backup_dict, file)
        QMessageBox.information(self, "Backup File", f"Backup file created in config directory:\n\n{backup_file_path}")
        self.log(f"Created Backup File {suggested_filename}", LogLevel.INFO)
        self.log(f"Created Backup File {backup_file_path}", LogLevel.DEBUG)

    def get_youtube_api_key(self):
        headers = {"User-Agent": f"LightPlan Studio {self.version}"}
        #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
        params = {"key": self.lightplan_studio_key}
        try:
            response = requests.get(self.youtube_key_url, params=params, headers=headers)
            if(response.status_code == 200):
                try:
                    jsonObj = response.json()
                    self.youtube_api_key = jsonObj["youtube_api_key"]
                    self.log("Fetched Youtube API Key from LightPlanStudio.com", LogLevel.INFO)
                    return True
                except json.decoder.JSONDecodeError as e:
                    self.log("Error fetching Youtube API Key from LightPlanStudio.com", LogLevel.ERROR)
                    self.log(str(e), LogLevel.ERROR)
                    self.log(response.text, LogLevel.DEBUG)
            else:
                try:
                    self.log(f"Status Code {response.status_code} when fetching Youtube API Key from LightplanStudio.com", LogLevel.ERROR)
                    jsonObj = response.json()
                    msg = jsonObj["message"]
                    self.log(msg, LogLevel.ERROR)
                except json.decoder.JSONDecodeError as e:
                    self.log("Error processing response from LightPlanStudio.com", LogLevel.ERROR)
                    self.log(str(e), LogLevel.ERROR)
                self.log(response.text, LogLevel.DEBUG)
        except Exception as e:
            self.log("Error while fetching Youtube API Key", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
        return False

    def youtube_region_check(self, result):
        if result and not result["error"]:
            if result["us_blocked"] or result["au_blocked"]:
                if result["us_blocked"] == True and result["au_blocked"] == False:
                    QMessageBox.warning(self, "LightPlan Studio", "Your Youtube video is blocked in the US.")
                elif result["us_blocked"] == False and result["au_blocked"] == True:
                    QMessageBox.warning(self, "LightPlan Studio", "Your Youtube video is blocked in Australia.")
                else:
                    QMessageBox.warning(self, "LightPlan Studio", "Your Youtube video is blocked in both the US and Australia.")
            else:
                self.log("Youtube Video is NOT region blocked", LogLevel.DEBUG)


    ## SSL Integration Functions
    def check_start_ssl_connection(self):
        ssl_int = valueToBool(self.settings.value("StreamerSongList/IntegrationEnabled", False))

        #IF ssl integration not enabled, do nothing
        if(not ssl_int):
            return

        user = self.settings.value("Twitch/Channel", "").strip()
        #If user is blank, do nothing
        if(len(user) <= 0):
            return

        #If user hasnt changed and still connected, dont do anything
        if(user == self.streamer_song_list.get_user() and self.streamer_song_list.connected()):
            return

        #If connected, disconnect
        if(self.streamer_song_list.connected()):
            self.streamer_song_list.disconnect()
        
        #Create new ssl object
        self.streamer_song_list = StreamerSongList()
        
        #Map the channel user to an SSL Id
        if not self.streamer_song_list.sslId_from_user(user):
            self.log(f"Could not map user [{user}] to ssl id", LogLevel.ERROR)
            return

        #Map signals to slots
        self.streamer_song_list.signals.disconnected.connect(self.ssl_disconnected)
        self.streamer_song_list.signals.connected.connect(self.ssl_connected)
        self.streamer_song_list.signals.queue_update.connect(self.ssl_queue_update)
        self.streamer_song_list.signals.log.connect(self.log)

        # Start the thread
        self.threadpool.start(self.streamer_song_list)
        

    ## SSL Integration Slots
    def refresh_ssl_layout(self, ssl_queue=[]):
        for button in self.ssl_queue_buttons:
            self.ssl_layout.removeWidget(button)
            button.deleteLater()
        self.ssl_queue_buttons.clear()
        
        for song in ssl_queue:
            text = f"{song['title']} - {song['artist']}"
            if len(text) > 25:
                text = text[:25] + "..."
            button = SSLButton(text, self)
            button.data = song
            button.clicked.connect(self.ssl_button_clicked)
            self.ssl_queue_buttons.append(button)

        self.ssl_queue_buttons.reverse()

        for button in self.ssl_queue_buttons:
            self.ssl_layout.insertWidget(0, button)

    def ssl_button_clicked(self):
        sender = self.sender()
        self.log("SSL Button Clicked", LogLevel.DEBUG)
        self.log(sender.data, LogLevel.DEBUG)
        lp = sender.data
        if not lp:
            return
        self.open_lp(lp["id"])
        self.click_start_lightplan()

    def ssl_connected(self):
        self.log("Event Connected to StreamerSongList")
    
    def ssl_disconnected(self):
        self.log("Event Disconnected from StreamerSongList")
    
    def ssl_queue_update(self, queue_dict):
        size = len(queue_dict)
        self.log(f"SSL: Queue Update Event ({size})")
        self.log(str(queue_dict), LogLevel.DEBUG)
        #Map SSL Queue Songs to LightPlans
        queue = []
        for song in queue_dict:
            if song is None:
                continue
            for lpf in self.lightplan_files:
                try:
                    ssl_id = int(lpf["ssl_id"])
                except ValueError as ve:
                    ssl_id = 0
                if song["id"] == ssl_id:
                    queue.append(lpf)
                    title = lpf["title"]
                    artist = lpf["artist"]
                    self.log(f"Matched SSL Song: {artist} - {title}", LogLevel.DEBUG)
        self.refresh_ssl_layout(queue)
    
    # New LightPlan Explorer Code
    def update_lightplan_explorer(self):
        expanded = self.get_expanded_tree_objs()
        print("Previously Expanded LP Tree Items:")
        for e in expanded:
            print(f"{e.artist} - {e.title} id: {e.id} parent_id: {e.parent_id}")

        lightplans = self.lightplan_db.fetch_all_lightplans()
        folders = self.lightplan_db.fetch_all_folders()
        self.lp_tree_model.clear()
        self.lp_tree_model.setHorizontalHeaderLabels(['LightPlans'])
        folder_items = []
        lightplan_items = []
        artist_items = []

        # Create all folder objects
        for folder in folders:
            folder_obj = LightPlanTreeItem(folder["name"], TreeItemType.FOLDER)
            folder_obj.setEditable(False)
            folder_obj.setData(folder["name"], Qt.DisplayRole)
            folder_obj.setData(folder, Qt.UserRole)
            folder_obj.setIcon(self.dir_icon)
            folder_obj.setParentId(folder["parent_id"])
            folder_obj.setId(folder["folder_id"])
            folder_items.append(folder_obj)

        # Create all lightplan objects
        for lightplan in lightplans:
            folder_obj = LightPlanTreeItem(lightplan["song_title"], TreeItemType.LIGHTPLAN)
            folder_obj.setEditable(False)
            folder_obj.setData(lightplan["song_title"], Qt.DisplayRole)
            folder_obj.setData(lightplan, Qt.UserRole)
            folder_obj.setIcon(self.lightplan_icon)
            folder_obj.setParentId(lightplan["folder_id"])
            folder_obj.setArtist(lightplan["song_artist"])
            folder_obj.setTitle(lightplan["song_title"])
            folder_obj.setId(lightplan["lightplan_id"])
            lightplan_items.append(folder_obj)

        # Add the lightplans to the treeview
        for item in lightplan_items:
            #Find the artist parent
            artist_item = None
            for ai in artist_items:
                if ai.artist == item.artist and ai.parent_id == item.parent_id:
                    artist_item = ai
                    break
            if not artist_item:
                #Create artist item if it doesnt exist
                artist_item = LightPlanTreeItem(item.artist, TreeItemType.ARTIST)
                artist_item.setArtist(item.artist)
                artist_item.setTitle(item.title)
                artist_item.setParentId(item.parent_id)
                artist_item.setEditable(False)
                artist_items.append(artist_item)
            artist_item.appendRow(item)

        # Create the hierarchy of folders
        for folder in folder_items:
            if folder.parent_id == 0:
                #Root Item
                self.lp_tree_model.appendRow(folder)
            else:
                #Find parent item and the folder to it
                for x in range(0, len(folder_items)):
                    if folder_items[x].id == folder.parent_id:
                        print(f"Adding item to parent ({folder_items[x].id}) : {folder.id}")
                        folder_items[x].appendRow(folder)

        # Add the artist items to the tree model
        for artist_item in artist_items:
            if artist_item.parent_id == 0:
                self.lp_tree_model.appendRow(artist_item)
            else:
                for x in range(0, len(folder_items)):
                        if folder_items[x].id == artist_item.parent_id:
                            folder_items[x].appendRow(artist_item)

        #Re-expand previously expanded items
        for expanded_item in expanded:
            for item in folder_items:
                if item.id == expanded_item.id and item.parent_id == expanded_item.parent_id:
                    index = self.lp_tree_model.indexFromItem(item)
                    print(f"Re-expanding folder ({item.name})")
                    self.lp_tree_view.expand(index)
            for item in artist_items:
                if item.artist == expanded_item.artist and item.parent_id == expanded_item.parent_id:
                    index = self.lp_tree_model.indexFromItem(item)
                    print(f"Re-expanding artist ({item.name})")
                    self.lp_tree_view.expand(index)

    def get_expanded_tree_objs(self):
        expanded = []
        indexes = self.lp_tree_model.persistentIndexList()
        for index in indexes:
            if(self.lp_tree_view.isExpanded(index)):
                item = self.lp_tree_model.item(index.row())
                expanded.append(item)
        return expanded
                    
    def lp_tree_doubleclicked(self):
        index = self.lp_tree_view.selectedIndexes()[0]
        selected = index.model().itemFromIndex(index)
        if selected.get_type() == TreeItemType.LIGHTPLAN:
            self.open_lp(selected.id)

    def lp_tree_createroot_clicked(self):
        response = QInputDialog.getText(self, "Create Top Level Folder", "Folder Name:", QLineEdit.Normal, "")
        if response[1]:
            self.lightplan_db.create_folder(0, response[0])
            self.update_lightplan_explorer()

    def lptree_show_context_menu(self):
        lp_tree_context_menu = QMenu(self.lp_tree_view)
        lp_tree_context_menu.addAction(self.lp_tree_context_createroot_action)
        indexes = self.lp_tree_view.selectedIndexes()

        # No Item Selected
        if len(indexes) == 0:
            lp_tree_context_menu.popup(QCursor.pos())
            return

        item = self.lp_tree_model.itemFromIndex(indexes[0])
        
        # If not top level item, add Create action
        if item.parent_id != 0 or item.get_type() == TreeItemType.FOLDER:
            if item.get_type() == TreeItemType.FOLDER:
                parent_folder = self.lightplan_db.fetch_folder(item.id)
            else:
                parent_folder = self.lightplan_db.fetch_folder(item.parent_id)
            if parent_folder:
                self.lp_tree_context_create_action.setText(f"Create Folder In [{parent_folder['name']}]")
            else:
                self.lp_tree_context_create_action.setText(f"Create Folder Here")
            lp_tree_context_menu.addAction(self.lp_tree_context_create_action)

        type_str = str(item.get_type())

        # Add move action
        lp_tree_context_menu.addSeparator()

        # Temporarily disable moving whole artists
        self.lp_tree_context_move_action.setEnabled(item.get_type() != TreeItemType.ARTIST)
        
        self.lp_tree_context_move_action.setText(f"Move {type_str} [{item.name}]")
        lp_tree_context_menu.addAction(self.lp_tree_context_move_action)

        # If Folder, add rename option
        if item.get_type() == TreeItemType.FOLDER:
            lp_tree_context_menu.addSeparator()
            self.lp_tree_context_rename_action.setText(f"Rename {type_str} [{item.name}]")
            lp_tree_context_menu.addAction(self.lp_tree_context_rename_action)

        # Lastly but not leastily add delete action
        lp_tree_context_menu.addSeparator()
        self.lp_tree_context_delete_action.setText(f"Delete {type_str} [{item.name}]")
        lp_tree_context_menu.addAction(self.lp_tree_context_delete_action)
        lp_tree_context_menu.popup(QCursor.pos())

    def lp_tree_rename_clicked(self):
        indexes = self.lp_tree_view.selectedIndexes()
        if len(indexes) == 0:
            return
        item = self.lp_tree_model.itemFromIndex(indexes[0])
        if item.get_type() != TreeItemType.FOLDER:
            return
        response = QInputDialog.getText(self, "Rename Folder", "Folder Name:", QLineEdit.Normal, "")
        if response[1]:
            self.lightplan_db.rename_folder(item.id, response[0])
            self.update_lightplan_explorer()

    def lp_tree_move_clicked(self):
        indexes = self.lp_tree_view.selectedIndexes()
        if len(indexes) == 0:
            return
        item = self.lp_tree_model.itemFromIndex(indexes[0])
        self.log(f"Move Clicked on Item {item.name}", LogLevel.DEBUG)
        self.show_move_dialog(item)

    def lp_tree_create_clicked(self):
        indexes = self.lp_tree_view.selectedIndexes()
        parent_id = 0
        if len(indexes) == 0:
            return
        item = self.lp_tree_model.itemFromIndex(indexes[0])
        if item.get_type() == TreeItemType.FOLDER:
            #If item is a folder, the item becomes the parent of the new folder
            parent_id = item.id
        else:
            #if item is not a folder, new folder's parent is same as item's parent
            parent_id = item.parent_id
        response = QInputDialog.getText(self, "Create Folder", "Folder Name:", QLineEdit.Normal, "")
        if response[1]:
            self.lightplan_db.create_folder(parent_id, response[0])
            self.update_lightplan_explorer()

    def lp_tree_delete_clicked(self):
        indexes = self.lp_tree_view.selectedIndexes()
        if len(indexes) == 0:
            return
        item = self.lp_tree_model.itemFromIndex(indexes[0])
        if item.get_type() == TreeItemType.FOLDER:
            msg = f"Are you sure you want to delete folder {item.name}?\n\nThis will also delete any subfolders and LightPlans in the folder. This action cannot be undone!"
        elif item.get_type() == TreeItemType.LIGHTPLAN:
            msg = f"Are you sure you want to delete LightPlan {item.artist} - {item.title}?\n\n This action cannot be undone!"
        else:
            return
        
        choice = QMessageBox.question(self, 
            "LightPlan Studio",
            msg,
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            if item.get_type() == TreeItemType.FOLDER:
                if self.lightplan_db.delete_folder(item.id):
                    self.log(f"Deleted Folder {item.name}")
            elif item.get_type() == TreeItemType.LIGHTPLAN:
                if self.lightplan_db.delete_lightplan(item.id):
                    self.log(f"Deleted LightPlan {item.artist} - {item.title}")
            else:
                #Handle deleting an artist
                pass
            self.update_lightplan_explorer()

    def clear_lightplan(self):
        self.lp_songtitle_edit.clear()
        self.lp_artist_edit.clear()
        self.lp_author_edit.clear()
        self.lp_sslid_edit.clear()
        self.lp_spotifyid_edit.clear()
        self.lp_youtubeurl_edit.clear()
        self.lp_notes_edit.clear()
        self.start_event_edit.setText(msToStr(0, True))
        self.lp_table_model.clear_events()
        self.update_progressbar()

    def new_lp_clicked(self):
        if(self.checkLightPlanUpdated()):
            ret = QMessageBox.question(self, "LightPlan Studio",
                "The LightPlan has been modified.\nDo you want to save your changes?",
                QMessageBox.Save, 
                QMessageBox.Discard)
            if(ret == QMessageBox.Save):
                if(self.save_light_plan()):
                    QMessageBox.information(self, "LightPlan Studio", "LightPlan Saved")
        self.clear_lightplan()
        self.current_lightplan["lightplan"] = self.lightplan_gui_to_dict()
        self.current_lightplan["id"] = None
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()
        self.set_status("New LightPlan")

    ## Show Loading Gif ###
    def loading(self, show=True):
        if(show):
            self.loading_dialog.show()
        else:
            self.loading_dialog.hide()
    
    ## LightPlan File Functions ##
    def import_lightplans(self):
        files = QFileDialog.getOpenFileNames(self, "Import LightPlans", self.lightplan_dir, "LightPlans (*.plan)")
        if(files):
            target_folder = self.get_folder_selection()
            if not target_folder:
                target_folder = {
                    "folder_id": 0,
                    "parent_id": 0,
                    "name": ""
                }
            for f in files[0]:
                self.log(f"Importing LightPlan {f}", LogLevel.DEBUG)
                with open(f) as plan:
                    lp = json.load(plan)
                    result = self.lightplan_db.insert_lightplan(lp, target_folder["folder_id"])
                    if(result):
                        self.log(f"Created Lightplan with Id: {result}", LogLevel.DEBUG)

    def check_save_lightplan(self):
        if(self.checkLightPlanUpdated()):
            ret = QMessageBox.question(self, "LightPlan Studio",
                "The LightPlan has been modified.\nDo you want to save your changes?",
                QMessageBox.Save, 
                QMessageBox.Discard)
            if(ret == QMessageBox.Save):
                if(self.save_light_plan()):
                    QMessageBox.information(self, "LightPlan Studio", "LightPlan Saved")

    def show_file_dialog(self):
        file_name = QFileDialog.getOpenFileName(self, "Open LightPlan", self.lightplan_dir, "LightPlans (*.plan)")
        if(file_name):
            self.open_lp(file_name[0])
        self.log(f"Opening LightPlan File: {file_name}")

    def open_lp(self, lp_id):
        lightplan_dict = None
        lightplan_dict = self.lightplan_db.fetch_lightplan(lp_id)
        if not lightplan_dict:
            self.log(f"Error fetching LightPlan with Id: {lp_id}", LogLevel.ERROR)
            return
        self.clear_lightplan()
        self.lp_songtitle_edit.setText(lightplan_dict["song_title"])
        self.lp_artist_edit.setText(lightplan_dict["song_artist"])
        self.lp_author_edit.setText(lightplan_dict["author"])
        ssl_id = str(lightplan_dict["ssl_id"])
        if ssl_id == "0":
            ssl_id = ""
        spotify_id = str(lightplan_dict["spotify_id"])
        if spotify_id == "0":
            spotify_id = ""
        self.lp_sslid_edit.setText(ssl_id)
        self.lp_spotifyid_edit.setText(spotify_id)
        self.lp_youtubeurl_edit.setText(lightplan_dict["video_url"])
        self.lp_notes_edit.setPlainText(lightplan_dict["notes"])
        self.start_event_edit.setText(msToStr(lightplan_dict["starting_ms"], True))
        self.lp_table_model.clear_events()
        for evt in lightplan_dict["events"]:
            evt_obj = LightPlanEvent(evt["offset"],evt["command"],evt["comment"],valueToBool(evt["ignore_delay"]))
            self.lp_table_model.insert_event(evt_obj)
        self.current_lightplan = {
            "id": lightplan_dict["lightplan_id"],
            "folder_id": lightplan_dict["folder_id"],
            "md5": hashlib.md5(str(lightplan_dict).encode("utf-8")).hexdigest(),
            "lightplan": lightplan_dict
        }
        self.log(f"Opened LightPlan {self.current_lightplan['id']}", LogLevel.DEBUG)
        self.log(f"{self.current_lightplan['lightplan']['song_artist']} - {self.current_lightplan['lightplan']['song_title']}", LogLevel.INFO)
        self.update_progressbar()
        self.set_status(f"{self.current_lightplan['lightplan']['song_artist']} - {self.current_lightplan['lightplan']['song_title']}")

    def checkLightPlanUpdated(self):
        lp = self.lightplan_gui_to_dict()
        return hashlib.md5(str(lp).encode("utf-8")).hexdigest() != self.current_lightplan["md5"]

    def lightplan_gui_to_dict(self):
        self.lp_table_model.sort(0,Qt.AscendingOrder)
        lightplan_dict = {
            "lightplan_id": self.current_lightplan["id"],
            "folder_id": self.current_lightplan["folder_id"],
            "song_title": "",
            "song_artist": "",
            "author": "",
            "ssl_id": 0,
            "spotify_id": 0,
            "video_url": "",
            "notes": "",
            "starting_ms": 0,
            "events": []
        }
        lightplan_dict["song_title"] = self.lp_songtitle_edit.text().strip()
        lightplan_dict["song_artist"] = self.lp_artist_edit.text().strip()
        lightplan_dict["author"] = self.lp_author_edit.text().strip()
        try:
            ssl_id = int(self.lp_sslid_edit.text().strip(), 10)
        except ValueError as ve:
            ssl_id = 0
        try:
            spotify_id = int(self.lp_spotifyid_edit.text().strip(), 10)
        except ValueError as ve:
            spotify_id = 0
        lightplan_dict["ssl_id"] = ssl_id
        lightplan_dict["spotify_id"] = spotify_id
        lightplan_dict["video_url"] = self.lp_youtubeurl_edit.text().strip()
        lightplan_dict["notes"] = self.lp_notes_edit.toPlainText().strip()
        lightplan_dict["starting_ms"] = strToMs(self.start_event_edit.text().strip())
        lightplan_dict["events"] = self.lp_table_model.exportJsonDict()
        lightplan_dict["lightplan_id"] = self.current_lightplan["id"]
        return lightplan_dict
    
    def save_light_plan(self):
        self.current_lightplan["lightplan"] = self.lightplan_gui_to_dict()
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()
        if(len(self.current_lightplan["lightplan"]["song_title"].strip())==0 or len(self.current_lightplan["lightplan"]["song_artist"].strip())==0):
            QMessageBox.warning(self, "LightPlan Studio", "Song Artist and Title are required.")
            return False
        if(self.current_lightplan["id"] is None):
            #If new LightPlan, insert into DB and get ID
            id = self.lightplan_db.insert_lightplan(self.current_lightplan["lightplan"])
            if id:
                self.current_lightplan["id"] = id
                self.current_lightplan["lightplan"]["lightplan_id"] = id
                self.log(f"Saved LightPlan id = {id}", LogLevel.INFO)
                self.set_status("LightPlan Saved", 2500)
            else:
                self.log("Error saving LightPlan", LogLevel.ERROR)
        else:
            #Existing LightPlan - just update
            if self.lightplan_db.update_lightplan(self.current_lightplan["lightplan"]):
                self.log(f"Saved LightPlan id = {self.current_lightplan['id']}", LogLevel.INFO)
                self.set_status("LightPlan Saved", 2500)
            else:
                self.log("Error saving LightPlan", LogLevel.ERROR)
        self.update_lightplan_explorer()
        return True

    def click_save_button(self):
        if self.checkLightPlanUpdated():
            if(self.save_light_plan()):
                self.log("LightPlan Saved")
                self.log(self.current_lightplan["md5"], LogLevel.DEBUG)
        else:
            self.log("LightPlan not changed", LogLevel.DEBUG)
            self.log(self.current_lightplan["md5"], LogLevel.DEBUG)

    def get_lp_basename(self, artist, title, extension="plan"):
        keepcharacters = (' ','.','_',"-")
        file_name = f"{artist} - {title}"
        file_name = "".join(c for c in file_name if c.isalnum() or c in keepcharacters).rstrip()
        return f"{file_name}.{extension}"

    def hash_str(self, value, length=16):
        if(length>32 or length<1):
            length=32
        hash = hashlib.md5(value.encode("UTF-8")).hexdigest()
        return hash[:length]

    def update_progressbar(self, left=None, right=None, roles=None):
        num_events = self.lp_table_model.rowCount()
        if(num_events <= 0):
            self.control_lp_progressbar.setTextVisible(False)
            self.control_lp_progressbar.setMaximum(1)
        else:
            if(self.control_lp_progressbar.isTextVisible()==False):
                self.control_lp_progressbar.setTextVisible(True)
            self.control_lp_progressbar.setMaximum(num_events)
        self.control_lp_progressbar.setFormat("LightPlan Event %v/%m")

    ## LightPlan Runner Functions ##

    def click_start_lightplan(self):
        #LightPlan Not Running - Start It
        if(self.lightplan_runner is None or self.lightplan_runner.is_running() == False):
            self.lp_songtitle_edit.setEnabled(False)
            self.lp_artist_edit.setEnabled(False)
            self.lp_author_edit.setEnabled(False)
            self.lp_sslid_edit.setEnabled(False)
            self.lp_spotifyid_edit.setEnabled(False)
            self.lp_youtubeurl_edit.setEnabled(False)
            self.lp_notes_edit.setEnabled(False)
            self.start_event_edit.setEnabled(False)
            self.event_table_view.setEnabled(False)
            self.load_song_button.setEnabled(False)
            self.insert_event_button.setEnabled(False)
            self.set_delay_button.setEnabled(False)
            self.calc_delay_button.setEnabled(False)
            self.twitch_connect_button.setEnabled(False)
            self.action_new_lp.setEnabled(False)
            self.action_open_lp.setEnabled(False)
            self.action_save_lp.setEnabled(False)
            self.action_settings.setEnabled(False)
            self.action_help_about.setEnabled(False)
            self.action_help_oauth.setEnabled(False)
            self.action_help_docs.setEnabled(False)
            self.action_help_checkcmds.setEnabled(False)
            self.event_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
            lp = self.lightplan_gui_to_dict()
            self.control_lp_progressbar.setValue(0)
            self.lightplan_runner = LightPlanRunner(lp, self.stream_delay_ms, self.delay_adjust_ms)
            self.lightplan_runner.signals.log.connect(self.log)
            self.lightplan_runner.signals.done.connect(self.lightplan_runner_done)
            self.lightplan_runner.signals.progress.connect(self.lightplan_runner_progress)
            self.lightplan_runner.signals.privmsg.connect(self.privmsg)
            self.threadpool.start(self.lightplan_runner)
            self.lightplan_start_timer.start(0.2)
            self.lightplan_start_time = time.time()
            self.next_event_secs = 0
            self.set_status("LightPlan Started", 2500)
            self.control_startlp_button.setText("Stop LightPlan")
        else:
            #LightPlan Already Running - Stop It
            self.lightplan_runner.stop()
            self.control_startlp_button.setText("Start LightPlan")

    def lightplan_runner_done(self, msg="LightPlan Stopped"):
        self.lp_songtitle_edit.setEnabled(True)
        self.lp_artist_edit.setEnabled(True)
        self.lp_author_edit.setEnabled(True)
        self.lp_sslid_edit.setEnabled(True)
        self.lp_spotifyid_edit.setEnabled(True)
        self.lp_youtubeurl_edit.setEnabled(True)
        self.lp_notes_edit.setEnabled(True)
        self.start_event_edit.setEnabled(True)
        self.event_table_view.setEnabled(True)
        self.load_song_button.setEnabled(True)
        self.insert_event_button.setEnabled(True)
        self.set_delay_button.setEnabled(True)
        self.twitch_connect_button.setEnabled(True)
        self.calc_delay_button.setEnabled(True)
        self.action_new_lp.setEnabled(True)
        self.action_open_lp.setEnabled(True)
        self.action_save_lp.setEnabled(True)
        self.action_settings.setEnabled(True)
        self.action_help_about.setEnabled(True)
        self.action_help_oauth.setEnabled(True)
        self.action_help_docs.setEnabled(True)
        self.action_help_checkcmds.setEnabled(True)
        self.control_nextevent_label.clear()
        self.control_lpelapsed_label.setText("00:00")
        self.control_lp_progressbar.setValue(0)
        self.event_table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)
        self.lightplan_start_timer.stop()
        self.control_startlp_button.setChecked(False)
        self.control_startlp_button.setText("Start LightPlan")
        self.delay_adjust_spinner.setValue(0)
        self.delay_adjust_slider.setValue(0)
        self.set_status(msg, 2500)

    def lightplan_runner_progress(self, cur_evt_num, next_event_secs, next_event, original_index):
        self.next_event_secs = next_event_secs
        self.control_nextevent_label.setText(next_event)
        self.control_lp_progressbar.setValue(cur_evt_num)
        if(original_index >= 0 and original_index < len(self.lp_table_model.events)):
            self.event_table_view.selectRow(original_index)
            self.lp_table_model.scrollToRow(original_index)
        else:
            self.event_table_view.selectRow(0)
            self.lp_table_model.scrollToRow(0)
            
    def update_lightplan_elapsed(self):
        elapsed = time.time()-self.lightplan_start_time
        target = self.next_event_secs - elapsed
        if(target >= 0):
            self.control_lpelapsed_label.setText(secsToStr(target))

    ## Twitch Chat Functions ##

    def privmsg(self, msg):
        if(self.twitch and self.twitch.connected()):
            self.twitch.privmsg(msg)

    def click_twitch_connect_button(self):
        if(self.twitch and self.twitch.connected()):
            self.twitch.die()
            self.twitch_connect_button.setChecked(False)
            if(self.streamer_song_list.connected()):
                self.streamer_song_list.disconnect()
        else:
            user_name = self.settings.value("Twitch/Username", "")
            token = self.settings.value("Twitch/OAuthToken", "")
            channel = self.settings.value("Twitch/Channel", "")
            self.twitch = TwitchIRC(user_name, token, channel)
            self.twitch.signals.log.connect(self.log)
            self.twitch.signals.irc_disconnect.connect(self.twitch_disconnect)
            self.twitch.signals.irc_connect.connect(self.twitch_connect)
            self.twitch.signals.connect_failed.connect(self.twitch_connect_failed)
            self.threadpool.start(self.twitch)
            self.twitch_connect_button.setChecked(True)
            self.check_start_ssl_connection()

    def twitch_connect(self):
        self.twitch_connect_button.setText("Disconnect Twitch")
        self.calc_delay_button.setEnabled(True)
        self.control_startlp_button.setEnabled(True)
        self.twitch_connect_button.setChecked(True)
        self.connected_label.setHidden(False)

    def twitch_disconnect(self):
        self.twitch_connect_button.setText("Connect Twitch")
        self.calc_delay_button.setEnabled(False)
        self.control_startlp_button.setEnabled(False)
        self.twitch_connect_button.setChecked(False)
        self.connected_label.setHidden(True)

    def twitch_connect_failed(self):
        choice = QMessageBox.warning(self, 
            "LightPlan Studio", 
            "Twitch IRC Connection Failed.\n\nDo you want to try again?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.Yes)
        if(choice == QMessageBox.StandardButton.Yes):
            self.click_twitch_connect_button()

    ## Event Wizard Functions ##

    def insert_event(self):
        pos = self.audio_player.position()
        evt = LightPlanEvent(pos)
        self.lp_table_model.insert_event(evt)
        self.update_progressbar()
        
    def load_youtube(self):
        url = self.lp_youtubeurl_edit.text().strip()
        if(len(url)==0):
            self.log("No Youtube URL Specified")
            choice = QMessageBox.information(self, "Load Video", 
                "No Youtube URL spectified. Would you like to load an local mp4 file instead?",
                (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
                QMessageBox.StandardButton.Yes)
            if(choice == QMessageBox.StandardButton.No):
                return
            else:
                file_name = QFileDialog.getOpenFileName(self, "Load MP4 File", self.documents_dir, "MP4 Video (*.mp4)")
                if(len(file_name[0]) > 0 and os.path.exists(file_name[0])):
                    self.log(f"Loading Local MP4 File: {file_name[0]}")
                    data = {
                        "audio_path": file_name[0],
                        "image_path": ""
                    }
                    self.download_complete(True, data)
                    return
        self.loading()
        #Check if youtube url is region blocked
        if "youtube.com/watch?v=" in url:
            parts = url.split("v=")
            if len(parts) == 2:
                parts = parts[1].split("&")
                self.log(f"Looking Up Video Info for ID: {parts[0]}", LogLevel.DEBUG)
                yti = YoutubeVideoInfo(self.youtube_api_key, parts[0])
                yti.signals.log.connect(self.log)
                yti.signals.done.connect(self.youtube_region_check)
                self.threadpool.start(yti)
        filename = self.hash_str(url)+".mp4"
        audio_path = os.path.join(self.audio_dir, filename).replace("\\", "/")
        if(not os.path.exists(audio_path)):
            self.song_slider.setEnabled(False)
            self.play_button.setEnabled(False)
            self.insert_event_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.current_time_lcd.display("00:00.000")
            url = self.lp_youtubeurl_edit.text()
            yt = YoutubeDownloader(url, self.audio_dir, filename)
            yt.signals.log.connect(self.log)
            yt.signals.done.connect(self.download_complete)
            self.threadpool.start(yt)
        else:
            data = {
                "audio_path": audio_path,
                "image_path": ""
            }
            self.log("Youtube Audio Loaded From Cache")
            self.log(audio_path, LogLevel.DEBUG)
            self.download_complete(True, data)

    def download_complete(self, result, data=None):
        if(not result):
            self.song_loaded_status_label.setText("No Song Loaded")
            return
        self.song_file_path = data["audio_path"]
        self.song_image_path = data["image_path"]
        #self.audio_player.setSource(self.song_file_path)
        self.audio_player.setSource(QUrl.fromLocalFile(self.song_file_path))
        self.position_ms = 0
        self.song_loaded = True
        self.song_slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.insert_event_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.song_loaded_status_icon.setPixmap(self.check_icon.pixmap(self.song_loaded_status_icon.width(), self.song_loaded_status_icon.height()))
        filename = os.path.basename(self.song_file_path)
        self.song_loaded_status_label.setText(f"File Loaded Successfully")
        self.set_status(f"File Loaded Successfully", 3000)
        self.loading(False)
        
    def song_slider_released(self):
        if(self.seek_position_ms != self.position_ms):
            self.audio_player.setPosition(int(self.seek_position_ms))
        if(self.resume_on_release):
            self.audio_player.play()
            self.resume_on_release = False
    
    def song_slider_pressed(self):
        self.seek_position_ms = self.position_ms
        if(self.audio_player.playbackState() == QMediaPlayer.PlayingState):
            self.resume_on_release = True
            self.audio_player.pause()
            
    def song_slider_moved(self):
        slider = self.song_slider.value()
        percent = slider / self.song_slider.maximum()
        self.seek_position_ms = self.duration_ms * percent
        self.current_time_lcd.display(msToStr(self.seek_position_ms, True))
        
    @Slot(QMediaPlayer.Error, str)
    def audio_player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.log(error_string, LogLevel.ERROR)
        ret = QMessageBox.warning(self, "Error", error_string)
    
    def durationChanged(self):
        self.duration_ms = self.audio_player.duration()
    
    def playbackStateChanged(self):
        if(self.audio_player.playbackState() == QMediaPlayer.PlayingState):
            self.key_listener = KeyListener()
            self.key_listener.signals.key_event.connect(self.insert_event)
            self.key_listener.signals.log.connect(self.log)
            self.threadpool.start(self.key_listener)
            self.insert_event_button.setText("Insert Event (Space Bar)")
            self.play_button.setIcon(self.pause_icon)
        else:
            if(self.key_listener):
                self.key_listener.die()
            self.play_button.setIcon(self.play_icon)
            self.insert_event_button.setText("Insert Event")
        
    def positionChanged(self):
        if(self.duration_ms == 0):
            return
        self.position_ms = self.audio_player.position()
        percent = (self.position_ms / self.duration_ms) * 1000
        self.song_slider.setValue(percent)
        self.current_time_lcd.display(msToStr(self.position_ms, True))
        
    def click_play_button(self):
        if(self.audio_player.playbackState() == QMediaPlayer.PlayingState):
            self.audio_player.pause()
        else:
            self.audio_player.play()
            self.insert_event_button.setFocus(Qt.TabFocusReason)
            
    def click_stop_button(self):
        self.current_time_lcd.display("00:00.000")
        self.song_slider.setValue(0)
        if(self.audio_player.playbackState() != QMediaPlayer.StoppedState):
            self.audio_player.stop()

    def volume_changed(self):
        self.volume = self.volume_slider.value()
        self.audio_output.setVolume(self.volume/100.00)

    def volume_change_event(self):
        self.volume = self.volume_slider.value()
        self.log(f"Volume Set {self.volume}%", LogLevel.INFO)
        self.set_status(f"Volume Set {self.volume}%", 2000)

    ## End Event Wizard Functions ##
    
    def click_set_start_event(self):
        cur_start = self.start_event_edit.text()
        if(cur_start != "00:00.000"):
            ret = QMessageBox.question(self, "LightPlan Studio", "A starting event has already been set. Want to overwrite it?", buttons=(QMessageBox.Ok | QMessageBox.Cancel))
            if(ret == QMessageBox.Cancel):
                return
        start_evt = self.lp_table_model.click_delete_event()
        self.start_event_edit.setText(msToStr(start_evt.offset_ms, True))
        warning = False
        for evt in self.lp_table_model.events:
            if(evt.offset_ms < start_evt.offset_ms):
                QMessageBox.warning(self, "LightPlan Studio", """It appears that there are one or more 
                    events that occur before the starting event. These events will fire 
                    immediately at the start of the LightPlan if not changed.""")

    def delay_spinner_changed(self, val):
        self.delay_adjust_ms = int(round(val*1000,0))
        if(self.lightplan_runner is not None):
            self.lightplan_runner.update_runtime_adjustment(self.delay_adjust_ms)
        self.log(f"Stream Delay Adjustment: {self.delay_adjust_ms} ms", LogLevel.DEBUG)

    def delay_slider_moved(self):
        val = self.delay_adjust_slider.value()
        self.delay_adjust_spinner.setValue(round(val/1000,1))
        self.delay_adjust_ms = val

    def delay_slider_released(self):
        self.log(f"Stream Delay Adjustment: {self.delay_adjust_ms} ms", LogLevel.DEBUG)
    
    ## More Functions ##

    def get_commands(self):
        custom_cmds_json = self.settings.value("LightPlanStudio/CustomCmds", "[]")
        try:
            self.custom_cmds = json.loads(custom_cmds_json)
        except json.decoder.JSONDecodeError as e:
            self.log("JSONDecodeError parsing custom commands", LogLevel.ERROR)
            self.log(str(e), LogLevel.DEBUG)
            self.custom_cmds = []
        all_commands = self.custom_cmds + self.defaultCommands
        return all_commands

    def click_hidelog_button(self):
        self.setFixedSize(self.defaultWidth, self.height)
        self.action_show_log.setChecked(False)
    
    def toggle_logvisible(self):
        if(self.action_show_log.isChecked()):
            self.setFixedSize(self.expandedWidth, self.height)
        else:
            self.setFixedSize(self.defaultWidth, self.height)
    
    def status_msg_changed(self, text):
        if(len(text)==0):
            self.set_status(self.status_msg)

    def set_status(self, msg, timeout=0):
        if(timeout==0):
            self.status_msg = msg
        self.statusbar.showMessage(msg, timeout)

    def fetch_commands(self):
        url = "https://lightplanstudio.com/api/commands.json"
        self.log(f"Requesting updated light commands {url}", LogLevel.DEBUG)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
        try:
            r = requests.get(url, headers=headers)
            self.log(f"HTTP Status Code {r.status_code}", LogLevel.DEBUG)
            if(r.status_code==200):
                return r.json()
            self.log("Could not fetch light commands!", LogLevel.ERROR)
            self.log(r.text, LogLevel.ERROR)
        except Exception as e:
            self.log("Error requesting updated commands", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
        return None

    def show_ssl_match_dialog(self):
        search = self.lp_artist_edit.text() + " " + self.lp_songtitle_edit.text()
        user = self.settings.value("Twitch/Channel", "").strip()
        ssl_id = 0
        if not self.streamer_song_list.sslId_from_user(user):
            self.log(f"Could not map user [{user}] to ssl id", LogLevel.ERROR)
            QMessageBox.warning(self, "LightPlan Studio", f"Could not match Twitch User ({user}) to SSL ID")
            return
        dlg = SSLMatchDialog(self, self.threadpool, self.streamer_song_list.ssl_id, user, search)
        dlg.signals.log.connect(self.log)
        result = dlg.exec()
        if(result == QDialog.Accepted):
            if dlg.selection:
                self.log(f"Match SSL ID {dlg.selection}", LogLevel.INFO)
                self.lp_sslid_edit.setText(str(dlg.selection))

    #Menu > Settings
    def show_settings_dialog(self):
        dlg = SettingsDialog(self.default_lightplan_dir, self)
        dlg.signals.log.connect(self.log)
        dlg.setSettings(self.settings)
        result = dlg.exec()
        if(result == QDialog.Accepted):
            #Save Settings
            self.settings = dlg.settings
            self.log_level = dlg.log_level
            self.lightplan_dir = self.settings.value("LightPlanStudio/LightPlanDir", self.default_lightplan_dir)
            #self.checkStartSSLIntegration()
            self.reset_fswatcher()
            self.lp_table_model.update_commands(self.get_commands())
            self.set_status("Settings Saved", 2500)
            self.log("Settings Saved")
    
    def check_showlog(self):
        checked = valueToBool(self.settings.value("LightPlanStudio/ShowLogOnStart", False))
        self.action_show_log.setChecked(checked)
        if checked:
            self.setFixedSize(self.expandedWidth, self.height)
        else:
            self.setFixedSize(self.defaultWidth, self.height)

    def set_delay_dialog(self):
        delay_secs, result = QInputDialog.getDouble(self, "Set Stream Delay", "Stream Delay Seconds:", 0, 0, 9999, 3)
        if(result):
            self.stream_delay_ms = int(delay_secs*1000)
            self.delay_lcd.display(str(round(delay_secs, 2)))
            self.log(f"Stream Delay Set: {self.stream_delay_ms} ms")

    def show_calc_delay_dialog(self):
        dlg = CalcDelayDialog(self, self.twitch)
        dlg.signals.log.connect(self.log)
        result = dlg.exec()
        if(result == QDialog.Accepted):
            self.stream_delay_ms = dlg.delay
            self.delay_lcd.display(str(round(self.stream_delay_ms/1000, 1)))
            self.log(f"Stream Delay: {self.stream_delay_ms}ms")

    def get_folder_selection(self):
        folders = self.lightplan_db.fetch_all_folders()
        dlg = ItemMoveDialog(None, folders, self)
        dlg.signals.log.connect(self.log)
        result = dlg.exec()
        if(result == QDialog.Accepted and dlg.selected_folder):
            return dlg.selected_folder
        return None
        
    def show_move_dialog(self, selected_item):
        folders = self.lightplan_db.fetch_all_folders()
        dlg = ItemMoveDialog(selected_item, folders, self)
        dlg.signals.log.connect(self.log)
        result = dlg.exec()
        if(result == QDialog.Accepted):
            if dlg.selected_folder:
                self.log(f"Moving Item {selected_item.name} to folder {dlg.selected_folder['name']}")
                if selected_item.get_type() == TreeItemType.FOLDER:
                    self.lightplan_db.move_folder(selected_item.id, dlg.selected_folder["folder_id"])
                else:
                    self.lightplan_db.move_lightplan(selected_item.id, dlg.selected_folder["folder_id"])
            self.update_lightplan_explorer()

    def closeEvent(self, evt):
        self.check_save_lightplan()
        if(self.key_listener):
            self.key_listener.die()
        if(self.twitch and self.twitch.connected()):
            self.twitch.die()
        if(self.lightplan_runner is not None and self.lightplan_runner.is_running()):
            self.lightplan_runner.stop()
        if(self.streamer_song_list.connected()):
            self.streamer_song_list.disconnect()
        # Save Window Geometry
        self.settings.setValue("LightPlanStudio/geometry", self.saveGeometry())
        self.settings.setValue("LightPlanStudio/windowState", self.saveState())
        self.settings.sync()
        return evt.accept()
    
    def get_parent_dir(self, path_str):
        dir_path = os.path.dirname(path_str)
        if(dir_path):
            dir = os.path.basename(dir_path)
            return dir
        return None
        
    def log(self, msg, level=LogLevel.INFO):
        if(not msg or level.value > self.log_level.value):
            return
        if(level == LogLevel.ERROR):
            style = "color: #cc0000;"
        elif(level == LogLevel.DEBUG):
            style = "color: #006600;"
            print(msg)
        else:
            style = "color: #000000;"
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        msg = f'<span style="{style}">{timestamp} - {msg}</span>'
        self.debug_log_edit.append(msg)

class ItemMoveDialog(QDialog):
    class Signals(QObject):
        log = Signal(str, LogLevel)
    
    def __init__(self, item, folders, parent=None):
        super().__init__(parent)
        self.selected_folder = None
        self.signals = self.Signals()
        self.ui = UI.Ui_ItemMoveDialog()
        self.ui.setupUi(self)
        self.check = True
        if item:
            if item.get_type() == TreeItemType.LIGHTPLAN:
                self.ui.item_name.setText(f"LightPlan [{item.artist} - {item.title}]")
            elif item.get_type() == TreeItemType.ARTIST:
                self.ui.item_name.setText(f"Artist [{item.name}]")
            elif item.get_type() == TreeItemType.FOLDER:
                self.ui.item_name.setText(f"Folder [{item.name}]")
            else:
                self.ui.item_name.setText(f"{item.name}")
        else:
            self.ui.item_label.setFixedWidth(250)
            self.ui.item_label.setText("Select Folder for Imported LightPlans")
            self.ui.item_name.setVisible(False)
            item = LightPlanTreeItem("None")
            item.setId(0)
            item.setParentId(0)
            self.check = False

        self.item = item
        self.ui.cancel_button.clicked.connect(self.cancel_clicked)
        self.ui.move_button.clicked.connect(self.move_clicked)
        self.ui.folder_widget.setHeaderLabels(["LightPlan Folders"])
        folder_items = []
        root = {
            "folder_id": 0,
            "parent_id": 0,
            "name": "LightPlans"
        }
        folders.insert(0, root)
        for folder in folders:
            item = FolderTreeWidgetItem(folder["name"], folder)
            item.setText(0, folder["name"])
            item.setIcon(0, parent.dir_icon)
            folder_items.append(item)

        for item in folder_items:
            if item.folder_data["folder_id"] == 0:
                continue
            for parent in folder_items:
                if parent.folder_data["folder_id"] == item.folder_data["parent_id"]:
                    parent.addChild(item)

        self.ui.folder_widget.insertTopLevelItems(0, folder_items)
        self.ui.folder_widget.expandAll()

    def move_clicked(self):
        indexes = self.ui.folder_widget.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.ui.folder_widget.itemFromIndex(index)
            if self.check:
                if self.item.get_type() == TreeItemType.FOLDER:
                    if item.folder_data["folder_id"] == self.item.id:
                        QMessageBox.warning(self, "Move Error", "Cannot move a folder into itself.")
                        return
                    if item.folder_data["parent_id"] == self.item.parent_id:
                        QMessageBox.warning(self, f"Move Error", "Folder is already in there!")
                        return
                else:
                    if item.folder_data["folder_id"] == self.item.parent_id:
                        QMessageBox.warning(self, "Move Error", "Item is already in there!")
                        return
            self.selected_folder = item.folder_data
            self.accept()

    def cancel_clicked(self):
        self.reject()

class LoadingDialog(QDialog):

    class Signals(QObject):
        log = Signal(str, LogLevel)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.signals = self.Signals()
        self.ui = UI.Ui_LoadingDialog()
        self.ui.setupUi(self)

    def setMovie(self, movie):
        self.movie = movie
        self.ui.loading_label.setMovie(movie)
        self.movie.start()

class SSLMatchDialog(QDialog):
    
    class RowObj(QTableWidgetItem):
        def __init__(self, text, song=None):
            super(SSLMatchDialog.RowObj, self).__init__(text)
            self.song = song

    class Runner(QRunnable):
        class Signals(QObject):
            done = Signal(list)
            log = Signal(str, LogLevel)

        def __init__(self, ssl_id):
            super(SSLMatchDialog.Runner, self).__init__()
            self.signals = self.Signals()
            self.ssl_id = ssl_id

        def get_all_songs(self, ssl_id):
            url = f"https://api.streamersonglist.com/v1/streamers/{ssl_id}/songs?size=ALL&current=1&showInactive=false&isNew=false&order=asc"
            r = requests.get(url)
            self.log(f"Fetching SSL Songs {url}", LogLevel.DEBUG)
            if(r.status_code==200):
                return r.json()["items"]
            self.log(f"Error Retrieving SSL Songs: HTTP Code {r.status_code}", LogLevel.ERROR)
            return None

        def run(self):
            songs = self.get_all_songs(self.ssl_id)
            self.signals.done.emit(songs)

        def log(self, msg, level = LogLevel.INFO):
            self.signals.log.emit(msg, level)

    class Signals(QObject):
        log = Signal(str, LogLevel)

    def __init__(self, parent, threadpool, ssl_id, ssl_user, search_text):
        super().__init__(parent)
        self.signals = self.Signals()
        self.songs = []
        self.selection = None
        self.ssl_user = ssl_user
        self.ssl_id = ssl_id
        self.search_text = search_text
        self.ui = UI.Ui_SSLMatchDialog()
        self.ui.setupUi(self)
        self.ui.song_table.setHorizontalHeaderLabels(["Artist", "Title"])
        self.ui.song_table.setEnabled(False)
        self.ui.search_edit.setEnabled(False)
        self.ui.label.setEnabled(False)
        self.ui.save_button.clicked.connect(self.save_clicked)
        self.ui.cancel_button.clicked.connect(self.cancel_clicked)
        self.ui.status_label.setText(f"Fetching all songs for user {ssl_user}")
        self.ui.search_edit.setText(search_text)
        self.ui.search_edit.textChanged.connect(self.update_table)
        runner = SSLMatchDialog.Runner(ssl_id)
        runner.signals.done.connect(self.songs_done)
        runner.signals.log.connect(self.log)
        threadpool.start(runner)

    def songs_done(self, songs):
        if not songs:
            self.ui.status_label.setText(f"Error fetching songs for SSL User {self.ssl_user}")
            return
        n = len(songs)
        self.songs = songs
        self.ui.status_label.setText(f"Fetched {n} songs for user {self.ssl_user}")
        self.log(f"Fetched {n} songs for SSL User {self.ssl_user}", LogLevel.INFO)
        self.ui.song_table.setEnabled(True)
        self.ui.search_edit.setEnabled(True)
        self.ui.label.setEnabled(True)
        self.ui.progress.setVisible(False)
        self.update_table()

    def update_table(self):
        search_text = self.ui.search_edit.text()
        filtered = self.filter_songs(self.songs, search_text)
        self.ui.song_table.clearContents()
        self.ui.song_table.setRowCount(0)
        for song in filtered:
            row = self.ui.song_table.rowCount()
            self.ui.song_table.insertRow(row)
            artist_item = SSLMatchDialog.RowObj(song["artist"], song)
            title_item = SSLMatchDialog.RowObj(song["title"], song)
            self.ui.song_table.setItem(row, 0, artist_item)
            self.ui.song_table.setItem(row, 1, title_item)

    def filter_songs(self, songs, filter):
        if not filter:
            return songs
        filtered = []
        filters = filter.lower().split()
        for song in songs:
            target = song["artist"] + " " + song["title"]
            target = unicodedata.normalize("NFC", target)
            target = re.sub("[^A-Za-z0-9! ]*", "", target).lower()
            include = True
            for word in filters:
                if word not in target:
                    include = False
                    break
            if include:
                filtered.append(song)
        return filtered

    def cancel_clicked(self):
        self.reject()

    def save_clicked(self):
        sel = self.ui.song_table.selectedItems()
        if sel and len(sel) > 0:
            self.selection = sel[0].song["id"]
        self.accept()

    def log(self, msg, log_level=LogLevel.DEBUG):
        self.signals.log.emit(msg, log_level)

class CalcDelayDialog(QDialog):
    
    class Signals(QObject):
        log = Signal(str, LogLevel)

    def __init__(self, parent, twitch):
        super().__init__(parent)
        self.ui = UI.Ui_CalcDelayDialog()
        self.ui.setupUi(self)
        self.ui.save_button.clicked.connect(self.save_clicked)
        self.ui.cancel_button.clicked.connect(self.cancel_clicked)
        self.ui.send_button.clicked.connect(self.send_clicked)
        self.ui.stop_button.clicked.connect(self.stop_clicked)
        self.ui.stop_button.setEnabled(False)
        self.signals = self.Signals()
        self.update_frequency_ms = 50
        self.delay = 0
        self.elapsed = 0
        self.start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_update)
        self.ui.delay_lcd.display("00:00.000")
        self.twitch = twitch

    def timer_update(self):
        self.elapsed = time.time()-self.start_time
        display_str = CalcDelayDialog.secToStr(self.elapsed)
        self.ui.delay_lcd.display(display_str)

    def send_clicked(self):
        msg = self.ui.command_combo.currentText()
        if(self.twitch and self.twitch.connected()):
            self.twitch.privmsg(msg)
        self.elapsed = 0
        self.start_time = time.time()
        self.timer.start(self.update_frequency_ms)
        self.ui.send_button.setEnabled(False)
        self.ui.stop_button.setEnabled(True)
        self.ui.save_button.setEnabled(False)
        self.ui.cancel_button.setEnabled(False)

    def stop_clicked(self):
        self.timer.stop()
        self.timer_update()
        self.delay = round(self.elapsed*1000)
        self.ui.send_button.setEnabled(True)
        self.ui.stop_button.setEnabled(False)
        self.ui.save_button.setEnabled(True)
        self.ui.cancel_button.setEnabled(True)

    def cancel_clicked(self):
        self.reject()

    def save_clicked(self):
        self.accept()

    def log(self, msg, log_level=LogLevel.DEBUG):
        self.signals.log.emit(msg, LogLevel.DEBUG)

    @staticmethod
    def secToStr(ms):
        #ms = ms / 1000
        mins, secs = divmod(ms, 60)
        return "{:02d}:{:06.3f}".format(int(mins), secs)

class SettingsDialog(QDialog):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        
    settings = None
    
    def __init__(self, default_dir, parent=None):
        super().__init__(parent)
        
        self.signals = self.Signals()
        
        self.ui = UI.Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.log_level_combo.clear()
        for level in LogLevel:
            self.ui.log_level_combo.addItem(level.name, level)
        self.ui.saveButton.clicked.connect(self.saveButtonClick)
        self.ui.cancelButton.clicked.connect(self.cancelButtonClick)
        self.ui.addCmdButton.clicked.connect(self.addCmdButtonClicked)
        self.ui.editCmdButton.clicked.connect(self.editCmdButtonClicked)
        self.ui.delCmdButton.clicked.connect(self.delCmdButtonClicked)
        self.ui.dir_browse_button.clicked.connect(self.dir_browse_clicked)
        self.ui.dir_default_button.clicked.connect(self.dir_default_clicked)
        self.log_level = LogLevel.INFO
        self.default_dir = default_dir
        # Hide OAuth Token?
        self.ui.oauthEdit.setEchoMode(QLineEdit.Password)
        self.lightplan_dir = default_dir
        self.settings = None
    
    def dir_browse_clicked(self):
        dir = QFileDialog.getExistingDirectory(self, "LightPLan Directory", self.lightplan_dir)
        if(dir):
            self.ui.dir_edit.setText(dir)

    def dir_default_clicked(self):
        self.ui.dir_edit.setText(self.default_dir)

    def setSettings(self, settings):
        self.settings = settings
        ssl_int = valueToBool(self.settings.value("StreamerSongList/IntegrationEnabled", False))
        show_log = valueToBool(self.settings.value("LightPlanStudio/ShowLogOnStart", False))
        update_cmds = valueToBool(self.settings.value("LightPlanStudio/UpdateCmdsOnStart", False))
        self.ui.sslCheckBox.setChecked(ssl_int)
        self.ui.userEdit.setText(self.settings.value("Twitch/Username", ""))
        self.ui.oauthEdit.setText(self.settings.value("Twitch/OAuthToken", ""))
        self.ui.channelEdit.setText(self.settings.value("Twitch/Channel", ""))
        self.ui.showLogCheckBox.setChecked(show_log)
        self.ui.updateCommandsCheckBox.setChecked(update_cmds)
        self.lightplan_dir = self.settings.value("LightPlanStudio/LightPlanDir", self.default_dir)
        self.ui.dir_edit.setText(self.lightplan_dir)
        log_level_value = self.settings.value("LightPlanStudio/LogLevel", LogLevel.INFO.value, int)

        self.log_level = LogLevel.get(log_level_value)
        ind = self.ui.log_level_combo.findData(self.log_level)
        
        if(ind == -1):
            self.ui.log_level_combo.setCurrentIndex(0)
        else:
            self.ui.log_level_combo.setCurrentIndex(ind)
        
        self.ui.customCmdListView.clear()
        customCmds = self.settings.value("LightPlanStudio/CustomCmds", "[]")
        try:
            customCmdList = json.loads(customCmds)
        except json.decoder.JSONDecodeError as e:
            self.signals.log.emit("JSONDecodeError parsing custom commands", LogLevel.ERROR)
            self.signals.log.emit(str(e), LogLevel.DEBUG)
            customCmdList = []
            
        self.ui.customCmdListView.addItems(customCmdList)
        self.signals.log.emit("Settings Loaded", LogLevel.INFO)
        
    def addCmdButtonClicked(self):
        text, ok = QInputDialog.getText(self, "Add", "Add Custom Command:")
        if(ok and len(text.strip())>0):
            self.ui.customCmdListView.addItem(str(text))
    
    def editCmdButtonClicked(self):
        curItemIndex = self.ui.customCmdListView.currentRow()
        curItem = self.ui.customCmdListView.takeItem(curItemIndex)
        if(curItem):
            text, ok = QInputDialog.getText(self, "Edit", "Edit Custom Command:", text=curItem.text())
            if(ok and len(text.strip())>0):
                self.ui.customCmdListView.insertItem(curItemIndex, str(text))
            else:
                self.ui.customCmdListView.insertItem(curItemIndex, curItem)
    
    def delCmdButtonClicked(self):
        curItemIndex = self.ui.customCmdListView.currentRow()
        self.ui.customCmdListView.takeItem(curItemIndex)

    def saveButtonClick(self):
        self.settings.setValue("StreamerSongList/IntegrationEnabled", self.ui.sslCheckBox.isChecked())
        self.settings.setValue("Twitch/Username", self.ui.userEdit.text())
        token = self.ui.oauthEdit.text().replace("oauth:", "")
        self.settings.setValue("Twitch/OAuthToken", token)
        self.settings.setValue("Twitch/Channel", self.ui.channelEdit.text())
        self.settings.setValue("LightPlanStudio/ShowLogOnStart", self.ui.showLogCheckBox.isChecked())
        self.settings.setValue("LightPlanStudio/UpdateCmdsOnStart", self.ui.updateCommandsCheckBox.isChecked())
        self.log_level = self.ui.log_level_combo.currentData()
        self.settings.setValue("LightPlanStudio/LogLevel", self.log_level.value)
        self.settings.setValue("LightPlanStudio/LightPlanDir", self.ui.dir_edit.text())
        custom_cmds = []
        for x in range(self.ui.customCmdListView.count()):
            custom_cmds.append(self.ui.customCmdListView.item(x).text())
        custom_cmd_str = "|".join(custom_cmds)
        self.settings.setValue("LightPlanStudio/CustomCmds", json.dumps(custom_cmds))
        self.settings.sync()
        self.accept()
        
    def cancelButtonClick(self):
        self.reject()
    
def secsToStr(secs, ms=False):
    mins, secs = divmod(secs, 60)
    if(ms):
        return "{:02d}:{:06.3f}".format(int(mins), secs) 
    return "{:02d}:{:02d}".format(int(mins),int(secs)) 
    
def msToStr(ms, show_ms=False):
    return secsToStr(ms/1000.0, show_ms)

def valueToBool(value):
    return value.lower() == 'true' if isinstance(value, str) else bool(value)

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

if __name__ == "__main__":
    version = "1.0.0"
    app_name = "LightPlanStudio"
    org_name = "ChillAspect"
    app = QApplication(sys.argv)
    pixmap = QPixmap(":resources/img/lps_splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    app.setOrganizationName(org_name)
    app.setApplicationName(app_name)
    app.setApplicationVersion(version)

    """
    ## Theme Editor? ##
    app.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    background_color = QColor(21,32,43)
    background_alt_color = QColor(34,48,60)
    button_color = QColor(136, 153, 166)
    disabledColor = QColor(127,127,127)
    palette.setColor(QPalette.Window, background_color)
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(18,18,18))
    palette.setColor(QPalette.AlternateBase, background_alt_color)
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabledColor)
    palette.setColor(QPalette.Button, button_color)
    palette.setColor(QPalette.ButtonText, background_color)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabledColor)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, disabledColor)
    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    """

    window = LightPlanStudio(app_name, version, app)
    time.sleep(2.5)
    window.show()
    splash.finish(window)
    sys.exit(app.exec())
