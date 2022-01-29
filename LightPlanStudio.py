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


# PySide6 Imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QStyle, 
        QDialog, QInputDialog, QSplashScreen, QProgressDialog, 
        QMessageBox, QTableWidgetItem,QAbstractItemView, 
        QLineEdit, QCheckBox, QComboBox, QHeaderView)
from PySide6.QtCore import QFile, Slot, Signal, QObject, QThread, QStandardPaths, QSettings, QTextStream, Qt, QTimer, QThreadPool
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon, QMovie
from PySide6.QtMultimedia import QAudio, QAudioOutput, QMediaFormat, QMediaPlayer

# LightPlanStudio Imports
import Resources
import UI_Components as UI
from LightPlanStudioLib import YoutubeDownloader, LogLevel, LightPlanEvent, LightPlanTableModel

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
        
        #Get Settings
        QSettings.setDefaultFormat(QSettings.IniFormat)
        self.settings = QSettings()
        self.log_level = LogLevel.get(self.settings.value("LightPlanStudio/LogLevel", LogLevel.INFO, int))
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
        self.configPath = self.settings.fileName()

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
        
        #Set window Icon
        default_icon_pixmap = QStyle.StandardPixmap.SP_FileDialogListView
        lps_icon_pixmap = QPixmap(":resources/img/icon.ico")
        lightplan_icon = QIcon(lps_icon_pixmap)
        default_icon = self.style().standardIcon(default_icon_pixmap)
        if(lightplan_icon):
            self.setWindowIcon(lightplan_icon)
        else:
            self.setWindowIcon(default_icon)
        
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
        self.resume_on_release = False
        
        ## Event Table ##
        self.lp_table_model = LightPlanTableModel(self.event_table_view, [], self.defaultCommands)
        
        ## Setup UI Signals ##
        # Menu Signals
        self.action_new_lp.triggered.connect(self.menu_click)
        self.action_open_lp.triggered.connect(self.menu_click)
        self.action_save_lp.triggered.connect(self.menu_click)
        self.action_exit.triggered.connect(self.menu_click)
        self.action_settings.triggered.connect(self.menu_click)
        self.action_lp_wizard.triggered.connect(self.menu_click)
        self.action_show_log.triggered.connect(self.menu_click)
        self.action_help_about.triggered.connect(self.menu_click)
        self.action_help_oauth.triggered.connect(self.menu_click)
        self.action_help_docs.triggered.connect(self.menu_click)
        self.action_help_checkcmds.triggered.connect(self.menu_click)
        
        # Button Signals
        self.debug_hidelog_button.clicked.connect(self.click_hidelog_button)
        self.load_song_button.clicked.connect(self.load_youtube)
        self.insert_event_button.clicked.connect(self.insert_event)
        self.play_button.clicked.connect(self.click_play_button)
        self.stop_button.clicked.connect(self.click_stop_button)
        self.song_slider.sliderMoved.connect(self.song_slider_moved)
        self.song_slider.sliderPressed.connect(self.song_slider_pressed)
        self.song_slider.sliderReleased.connect(self.song_slider_released)
        
        ## Get Temp Dir to Store Files
        self.temp_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.TempLocation), "LightPlanStudio")
        
        ## ThreadPool
        self.threadpool = QThreadPool()
        
        # Setup UI Based on Config
        self.check_showlog()
        
        #Print Log Messages
        self.log(f"Config File:{self.configPath}", LogLevel.DEBUG)
        self.lp_youtubeurl_edit.setText("https://www.youtube.com/watch?v=OnzkhQsmSag")
        
        
    ### Menu Signals #####
    def menu_click(self):
        sender = self.sender()
        if(sender == self.action_new_lp):
            self.loading()
            self.log("action_new_lp")
        elif(sender == self.action_open_lp):
            self.loading(False)
            self.log("action_open_lp")
        elif(sender == self.action_save_lp):
            self.log("action_save_lp")
        elif(sender == self.action_exit):
            self.log("action_exit")
        elif(sender == self.action_settings):
            self.show_settings_dialog()
        elif(sender == self.action_lp_wizard):
            self.show_wizard_dialog()
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
    
    def loading(self, show=True):
        if(show):
            self.loading_dialog.show()
        else:
            self.loading_dialog.hide()
        
    ## Event Wizard Functions ##
    
    def insert_event(self):
        pos = self.audio_player.position()
        evt = LightPlanEvent(self.defaultCommands, pos)
        self.lp_table_model.insertEvent(evt)
        
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
        #self.runtime_label.setText("Runtime: " + secsToStr(data["youtube"].length))
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
            
    def click_stop_button(self):
        self.current_time_lcd.display("00:00.000")
        self.song_slider.setValue(0)
        if(self.audio_player.playbackState() != QMediaPlayer.StoppedState):
            self.audio_player.stop()
            
    ## End Event Wizard Functions ##
    
    def click_hidelog_button(self):
        self.setFixedSize(self.defaultWidth, self.height)
        self.action_show_log.setChecked(False)
    
    def toggle_logvisible(self):
        if(self.action_show_log.isChecked()):
            self.setFixedSize(self.expandedWidth, self.height)
        else:
            self.setFixedSize(self.defaultWidth, self.height)
    
    def show_wizard_dialog(self):
        dlg = LightPlanWizard(self)
        dlg.signals.log.connect(self.log)
        result = dlg.exec()
        
    #Menu > Settings
    def show_settings_dialog(self):
        dlg = SettingsDialog(self)
        dlg.signals.log.connect(self.log)
        dlg.setSettings(self.settings)
        result = dlg.exec()
        if(result == QDialog.Accepted):
            #Save Settings
            self.settings = dlg.settings
            self.log_level = dlg.log_level
            #self.checkStartSSLIntegration()
            self.statusbar.showMessage("Settings Saved")
            self.log("Settings Saved")
    
    def check_showlog(self):
        checked = valueToBool(self.settings.value("LightPlanStudio/ShowLogOnStart", False))
        self.action_show_log.setChecked(checked)
        if checked:
            self.setFixedSize(self.expandedWidth, self.height)
        else:
            self.setFixedSize(self.defaultWidth, self.height)
                
    def closeEvent(self, evt):
        print("Closing LightPlanStudio")
        
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
        
class SettingsDialog(QDialog):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        
    settings = None
    
    def __init__(self, parent=None):
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
        self.log_level = LogLevel.INFO
        self.settings = None
        
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
    
if __name__ == "__main__":
    version = "1.0.0"
    app_name = "LightPlanStudio"
    app = QApplication(sys.argv)
    pixmap = QPixmap(":resources/img/lps_splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    app.setOrganizationName(app_name)
    app.setApplicationName(app_name)
    app.setApplicationVersion(version)
    window = LightPlanStudio(app_name, version)
    time.sleep(2.5)
    window.show()
    splash.finish(window)
    sys.exit(app.exec())
