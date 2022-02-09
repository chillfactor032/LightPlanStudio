# Python Imports
import os
import sys
import datetime
import json
import time
import requests
from pytube import YouTube
from pathlib import Path
from enum import Enum
import hashlib

# PySide6 Imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QStyle, 
        QDialog, QInputDialog, QSplashScreen, QProgressDialog, 
        QMessageBox, QTableWidgetItem,QAbstractItemView, 
        QLineEdit, QCheckBox, QComboBox, QHeaderView, QFileDialog)
from PySide6.QtCore import QFile, Slot, Signal, QObject, QThread, QStandardPaths, QSettings, QTextStream, Qt, QTimer, QThreadPool, QFileSystemWatcher
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon, QMovie
from PySide6.QtMultimedia import QAudio, QAudioOutput, QMediaFormat, QMediaPlayer

# LightPlanStudio Imports
import Resources
import UI_Components as UI
from LightPlanStudioLib import YoutubeDownloader, LogLevel, LightPlanEvent, LightPlanTableModel, TwitchIRC, LightPlanRunner

class LightPlanStudio(QMainWindow, UI.Ui_LPS_MainWindow):
    def __init__(self, app_name, version):
        super(LightPlanStudio, self).__init__()
        
        #Read Version File From Resources
        version_file = QFile(":version.json")
        version_file.open(QFile.ReadOnly)
        text_stream = QTextStream(version_file)
        version_file_text = text_stream.readAll()
        self.version_dict = json.loads(version_file_text)
        self.app_name = self.version_dict["product_name"]
        self.version = self.version_dict["version"]
        
        ## Get Temp Dir to Store Files
        self.temp_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.TempLocation), "LightPlanStudio")
        self.config_dir = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
        if(not os.path.isdir(self.config_dir)):
            os.mkdir(self.config_dir)
        self.ini_path = os.path.join(self.config_dir, "LightPlanStudio.ini").replace("\\", "/")
        self.default_lightplan_dir = os.path.join(self.config_dir, "LightPlans").replace("\\", "/")
        if(not os.path.isdir(self.default_lightplan_dir)):
            os.mkdir(self.default_lightplan_dir)

        #Get Settings
        self.settings = QSettings(self.ini_path, QSettings.IniFormat)
        self.log_level = LogLevel.get(self.settings.value("LightPlanStudio/LogLevel", LogLevel.INFO, int))
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
        
        #Load UI Components
        self.setupUi(self)
        self.setWindowTitle(f"{self.app_name} {self.version}")
        self.loading_pixmap = QPixmap(":resources/img/loading.gif")
        self.loading_movie = QMovie(":resources/img/loading.gif")
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.ui.loading_label.setFixedSize(self.loading_pixmap.size())
        self.loading_dialog.setFixedSize(self.loading_pixmap.size())
        self.loading_dialog.setMovie(self.loading_movie)
        self.loading_dialog.hide()
        style = self.style()
        self.check_icon = style.standardIcon(QStyle.SP_DialogApplyButton)
        self.x_icon = style.standardIcon(QStyle.SP_DialogCloseButton)
        self.play_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaPlay))
        self.pause_icon = QIcon.fromTheme("media-playback-pause.png", style.standardIcon(QStyle.SP_MediaPause))
        self.stop_icon = QIcon.fromTheme("media-playback-stop.png", style.standardIcon(QStyle.SP_MediaStop))
        self.play_button.setIcon(self.play_icon)
        self.stop_button.setIcon(self.stop_icon)
        self.song_loaded_status_icon.setPixmap(self.x_icon.pixmap(self.song_loaded_status_icon.width(), self.song_loaded_status_icon.height()))
        self.current_time_lcd.display("00:00.000")
        self.green_button_css = 'QPushButton {background-color: #A3C1DA; color: green;}'
        self.red_button_css = 'QPushButton {background-color: #A3C1DA; color: red;}'
        self.default_button_css = self.twitch_connect_button.styleSheet()
        self.calc_delay_button.setEnabled(False)
        self.control_startlp_button.setEnabled(False)
        self.delay_lcd.display("0")
        self.start_event_edit.setInputMask("99\:99\.999")
        self.event_table_view.setStyleSheet("QTableView:disabled {background-color:#ffffff;}")

        #Set window Icon
        default_icon_pixmap = QStyle.StandardPixmap.SP_FileDialogListView
        lps_icon_pixmap = QPixmap(":resources/img/icon.ico")
        self.lightplan_icon = QIcon(lps_icon_pixmap)
        default_icon = self.style().standardIcon(default_icon_pixmap)
        if(self.lightplan_icon):
            self.setWindowIcon(self.lightplan_icon)
        else:
            self.setWindowIcon(default_icon)
            self.lightplan_icon = default_icon
        
        ## Setup Audio Player
        self.audio_output = QAudioOutput()
        self.audio_player = QMediaPlayer()
        self.audio_player.setAudioOutput(self.audio_output)
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
        self.lightplan_runner = None
        self.lightplan_start_timer = QTimer()
        self.lightplan_start_timer.timeout.connect(self.update_lightplan_elapsed)
        self.lightplan_start_time = None
        self.next_event_secs = 0

        ## Event Table ##
        self.lp_table_model = LightPlanTableModel(self.event_table_view, [], self.defaultCommands)
        self.lp_table_model.action_set_start_event.triggered.connect(self.click_set_start_event)

        ## Setup UI Signals ##
        # Menu Signals
        self.action_new_lp.triggered.connect(self.menu_click)
        self.action_open_lp.triggered.connect(self.menu_click)
        self.action_save_lp.triggered.connect(self.menu_click)
        self.action_exit.triggered.connect(self.menu_click)
        self.action_settings.triggered.connect(self.menu_click)
        self.action_show_log.triggered.connect(self.menu_click)
        self.action_help_about.triggered.connect(self.menu_click)
        self.action_help_oauth.triggered.connect(self.menu_click)
        self.action_help_docs.triggered.connect(self.menu_click)
        self.action_help_checkcmds.triggered.connect(self.menu_click)
        self.statusbar.messageChanged.connect(self.status_msg_changed)

        # Button Signals
        self.debug_hidelog_button.clicked.connect(self.click_hidelog_button)
        self.load_song_button.clicked.connect(self.load_youtube)
        self.insert_event_button.clicked.connect(self.insert_event)
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

        ## ThreadPool
        self.threadpool = QThreadPool()
        
        ## Twitch Chat 
        self.twitch = None

        # Setup UI Based on Config
        self.check_showlog()
        self.set_status(self.status_msg)

        # LightPlan Explorer Tab
        self.lp_tree_model = QStandardItemModel()
        self.lp_tree_model.setHorizontalHeaderLabels(['LightPlans'])
        self.lp_tree_view.setIndentation(12)
        self.lp_tree_view.setModel(self.lp_tree_model)
        self.lp_tree_view.doubleClicked.connect(self.lp_tree_doubleclicked)
        self.reset_fswatcher()

        #Set initial lightplan
        self.current_lightplan = {"path": None}
        self.current_lightplan["lightplan"] = self.lightplan_gui_to_dict()
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()
        
        #Print Log Messages
        self.log(f"Config File:{self.ini_path}", LogLevel.DEBUG)
        
        
    ### Menu Signals #####
    def menu_click(self):
        sender = self.sender()
        if(sender == self.action_new_lp):
            self.new_lp_clicked()
        elif(sender == self.action_open_lp):
            self.show_file_dialog()
        elif(sender == self.action_save_lp):
            self.log("action_save_lp")
        elif(sender == self.action_exit):
            self.log("action_exit")
        elif(sender == self.action_settings):
            self.show_settings_dialog()
        elif(sender == self.action_show_log):
            self.toggle_logvisible()
        elif(sender == self.action_help_about):
            self.log("action_help_about")
        elif(sender == self.action_help_oauth):
            self.log("action_help_oauth")
        elif(sender == self.action_help_docs):
            self.log("action_help_docs")
        elif(sender == self.action_help_checkcmds):
            self.log("action_help_checkcmds")
    
    # Setup FileSystemWatcher To keep the LP Explorer Updated
    def reset_fswatcher(self):
        if(self.file_watcher is not None):
            del self.file_watcher
        self.file_watcher = QFileSystemWatcher()
        self.refresh_lptree()
        self.file_watcher.addPath(self.lightplan_dir)
        for root, dirs, files in os.walk(self.lightplan_dir):
            for dir in dirs:
                self.file_watcher.addPath(os.path.join(root, dir))
        self.file_watcher.directoryChanged.connect(self.refresh_lptree)

    def refresh_lptree(self):
        self.lp_tree_model.clear()
        self.lp_tree_model.setHorizontalHeaderLabels(['LightPlans'])
        self.lightplan_files = []
        result = sorted(Path(self.lightplan_dir).rglob("*.plan"))
        lightplan = {}
        for plan in result:
            with open(plan, 'r') as json_file:
                try:
                    obj = {}
                    lightplan = json.load(json_file)
                    if("song_artist" not in lightplan or "song_title" not in lightplan):
                        continue
                    obj["path"] = plan.__str__()
                    obj["artist"] = lightplan["song_artist"]
                    obj["title"] = lightplan["song_title"]
                    obj["ssl_id"] = lightplan["ssl_id"]
                    self.lightplan_files.append(obj)
                except ValueError as err:
                    continue

        for lp in self.lightplan_files:
            item = QStandardItem(lp["title"])
            item.setEditable(False)
            item.setData(lp["path"])
            item.setIcon(self.lightplan_icon)
            artist = self.lp_tree_model.findItems(lp["artist"])
            if(len(artist)>0):
                artist[0].appendRow(item)
            else:
                parent = QStandardItem(lp["artist"])
                parent.setEditable(False)
                parent.setData("")
                parent.appendRow(item)
                self.lp_tree_model.appendRow(parent)  

    def lp_tree_doubleclicked(self):
        index = self.lp_tree_view.selectedIndexes()[0]
        selected = index.model().itemFromIndex(index)
        if(len(selected.data())>0):
            self.open_lp_file(selected.data())

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
        self.current_lightplan["path"] = None
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()
        self.set_status("New LightPlan")

    ## Show Loading Gif ###
    def loading(self, show=True):
        if(show):
            self.loading_dialog.show()
        else:
            self.loading_dialog.hide()
    
    ## LightPlan File Functions ##

    def show_file_dialog(self):
        file_name = QFileDialog.getOpenFileName(self, "Open LightPlan", self.lightplan_dir, "LightPlans (*.plan)")
        if(file_name):
            self.open_lp_file(file_name[0])
        self.log(f"Opening LightPlan File: {file_name}")

    def open_lp_file(self, lp_path):
        lightplan_dict = None
        if(not os.path.exists(lp_path)):
            return
        try:
            with open(lp_path, "r") as file:
                lightplan_dict = json.load(file)
        except json.JSONDecodeError as err:
            self.log(str(err), LogLevel.ERROR)
            return
        self.clear_lightplan()
        self.lp_songtitle_edit.setText(lightplan_dict["song_title"])
        self.lp_artist_edit.setText(lightplan_dict["song_artist"])
        self.lp_author_edit.setText(lightplan_dict["author"])
        self.lp_sslid_edit.setText(lightplan_dict["ssl_id"])
        self.lp_spotifyid_edit.setText(lightplan_dict["spotify_id"])
        self.lp_youtubeurl_edit.setText(lightplan_dict["youtube_url"])
        self.lp_notes_edit.setPlainText(lightplan_dict["notes"])
        self.start_event_edit.setText(msToStr(lightplan_dict["starting_ms"], True))
        self.lp_table_model.clear_events()
        for evt in lightplan_dict["events"]:
            evt_obj = LightPlanEvent(evt["offset"],evt["command"],evt["comment"],valueToBool(evt["ignore_delay"]))
            self.lp_table_model.insert_event(evt_obj)
        self.current_lightplan = {
            "path": lp_path,
            "md5": hashlib.md5(str(lightplan_dict).encode("utf-8")).hexdigest(),
            "lightplan": lightplan_dict
        }
        self.set_status(self.current_lightplan["path"])

    def checkLightPlanUpdated(self):
        lp = self.lightplan_gui_to_dict()
        return hashlib.md5(str(lp).encode("utf-8")).hexdigest() != self.current_lightplan["md5"]

    def lightplan_gui_to_dict(self):
        self.lp_table_model.sort(0,Qt.AscendingOrder)
        lightplan_dict = {
            "song_title": "",
            "song_artist": "",
            "author": "",
            "ssl_id": "",
            "spotify_id": "",
            "youtube_url": "",
            "notes": "",
            "starting_ms": 0,
            "events": []
        }
        lightplan_dict["song_title"] = self.lp_songtitle_edit.text().strip()
        lightplan_dict["song_artist"] = self.lp_artist_edit.text().strip()
        lightplan_dict["author"] = self.lp_author_edit.text().strip()
        lightplan_dict["ssl_id"] = self.lp_sslid_edit.text().strip()
        lightplan_dict["spotify_id"] = self.lp_spotifyid_edit.text().strip()
        lightplan_dict["youtube_url"] = self.lp_youtubeurl_edit.text().strip()
        lightplan_dict["notes"] = self.lp_notes_edit.toPlainText().strip()
        lightplan_dict["starting_ms"] = strToMs(self.start_event_edit.text().strip())
        lightplan_dict["events"] = self.lp_table_model.exportJsonDict()
        return lightplan_dict
    
    def save_light_plan(self):
        self.current_lightplan["lightplan"] = self.lightplan_gui_to_dict()
        self.current_lightplan["md5"] = hashlib.md5(str(self.current_lightplan["lightplan"]).encode("utf-8")).hexdigest()
        if(len(self.current_lightplan["lightplan"]["song_title"].strip())==0 or len(self.current_lightplan["lightplan"]["song_artist"].strip())==0):
            QMessageBox.warning(self, "LightPlan Studio", "Song Artist and Title are required.")
            return False
        if(self.current_lightplan["path"] is None):
            keepcharacters = (' ','.','_',"-")
            file_name = f"{self.current_lightplan['lightplan']['song_artist']} - {self.current_lightplan['lightplan']['song_title']}.plan"
            file_name = "".join(c for c in file_name if c.isalnum() or c in keepcharacters).rstrip()
            self.current_lightplan["path"] = os.path.join(self.lightplan_dir, file_name).replace("\\", "/")
        lp_json = json.dumps(self.current_lightplan["lightplan"])
        with open(self.current_lightplan["path"], "w") as file:
            file.write(lp_json)
        self.set_status("LightPlan Saved", 2500)
        return True

    def click_save_button(self):
        if(self.checkLightPlanUpdated()):
            if(self.save_light_plan()):
                self.log("LightPlan Saved")
                self.log(self.current_lightplan["md5"], LogLevel.DEBUG)
        else:
            self.log("LightPlan not changed", LogLevel.DEBUG)
            self.log(self.current_lightplan["md5"], LogLevel.DEBUG)

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
            self.lightplan_runner = LightPlanRunner(self.twitch, lp, self.stream_delay_ms, self.delay_adjust_ms)
            self.lightplan_runner.signals.log.connect(self.log)
            self.lightplan_runner.signals.done.connect(self.lightplan_runner_done)
            self.lightplan_runner.signals.progress.connect(self.lightplan_runner_progress)
            self.control_lp_progressbar.reset()
            self.control_lp_progressbar.setMaximum(len(lp["events"]))
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
        self.control_lp_progressbar.reset()
        self.control_lp_progressbar.setFormat("Light Event 0/0")
        self.event_table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)
        self.lightplan_start_timer.stop()
        self.set_status(msg, 2500)

    def lightplan_runner_progress(self, cur_evt_num, next_event_secs, next_event):
        self.next_event_secs = next_event_secs
        self.control_nextevent_label.setText(next_event)
        self.control_lp_progressbar.setValue(cur_evt_num)
        self.control_lp_progressbar.setFormat("Light Event %v/%m")
        
    def update_lightplan_elapsed(self):
        elapsed = time.time()-self.lightplan_start_time
        target = self.next_event_secs - elapsed
        if(target >= 0):
            self.control_lpelapsed_label.setText(secsToStr(target))

    ## Twitch Chat Functions ##

    def click_twitch_connect_button(self):
        if(self.twitch and self.twitch.connected()):
            self.twitch.die()
        else:
            user_name = self.settings.value("Twitch/Username", "")
            token = self.settings.value("Twitch/OAuthToken", "")
            channel = self.settings.value("Twitch/Channel", "")
            self.twitch = TwitchIRC(user_name, token, channel)
            self.twitch.signals.log.connect(self.log)
            self.twitch.signals.irc_disconnect.connect(self.twitch_disconnect)
            self.twitch.signals.irc_connect.connect(self.twitch_connect)
            self.threadpool.start(self.twitch)

    def twitch_connect(self):
        self.twitch_connect_button.setText("Disconnect Twitch")
        self.calc_delay_button.setEnabled(True)
        self.control_startlp_button.setEnabled(True)

    def twitch_disconnect(self):
        self.twitch_connect_button.setText("Connect Twitch")
        self.calc_delay_button.setEnabled(False)
        self.control_startlp_button.setEnabled(False)

    ## Event Wizard Functions ##
    
    def insert_event(self):
        pos = self.audio_player.position()
        evt = LightPlanEvent(pos)
        self.lp_table_model.insert_event(evt)
        
    def load_youtube(self):
        self.loading()
        self.song_slider.setEnabled(False)
        self.play_button.setEnabled(False)
        self.insert_event_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.current_time_lcd.display("00:00.000")
        url = self.lp_youtubeurl_edit.text()
        yt = YoutubeDownloader(url, self.temp_dir)
        yt.signals.log.connect(self.log)
        yt.signals.done.connect(self.download_complete)
        self.threadpool.start(yt)
    
    def download_complete(self, result, data=None):
        if(not result):
            return
        self.song_file_path = data["audio_path"]
        self.song_image_path = data["image_path"]
        self.audio_player.setSource(self.song_file_path)
        self.position_ms = 0
        self.song_loaded = True
        self.song_slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.insert_event_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.song_loaded_status_icon.setPixmap(self.check_icon.pixmap(self.song_loaded_status_icon.width(), self.song_loaded_status_icon.height()))
        self.song_loaded_status_label.setText("Song Loaded")
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
        ret = QMessageBox.warning(self, "Error", error_string)
    
    def durationChanged(self):
        self.duration_ms = self.audio_player.duration()
    
    def playbackStateChanged(self):
        if(self.audio_player.playbackState() == QMediaPlayer.PlayingState):
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)
        
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
            
    ## End Event Wizard Functions ##
    
    def click_set_start_event(self):
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

    def closeEvent(self, evt):
        if(self.checkLightPlanUpdated()):
            ret = QMessageBox.question(self, "LightPlan Studio",
                "The LightPlan has been modified.\nDo you want to save your changes?",
                QMessageBox.Save, 
                QMessageBox.Discard)
            if(ret == QMessageBox.Save):
                if(self.save_light_plan()):
                    QMessageBox.information(self, "LightPlan Studio", "LightPlan Saved")
                else:
                    return evt.ignore()
        if(self.twitch and self.twitch.connected()):
            self.twitch.die()
        if(self.lightplan_runner is not None and self.lightplan_runner.is_running()):
            self.lightplan_runner.stop()
        return evt.accept()
        
    def log(self, msg, level=LogLevel.INFO):
        if(not msg or level.value > self.log_level.value):
            return
        if(level == LogLevel.ERROR):
            style = "color: #cc0000;"
        elif(level == LogLevel.DEBUG):
            style = "color: #006600;"
        else:
            style = "color: #000000;"
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        msg = f'<span style="{style}">{timestamp} - {msg}</span>'
        self.debug_log_edit.append(msg)


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
        self.settings = None
    
    def dir_browse_clicked(self):
        dir = QFileDialog.getExistingDirectory(self, "LightPLan Directory")
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
        self.ui.dir_edit.setText(self.settings.value("LightPlanStudio/LightPlanDir", self.default_dir))
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
        self.settings.setValue("Twitch/OAuthToken", self.ui.oauthEdit.text())
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
    window = LightPlanStudio(app_name, version)
    time.sleep(2.5)
    window.show()
    splash.finish(window)
    sys.exit(app.exec())
