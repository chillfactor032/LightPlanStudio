# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LPS_CalcDelay.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLCDNumber,
    QLabel, QPushButton, QSizePolicy, QWidget)

class Ui_CalcDelayDialog(object):
    def setupUi(self, CalcDelayDialog):
        if not CalcDelayDialog.objectName():
            CalcDelayDialog.setObjectName(u"CalcDelayDialog")
        CalcDelayDialog.resize(301, 238)
        self.command_combo = QComboBox(CalcDelayDialog)
        self.command_combo.addItem("")
        self.command_combo.addItem("")
        self.command_combo.addItem("")
        self.command_combo.setObjectName(u"command_combo")
        self.command_combo.setGeometry(QRect(10, 110, 191, 22))
        self.command_combo.setEditable(True)
        self.label = QLabel(CalcDelayDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 0, 281, 51))
        self.label.setWordWrap(True)
        self.send_button = QPushButton(CalcDelayDialog)
        self.send_button.setObjectName(u"send_button")
        self.send_button.setGeometry(QRect(220, 110, 71, 23))
        self.delay_lcd = QLCDNumber(CalcDelayDialog)
        self.delay_lcd.setObjectName(u"delay_lcd")
        self.delay_lcd.setGeometry(QRect(10, 140, 191, 51))
        self.delay_lcd.setDigitCount(9)
        self.stop_button = QPushButton(CalcDelayDialog)
        self.stop_button.setObjectName(u"stop_button")
        self.stop_button.setGeometry(QRect(220, 140, 71, 51))
        self.label_2 = QLabel(CalcDelayDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 51, 31))
        self.label_3 = QLabel(CalcDelayDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 60, 281, 31))
        self.label_3.setWordWrap(True)
        self.save_button = QPushButton(CalcDelayDialog)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setGeometry(QRect(120, 200, 81, 24))
        self.cancel_button = QPushButton(CalcDelayDialog)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QRect(220, 200, 71, 24))

        self.retranslateUi(CalcDelayDialog)

        QMetaObject.connectSlotsByName(CalcDelayDialog)
    # setupUi

    def retranslateUi(self, CalcDelayDialog):
        CalcDelayDialog.setWindowTitle(QCoreApplication.translate("CalcDelayDialog", u"Stream Delay", None))
        self.command_combo.setItemText(0, QCoreApplication.translate("CalcDelayDialog", u"!dim", None))
        self.command_combo.setItemText(1, QCoreApplication.translate("CalcDelayDialog", u"!normal", None))
        self.command_combo.setItemText(2, QCoreApplication.translate("CalcDelayDialog", u"!arctic", None))

        self.label.setText(QCoreApplication.translate("CalcDelayDialog", u"Send a chat command and stop the timer when you see it reflected on stream. ", None))
        self.send_button.setText(QCoreApplication.translate("CalcDelayDialog", u"Send", None))
        self.stop_button.setText(QCoreApplication.translate("CalcDelayDialog", u"Stop", None))
        self.label_2.setText(QCoreApplication.translate("CalcDelayDialog", u"Example: ", None))
        self.label_3.setText(QCoreApplication.translate("CalcDelayDialog", u"Send a !dim command and stop the timer when the lights change.", None))
        self.save_button.setText(QCoreApplication.translate("CalcDelayDialog", u"Save Delay", None))
        self.cancel_button.setText(QCoreApplication.translate("CalcDelayDialog", u"Cancel", None))
    # retranslateUi



# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LPS_LoadingDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QSizePolicy,
    QWidget)

class Ui_LoadingDialog(object):
    def setupUi(self, LoadingDialog):
        if not LoadingDialog.objectName():
            LoadingDialog.setObjectName(u"LoadingDialog")
        LoadingDialog.resize(320, 201)
        self.loading_label = QLabel(LoadingDialog)
        self.loading_label.setObjectName(u"loading_label")
        self.loading_label.setGeometry(QRect(-10, -10, 331, 211))

        self.retranslateUi(LoadingDialog)

        QMetaObject.connectSlotsByName(LoadingDialog)
    # setupUi

    def retranslateUi(self, LoadingDialog):
        LoadingDialog.setWindowTitle(QCoreApplication.translate("LoadingDialog", u"Dialog", None))
        self.loading_label.setText("")
    # retranslateUi



# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LPS_MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDoubleSpinBox, QFrame,
    QGroupBox, QHeaderView, QLCDNumber, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QStatusBar, QTabWidget,
    QTableView, QTextEdit, QTreeView, QVBoxLayout,
    QWidget)

class Ui_LPS_MainWindow(object):
    def setupUi(self, LPS_MainWindow):
        if not LPS_MainWindow.objectName():
            LPS_MainWindow.setObjectName(u"LPS_MainWindow")
        LPS_MainWindow.resize(1250, 800)
        self.action_help_about = QAction(LPS_MainWindow)
        self.action_help_about.setObjectName(u"action_help_about")
        self.action_help_oauth = QAction(LPS_MainWindow)
        self.action_help_oauth.setObjectName(u"action_help_oauth")
        self.action_new_lp = QAction(LPS_MainWindow)
        self.action_new_lp.setObjectName(u"action_new_lp")
        self.action_open_lp = QAction(LPS_MainWindow)
        self.action_open_lp.setObjectName(u"action_open_lp")
        self.action_Wizard = QAction(LPS_MainWindow)
        self.action_Wizard.setObjectName(u"action_Wizard")
        self.action_exit = QAction(LPS_MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_help_docs = QAction(LPS_MainWindow)
        self.action_help_docs.setObjectName(u"action_help_docs")
        self.action_settings = QAction(LPS_MainWindow)
        self.action_settings.setObjectName(u"action_settings")
        self.action_lp_wizard = QAction(LPS_MainWindow)
        self.action_lp_wizard.setObjectName(u"action_lp_wizard")
        self.action_show_log = QAction(LPS_MainWindow)
        self.action_show_log.setObjectName(u"action_show_log")
        self.action_show_log.setCheckable(True)
        self.action_save_lp = QAction(LPS_MainWindow)
        self.action_save_lp.setObjectName(u"action_save_lp")
        self.action_help_checkcmds = QAction(LPS_MainWindow)
        self.action_help_checkcmds.setObjectName(u"action_help_checkcmds")
        self.action_open_lpdir = QAction(LPS_MainWindow)
        self.action_open_lpdir.setObjectName(u"action_open_lpdir")
        self.action_open_configdir = QAction(LPS_MainWindow)
        self.action_open_configdir.setObjectName(u"action_open_configdir")
        self.action_import_lp = QAction(LPS_MainWindow)
        self.action_import_lp.setObjectName(u"action_import_lp")
        self.action_export_lp = QAction(LPS_MainWindow)
        self.action_export_lp.setObjectName(u"action_export_lp")
        self.centralwidget = QWidget(LPS_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(560, 10, 231, 341))
        self.lightPlanTab = QWidget()
        self.lightPlanTab.setObjectName(u"lightPlanTab")
        self.lp_tree_view = QTreeView(self.lightPlanTab)
        self.lp_tree_view.setObjectName(u"lp_tree_view")
        self.lp_tree_view.setGeometry(QRect(10, 10, 201, 291))
        self.lp_tree_view.setAcceptDrops(True)
        self.lp_tree_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.lp_tree_view.setDefaultDropAction(Qt.CopyAction)
        self.lp_tree_view.setAlternatingRowColors(True)
        self.tabWidget.addTab(self.lightPlanTab, "")
        self.sslTab = QWidget()
        self.sslTab.setObjectName(u"sslTab")
        self.verticalLayoutWidget = QWidget(self.sslTab)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 201, 291))
        self.ssl_layout = QVBoxLayout(self.verticalLayoutWidget)
        self.ssl_layout.setObjectName(u"ssl_layout")
        self.ssl_layout.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.ssl_layout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.sslTab, "")
        self.LightPlanBox = QGroupBox(self.centralwidget)
        self.LightPlanBox.setObjectName(u"LightPlanBox")
        self.LightPlanBox.setGeometry(QRect(10, 10, 541, 591))
        self.label = QLabel(self.LightPlanBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 30, 81, 21))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lp_songtitle_edit = QLineEdit(self.LightPlanBox)
        self.lp_songtitle_edit.setObjectName(u"lp_songtitle_edit")
        self.lp_songtitle_edit.setGeometry(QRect(90, 30, 181, 20))
        self.lp_artist_edit = QLineEdit(self.LightPlanBox)
        self.lp_artist_edit.setObjectName(u"lp_artist_edit")
        self.lp_artist_edit.setGeometry(QRect(90, 60, 181, 20))
        self.label_2 = QLabel(self.LightPlanBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 60, 81, 21))
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3 = QLabel(self.LightPlanBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 160, 31, 16))
        self.lp_notes_edit = QPlainTextEdit(self.LightPlanBox)
        self.lp_notes_edit.setObjectName(u"lp_notes_edit")
        self.lp_notes_edit.setGeometry(QRect(10, 180, 411, 51))
        self.label_4 = QLabel(self.LightPlanBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 90, 81, 21))
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lp_author_edit = QLineEdit(self.LightPlanBox)
        self.lp_author_edit.setObjectName(u"lp_author_edit")
        self.lp_author_edit.setGeometry(QRect(90, 90, 181, 20))
        self.label_5 = QLabel(self.LightPlanBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(300, 60, 41, 21))
        self.lp_sslid_edit = QLineEdit(self.LightPlanBox)
        self.lp_sslid_edit.setObjectName(u"lp_sslid_edit")
        self.lp_sslid_edit.setGeometry(QRect(340, 60, 141, 20))
        self.lp_spotifyid_edit = QLineEdit(self.LightPlanBox)
        self.lp_spotifyid_edit.setObjectName(u"lp_spotifyid_edit")
        self.lp_spotifyid_edit.setGeometry(QRect(340, 90, 181, 20))
        self.label_6 = QLabel(self.LightPlanBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(280, 90, 51, 21))
        self.label_7 = QLabel(self.LightPlanBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 240, 61, 16))
        self.label_8 = QLabel(self.LightPlanBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 130, 81, 21))
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lp_youtubeurl_edit = QLineEdit(self.LightPlanBox)
        self.lp_youtubeurl_edit.setObjectName(u"lp_youtubeurl_edit")
        self.lp_youtubeurl_edit.setGeometry(QRect(90, 130, 431, 20))
        self.lp_save_button = QPushButton(self.LightPlanBox)
        self.lp_save_button.setObjectName(u"lp_save_button")
        self.lp_save_button.setGeometry(QRect(450, 20, 75, 23))
        self.label_14 = QLabel(self.LightPlanBox)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(430, 180, 91, 16))
        self.start_event_edit = QLineEdit(self.LightPlanBox)
        self.start_event_edit.setObjectName(u"start_event_edit")
        self.start_event_edit.setGeometry(QRect(430, 210, 91, 22))
        self.event_table_view = QTableView(self.LightPlanBox)
        self.event_table_view.setObjectName(u"event_table_view")
        self.event_table_view.setGeometry(QRect(10, 260, 521, 321))
        self.event_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.event_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.event_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.event_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.event_table_view.setSortingEnabled(True)
        self.event_table_view.setWordWrap(False)
        self.event_table_view.verticalHeader().setVisible(False)
        self.ssl_lookup_button = QPushButton(self.LightPlanBox)
        self.ssl_lookup_button.setObjectName(u"ssl_lookup_button")
        self.ssl_lookup_button.setGeometry(QRect(490, 58, 29, 24))
        self.streamDelayBox = QGroupBox(self.centralwidget)
        self.streamDelayBox.setObjectName(u"streamDelayBox")
        self.streamDelayBox.setGeometry(QRect(560, 360, 231, 181))
        self.delay_lcd = QLCDNumber(self.streamDelayBox)
        self.delay_lcd.setObjectName(u"delay_lcd")
        self.delay_lcd.setGeometry(QRect(30, 30, 171, 41))
        self.delay_lcd.setFrameShape(QFrame.Box)
        self.delay_lcd.setFrameShadow(QFrame.Raised)
        self.delay_lcd.setLineWidth(1)
        self.delay_lcd.setDigitCount(5)
        self.delay_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.calc_delay_button = QPushButton(self.streamDelayBox)
        self.calc_delay_button.setObjectName(u"calc_delay_button")
        self.calc_delay_button.setGeometry(QRect(130, 80, 71, 31))
        self.label_10 = QLabel(self.streamDelayBox)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(30, 120, 161, 21))
        self.delay_adjust_slider = QSlider(self.streamDelayBox)
        self.delay_adjust_slider.setObjectName(u"delay_adjust_slider")
        self.delay_adjust_slider.setGeometry(QRect(10, 150, 211, 22))
        self.delay_adjust_slider.setMinimum(-30000)
        self.delay_adjust_slider.setMaximum(30000)
        self.delay_adjust_slider.setSingleStep(100)
        self.delay_adjust_slider.setPageStep(1000)
        self.delay_adjust_slider.setValue(0)
        self.delay_adjust_slider.setSliderPosition(0)
        self.delay_adjust_slider.setOrientation(Qt.Horizontal)
        self.delay_adjust_slider.setTickPosition(QSlider.NoTicks)
        self.delay_adjust_spinner = QDoubleSpinBox(self.streamDelayBox)
        self.delay_adjust_spinner.setObjectName(u"delay_adjust_spinner")
        self.delay_adjust_spinner.setGeometry(QRect(130, 120, 71, 22))
        self.delay_adjust_spinner.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.delay_adjust_spinner.setDecimals(1)
        self.delay_adjust_spinner.setMinimum(-100.000000000000000)
        self.delay_adjust_spinner.setSingleStep(0.100000000000000)
        self.set_delay_button = QPushButton(self.streamDelayBox)
        self.set_delay_button.setObjectName(u"set_delay_button")
        self.set_delay_button.setGeometry(QRect(30, 80, 71, 31))
        self.label_11 = QLabel(self.streamDelayBox)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(170, 50, 21, 16))
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(560, 550, 231, 201))
        self.control_startlp_button = QPushButton(self.groupBox_3)
        self.control_startlp_button.setObjectName(u"control_startlp_button")
        self.control_startlp_button.setGeometry(QRect(10, 150, 211, 41))
        self.twitch_connect_button = QPushButton(self.groupBox_3)
        self.twitch_connect_button.setObjectName(u"twitch_connect_button")
        self.twitch_connect_button.setGeometry(QRect(10, 30, 211, 31))
        self.control_lp_progressbar = QProgressBar(self.groupBox_3)
        self.control_lp_progressbar.setObjectName(u"control_lp_progressbar")
        self.control_lp_progressbar.setGeometry(QRect(10, 120, 211, 23))
        self.control_lp_progressbar.setValue(0)
        self.control_lp_progressbar.setAlignment(Qt.AlignCenter)
        self.control_lp_progressbar.setTextVisible(True)
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 100, 61, 16))
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.control_lpelapsed_label = QLabel(self.groupBox_3)
        self.control_lpelapsed_label.setObjectName(u"control_lpelapsed_label")
        self.control_lpelapsed_label.setGeometry(QRect(80, 100, 61, 16))
        self.label_12 = QLabel(self.groupBox_3)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 80, 61, 16))
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.line = QFrame(self.groupBox_3)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 60, 211, 16))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.control_nextevent_label = QLabel(self.groupBox_3)
        self.control_nextevent_label.setObjectName(u"control_nextevent_label")
        self.control_nextevent_label.setGeometry(QRect(80, 80, 121, 16))
        self.connected_label = QLabel(self.groupBox_3)
        self.connected_label.setObjectName(u"connected_label")
        self.connected_label.setGeometry(QRect(180, 73, 40, 40))
        self.debug_log_edit = QTextEdit(self.centralwidget)
        self.debug_log_edit.setObjectName(u"debug_log_edit")
        self.debug_log_edit.setGeometry(QRect(810, 30, 431, 691))
        self.debug_log_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.debug_log_edit.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)
        self.label_13 = QLabel(self.centralwidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(820, 10, 61, 16))
        self.debug_exportlog_button = QPushButton(self.centralwidget)
        self.debug_exportlog_button.setObjectName(u"debug_exportlog_button")
        self.debug_exportlog_button.setGeometry(QRect(1160, 730, 75, 23))
        self.debug_hidelog_button = QPushButton(self.centralwidget)
        self.debug_hidelog_button.setObjectName(u"debug_hidelog_button")
        self.debug_hidelog_button.setGeometry(QRect(810, 730, 75, 23))
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 610, 541, 141))
        self.insert_event_button = QPushButton(self.groupBox)
        self.insert_event_button.setObjectName(u"insert_event_button")
        self.insert_event_button.setGeometry(QRect(180, 100, 151, 31))
        self.current_time_lcd = QLCDNumber(self.groupBox)
        self.current_time_lcd.setObjectName(u"current_time_lcd")
        self.current_time_lcd.setGeometry(QRect(390, 20, 101, 31))
        self.current_time_lcd.setDigitCount(9)
        self.current_time_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.current_time_lcd.setProperty("value", 123456789.000000000000000)
        self.load_song_button = QPushButton(self.groupBox)
        self.load_song_button.setObjectName(u"load_song_button")
        self.load_song_button.setGeometry(QRect(10, 20, 101, 21))
        self.play_button = QPushButton(self.groupBox)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setGeometry(QRect(10, 100, 31, 31))
        icon = QIcon()
        iconThemeName = u"QStyle.SP_MediaPlay"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u"../../../../../.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.play_button.setIcon(icon)
        self.play_button.setIconSize(QSize(32, 32))
        self.stop_button = QPushButton(self.groupBox)
        self.stop_button.setObjectName(u"stop_button")
        self.stop_button.setGeometry(QRect(460, 100, 31, 31))
        self.stop_button.setIcon(icon)
        self.song_slider = QSlider(self.groupBox)
        self.song_slider.setObjectName(u"song_slider")
        self.song_slider.setGeometry(QRect(10, 60, 481, 31))
        self.song_slider.setMaximum(999)
        self.song_slider.setOrientation(Qt.Horizontal)
        self.song_slider.setTickPosition(QSlider.TicksBothSides)
        self.song_slider.setTickInterval(25)
        self.song_loaded_status_label = QLabel(self.groupBox)
        self.song_loaded_status_label.setObjectName(u"song_loaded_status_label")
        self.song_loaded_status_label.setGeometry(QRect(140, 20, 231, 20))
        self.song_loaded_status_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.song_loaded_status_icon = QLabel(self.groupBox)
        self.song_loaded_status_icon.setObjectName(u"song_loaded_status_icon")
        self.song_loaded_status_icon.setGeometry(QRect(120, 20, 21, 20))
        self.line_2 = QFrame(self.groupBox)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(490, 20, 31, 111))
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.volume_slider = QSlider(self.groupBox)
        self.volume_slider.setObjectName(u"volume_slider")
        self.volume_slider.setGeometry(QRect(510, 32, 22, 97))
        self.volume_slider.setMaximum(100)
        self.volume_slider.setSingleStep(1)
        self.volume_slider.setValue(50)
        self.volume_slider.setOrientation(Qt.Vertical)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.vol_label = QLabel(self.groupBox)
        self.vol_label.setObjectName(u"vol_label")
        self.vol_label.setGeometry(QRect(514, 10, 20, 20))
        LPS_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(LPS_MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1250, 22))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_Settings = QMenu(self.menubar)
        self.menu_Settings.setObjectName(u"menu_Settings")
        self.menu_Help = QMenu(self.menubar)
        self.menu_Help.setObjectName(u"menu_Help")
        self.menu_View = QMenu(self.menubar)
        self.menu_View.setObjectName(u"menu_View")
        LPS_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(LPS_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        LPS_MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Settings.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.menu_File.addAction(self.action_new_lp)
        self.menu_File.addAction(self.action_open_lp)
        self.menu_File.addAction(self.action_save_lp)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_import_lp)
        self.menu_File.addAction(self.action_export_lp)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_open_lpdir)
        self.menu_File.addAction(self.action_open_configdir)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_exit)
        self.menu_Settings.addAction(self.action_settings)
        self.menu_Help.addAction(self.action_help_about)
        self.menu_Help.addAction(self.action_help_oauth)
        self.menu_Help.addAction(self.action_help_docs)
        self.menu_Help.addAction(self.action_help_checkcmds)
        self.menu_View.addAction(self.action_show_log)

        self.retranslateUi(LPS_MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(LPS_MainWindow)
    # setupUi

    def retranslateUi(self, LPS_MainWindow):
        LPS_MainWindow.setWindowTitle(QCoreApplication.translate("LPS_MainWindow", u"LightPlan Studio 1.0", None))
        self.action_help_about.setText(QCoreApplication.translate("LPS_MainWindow", u"&About LightPlan Studio", None))
        self.action_help_oauth.setText(QCoreApplication.translate("LPS_MainWindow", u"&Oauth Token Help", None))
        self.action_new_lp.setText(QCoreApplication.translate("LPS_MainWindow", u"&New LightPlan", None))
        self.action_open_lp.setText(QCoreApplication.translate("LPS_MainWindow", u"&Open LightPlan", None))
        self.action_Wizard.setText(QCoreApplication.translate("LPS_MainWindow", u"&LightPlan Creation Wizard", None))
        self.action_exit.setText(QCoreApplication.translate("LPS_MainWindow", u"&Exit", None))
        self.action_help_docs.setText(QCoreApplication.translate("LPS_MainWindow", u"&Online Help", None))
        self.action_settings.setText(QCoreApplication.translate("LPS_MainWindow", u"&Settings", None))
        self.action_lp_wizard.setText(QCoreApplication.translate("LPS_MainWindow", u"LightPlan Wizard", None))
        self.action_show_log.setText(QCoreApplication.translate("LPS_MainWindow", u"&Show Log", None))
        self.action_save_lp.setText(QCoreApplication.translate("LPS_MainWindow", u"Save LightPlan", None))
        self.action_help_checkcmds.setText(QCoreApplication.translate("LPS_MainWindow", u"&Check for Updated Light Commands", None))
        self.action_open_lpdir.setText(QCoreApplication.translate("LPS_MainWindow", u"Open LightPlan Directory", None))
        self.action_open_configdir.setText(QCoreApplication.translate("LPS_MainWindow", u"Open Config Directory", None))
        self.action_import_lp.setText(QCoreApplication.translate("LPS_MainWindow", u"Import LightPlan", None))
        self.action_export_lp.setText(QCoreApplication.translate("LPS_MainWindow", u"Export LightPlan", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.lightPlanTab), QCoreApplication.translate("LPS_MainWindow", u"LightPlan Explorer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sslTab), QCoreApplication.translate("LPS_MainWindow", u"SSL Queue", None))
        self.LightPlanBox.setTitle(QCoreApplication.translate("LPS_MainWindow", u"LightPlan", None))
        self.label.setText(QCoreApplication.translate("LPS_MainWindow", u"Song Title:  ", None))
        self.label_2.setText(QCoreApplication.translate("LPS_MainWindow", u"Song Artist:  ", None))
        self.label_3.setText(QCoreApplication.translate("LPS_MainWindow", u"Notes:", None))
        self.label_4.setText(QCoreApplication.translate("LPS_MainWindow", u"LP Author:  ", None))
        self.label_5.setText(QCoreApplication.translate("LPS_MainWindow", u"SSL ID:", None))
        self.label_6.setText(QCoreApplication.translate("LPS_MainWindow", u"Spotify ID:", None))
        self.label_7.setText(QCoreApplication.translate("LPS_MainWindow", u"Event Table:", None))
        self.label_8.setText(QCoreApplication.translate("LPS_MainWindow", u"Youtube URL:  ", None))
        self.lp_save_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Save", None))
        self.label_14.setText(QCoreApplication.translate("LPS_MainWindow", u"LightPlan Start:", None))
        self.start_event_edit.setText(QCoreApplication.translate("LPS_MainWindow", u"00:00.000", None))
        self.ssl_lookup_button.setText("")
        self.streamDelayBox.setTitle(QCoreApplication.translate("LPS_MainWindow", u"Stream Delay", None))
        self.calc_delay_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Calculate", None))
        self.label_10.setText(QCoreApplication.translate("LPS_MainWindow", u"Runtime Adjust:", None))
        self.delay_adjust_spinner.setSuffix(QCoreApplication.translate("LPS_MainWindow", u" s", None))
        self.set_delay_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Set", None))
        self.label_11.setText(QCoreApplication.translate("LPS_MainWindow", u"sec", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("LPS_MainWindow", u"Control", None))
        self.control_startlp_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Start LightPlan", None))
        self.twitch_connect_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Connect Twitch", None))
        self.control_lp_progressbar.setFormat(QCoreApplication.translate("LPS_MainWindow", u"Light Event: 0/0", None))
        self.label_9.setText(QCoreApplication.translate("LPS_MainWindow", u"Firing In:", None))
        self.control_lpelapsed_label.setText(QCoreApplication.translate("LPS_MainWindow", u"00:00", None))
        self.label_12.setText(QCoreApplication.translate("LPS_MainWindow", u"Next Event:", None))
        self.control_nextevent_label.setText("")
        self.connected_label.setText(QCoreApplication.translate("LPS_MainWindow", u"0", None))
        self.debug_log_edit.setHtml(QCoreApplication.translate("LPS_MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8.25pt;\"><br /></p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("LPS_MainWindow", u"Debug Log", None))
        self.debug_exportlog_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Export", None))
        self.debug_hidelog_button.setText(QCoreApplication.translate("LPS_MainWindow", u"< Hide", None))
        self.groupBox.setTitle(QCoreApplication.translate("LPS_MainWindow", u"Event Wizard", None))
        self.insert_event_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Insert Event", None))
        self.load_song_button.setText(QCoreApplication.translate("LPS_MainWindow", u"Load", None))
        self.play_button.setText("")
        self.stop_button.setText("")
        self.song_loaded_status_label.setText(QCoreApplication.translate("LPS_MainWindow", u"No Song Loaded", None))
        self.song_loaded_status_icon.setText("")
        self.vol_label.setText(QCoreApplication.translate("LPS_MainWindow", u"TextLabel", None))
        self.menu_File.setTitle(QCoreApplication.translate("LPS_MainWindow", u"&File", None))
        self.menu_Settings.setTitle(QCoreApplication.translate("LPS_MainWindow", u"&Edit", None))
        self.menu_Help.setTitle(QCoreApplication.translate("LPS_MainWindow", u"&Help", None))
        self.menu_View.setTitle(QCoreApplication.translate("LPS_MainWindow", u"&View", None))
    # retranslateUi



# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LPS_SettingsDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGroupBox, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(671, 383)
        self.groupBox = QGroupBox(SettingsDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(340, 90, 321, 121))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 81, 20))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 50, 81, 20))
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 80, 81, 20))
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.userEdit = QLineEdit(self.groupBox)
        self.userEdit.setObjectName(u"userEdit")
        self.userEdit.setGeometry(QRect(100, 20, 201, 20))
        self.oauthEdit = QLineEdit(self.groupBox)
        self.oauthEdit.setObjectName(u"oauthEdit")
        self.oauthEdit.setGeometry(QRect(100, 50, 201, 20))
        self.channelEdit = QLineEdit(self.groupBox)
        self.channelEdit.setObjectName(u"channelEdit")
        self.channelEdit.setGeometry(QRect(100, 80, 201, 20))
        self.groupBox_2 = QGroupBox(SettingsDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(340, 10, 321, 71))
        self.sslCheckBox = QCheckBox(self.groupBox_2)
        self.sslCheckBox.setObjectName(u"sslCheckBox")
        self.sslCheckBox.setGeometry(QRect(20, 30, 181, 21))
        self.saveButton = QPushButton(SettingsDialog)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setGeometry(QRect(480, 350, 75, 23))
        self.cancelButton = QPushButton(SettingsDialog)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setGeometry(QRect(580, 350, 75, 23))
        self.groupBox_3 = QGroupBox(SettingsDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 10, 321, 331))
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 20, 51, 21))
        self.log_level_combo = QComboBox(self.groupBox_3)
        self.log_level_combo.addItem("")
        self.log_level_combo.addItem("")
        self.log_level_combo.setObjectName(u"log_level_combo")
        self.log_level_combo.setGeometry(QRect(70, 20, 69, 22))
        self.showLogCheckBox = QCheckBox(self.groupBox_3)
        self.showLogCheckBox.setObjectName(u"showLogCheckBox")
        self.showLogCheckBox.setGeometry(QRect(170, 20, 141, 21))
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 60, 121, 16))
        self.addCmdButton = QPushButton(self.groupBox_3)
        self.addCmdButton.setObjectName(u"addCmdButton")
        self.addCmdButton.setGeometry(QRect(250, 80, 51, 23))
        self.editCmdButton = QPushButton(self.groupBox_3)
        self.editCmdButton.setObjectName(u"editCmdButton")
        self.editCmdButton.setGeometry(QRect(250, 110, 51, 23))
        self.delCmdButton = QPushButton(self.groupBox_3)
        self.delCmdButton.setObjectName(u"delCmdButton")
        self.delCmdButton.setGeometry(QRect(250, 270, 51, 23))
        self.customCmdListView = QListWidget(self.groupBox_3)
        self.customCmdListView.setObjectName(u"customCmdListView")
        self.customCmdListView.setGeometry(QRect(20, 80, 221, 211))
        self.updateCommandsCheckBox = QCheckBox(self.groupBox_3)
        self.updateCommandsCheckBox.setObjectName(u"updateCommandsCheckBox")
        self.updateCommandsCheckBox.setGeometry(QRect(20, 300, 281, 21))
        self.groupBox_4 = QGroupBox(SettingsDialog)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(340, 220, 321, 121))
        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 20, 111, 21))
        self.dir_edit = QLineEdit(self.groupBox_4)
        self.dir_edit.setObjectName(u"dir_edit")
        self.dir_edit.setGeometry(QRect(10, 50, 301, 22))
        self.dir_edit.setReadOnly(True)
        self.dir_browse_button = QPushButton(self.groupBox_4)
        self.dir_browse_button.setObjectName(u"dir_browse_button")
        self.dir_browse_button.setGeometry(QRect(240, 90, 71, 23))
        self.dir_default_button = QPushButton(self.groupBox_4)
        self.dir_default_button.setObjectName(u"dir_default_button")
        self.dir_default_button.setGeometry(QRect(150, 90, 61, 23))

        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"LightPlanStudio Settings", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsDialog", u"Twitch", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Username:", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"OAuth Token:", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Channel:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingsDialog", u"Streamer Song List", None))
        self.sslCheckBox.setText(QCoreApplication.translate("SettingsDialog", u"Enable Integration", None))
        self.saveButton.setText(QCoreApplication.translate("SettingsDialog", u"Save", None))
        self.cancelButton.setText(QCoreApplication.translate("SettingsDialog", u"Cancel", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SettingsDialog", u"LightPlan Studio", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"Log Level:", None))
        self.log_level_combo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"INFO", None))
        self.log_level_combo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"DEBUG", None))

        self.showLogCheckBox.setText(QCoreApplication.translate("SettingsDialog", u"Show Log on Startup", None))
        self.label_6.setText(QCoreApplication.translate("SettingsDialog", u"Custom Commands:", None))
        self.addCmdButton.setText(QCoreApplication.translate("SettingsDialog", u"Add", None))
        self.editCmdButton.setText(QCoreApplication.translate("SettingsDialog", u"Edit", None))
        self.delCmdButton.setText(QCoreApplication.translate("SettingsDialog", u"Delete", None))
        self.updateCommandsCheckBox.setText(QCoreApplication.translate("SettingsDialog", u"Update Commands on Startup", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SettingsDialog", u"Storage", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"LightPlan Directory:", None))
        self.dir_browse_button.setText(QCoreApplication.translate("SettingsDialog", u"Browse", None))
        self.dir_default_button.setText(QCoreApplication.translate("SettingsDialog", u"Default", None))
    # retranslateUi



# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LPS_SSLMatchDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QHeaderView,
    QLabel, QLineEdit, QProgressBar, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_SSLMatchDialog(object):
    def setupUi(self, SSLMatchDialog):
        if not SSLMatchDialog.objectName():
            SSLMatchDialog.setObjectName(u"SSLMatchDialog")
        SSLMatchDialog.resize(277, 347)
        self.save_button = QPushButton(SSLMatchDialog)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setGeometry(QRect(100, 310, 75, 24))
        self.cancel_button = QPushButton(SSLMatchDialog)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QRect(190, 310, 75, 24))
        self.status_label = QLabel(SSLMatchDialog)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setGeometry(QRect(10, 10, 251, 21))
        self.song_table = QTableWidget(SSLMatchDialog)
        if (self.song_table.columnCount() < 2):
            self.song_table.setColumnCount(2)
        self.song_table.setObjectName(u"song_table")
        self.song_table.setGeometry(QRect(10, 71, 256, 231))
        self.song_table.setAlternatingRowColors(True)
        self.song_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.song_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.song_table.setSortingEnabled(True)
        self.song_table.setColumnCount(2)
        self.song_table.horizontalHeader().setStretchLastSection(True)
        self.song_table.verticalHeader().setVisible(False)
        self.search_edit = QLineEdit(SSLMatchDialog)
        self.search_edit.setObjectName(u"search_edit")
        self.search_edit.setGeometry(QRect(52, 40, 211, 22))
        self.label = QLabel(SSLMatchDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 40, 49, 21))
        self.progress = QProgressBar(SSLMatchDialog)
        self.progress.setObjectName(u"progress")
        self.progress.setGeometry(QRect(10, 310, 81, 23))
        self.progress.setMaximum(0)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        self.retranslateUi(SSLMatchDialog)

        QMetaObject.connectSlotsByName(SSLMatchDialog)
    # setupUi

    def retranslateUi(self, SSLMatchDialog):
        SSLMatchDialog.setWindowTitle(QCoreApplication.translate("SSLMatchDialog", u"Dialog", None))
        self.save_button.setText(QCoreApplication.translate("SSLMatchDialog", u"Save", None))
        self.cancel_button.setText(QCoreApplication.translate("SSLMatchDialog", u"Cancel", None))
        self.status_label.setText(QCoreApplication.translate("SSLMatchDialog", u"asdf", None))
        self.label.setText(QCoreApplication.translate("SSLMatchDialog", u"Search:", None))
    # retranslateUi



