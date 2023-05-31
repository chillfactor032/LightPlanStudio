#Python Imports
import time
import keyboard
import requests
import sqlite3
import json
from enum import Enum, auto

#PySide6 Imports
from PySide6.QtCore import QRunnable, Signal, Slot, QObject, Qt, QAbstractTableModel, QEvent
from PySide6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QMenu, QStyledItemDelegate, QStyle, QPushButton, QTreeWidgetItem
from PySide6.QtGui import QAction, QCursor, QStandardItemModel, QStandardItem

#LightPlan Imports
import irc.client
from twitchio.ext import commands
from pytube import YouTube
import socketio

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

class FolderTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, name, folder_data):
        super(FolderTreeWidgetItem, self).__init__(name)
        self.folder_data = folder_data

class TreeItemType(Enum):
    FOLDER = "Folder"
    ARTIST = "Artist"
    LIGHTPLAN = "LightPlan"

    def __str__(self):
        return str(self.value)

class LightPlanDB():

    class Signals(QObject):
        log = Signal(str, LogLevel)

    def __init__(self, version, path):
        self.version = version
        self.path = path
        self.signals = self.Signals()
        self.connection = sqlite3.connect(self.path)
        if self.connection:
            self.log("Connected to LightPlan Database", LogLevel.INFO)
        else:
            self.log("Error connecting to the LightPlan Database", LogLevel.ERROR)
        self.init_db()

    def init_db(self):
        #Initialize the DB if its empty (on first run)
        cursor = self.connection.cursor()
        lp_data = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lps_data';").fetchall()
        lp_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lightplans';").fetchall()
        folder_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='folders';").fetchall()
        event_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';").fetchall()
        if len(lp_table) == 0  or len(folder_table) == 0 or len(event_table) == 0:
            self.log(f"Initializing database for first use.")
            sql = """CREATE TABLE IF NOT EXISTS lps_data (
                name TEXT,
                data TEXT
            );
            """
            try:
                cursor.execute(sql)
            except Exception as e:
                self.log(str(e), LogLevel.ERROR)
            sql = """CREATE TABLE IF NOT EXISTS folders (
                folder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER DEFAULT 0,
                name TEXT
            );
            """
            try:
                cursor.execute(sql)
            except Exception as e:
                self.log(str(e), LogLevel.ERROR)
            sql = """CREATE TABLE IF NOT EXISTS lightplans (
                lightplan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER DEFAULT 0,
                title TEXT,
                artist TEXT,
                author TEXT,
                ssl_id INTEGER,
                spotify_id INTEGER,
                video_url TEXT,
                notes TEXT,
                starting_ms INTEGER
            );
            """
            try:
                cursor.execute(sql)
            except Exception as e:
                self.log(str(e), LogLevel.ERROR)
            sql = """CREATE TABLE IF NOT EXISTS events (
                lightplan_id INTEGER,
                offset INTEGER,
                command TEXT,
                comment TEXT,
                ignore_delay INTEGER
            );
            """
            try:
                cursor.execute(sql)
            except Exception as e:
                self.log(str(e), LogLevel.ERROR)
            cursor.execute("INSERT INTO folders (name) VALUES ('LiveLearn')")
            self.set_data("version", self.version)
            self.connection.commit()
    
    def get_data(self, name):
        sql = f"SELECT data FROM lps_data WHERE name=?;"
        cursor = self.connection.cursor()
        try:
            row = cursor.execute(sql, [name]).fetchone()
            self.connection.commit()
            if row:
                return row[0]
            return None
        except Exception as e:
            self.log(f"Could not fetch data [{name}]", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None

    def set_data(self, name, data):
        old_data = self.get_data(name)
        if old_data == data:
            return
        
        #Data doesnt exist yet
        if not old_data:
            sql = f"INSERT INTO lps_data (name, data) VALUES (?, ?);"
            cursor = self.connection.cursor()
            try:
                row = cursor.execute(sql, [name, data])
                self.connection.commit()
            except Exception as e:
                self.log(f"Could not set data [{name}] = [{data}]", LogLevel.ERROR)
                self.log(str(e), LogLevel.ERROR)
                return None
        else:
            sql = f"UPDATE lps_data SET data=? WHERE name=?;"
            cursor = self.connection.cursor()
            try:
                row = cursor.execute(sql, [data, name])
                self.connection.commit()
            except Exception as e:
                self.log(f"Could not set data [{name}] = [{data}]", LogLevel.ERROR)
                self.log(str(e), LogLevel.ERROR)
                return None

    def fetch_all_folders(self):
        sql = f"SELECT * FROM folders;"
        cursor = self.connection.cursor()
        folders = []
        try:
            rows = cursor.execute(sql).fetchall()
            for row in rows:
                folder = {
                    "folder_id": row[0],
                    "parent_id": row[1],
                    "name": row[2]
                }
                folders.append(folder)
            self.connection.commit()
            return folders
        except Exception as e:
            self.log(f"Could not fetch all folders", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None

    def fetch_folder(self, folder_id):
        sql = f"SELECT * FROM folders WHERE folder_id =?;"
        cursor = self.connection.cursor()
        try:
            row = cursor.execute(sql, [folder_id]).fetchone()
            folder = {
                "folder_id": row[0],
                "parent_id": row[1],
                "name": row[2]
            }
            self.connection.commit()
            return folder
        except Exception as e:
            self.log(f"Could not fetch folder {folder_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None

    def fetch_orphan_folders(self):
        orphans = []
        cursor = self.connection.cursor()
        #Root folders are never orphans
        sql = """
        SELECT f.folder_id, f.parent_id, f.name, (
            CASE WHEN f.parent_id = 0 
            THEN True 
            ELSE (
                CASE WHEN p.folder_id IS NULL
                THEN False
                ELSE True
                END)
            END) as parent_exists
        FROM folders f
        LEFT JOIN folders p
            ON f.parent_id = p.folder_id
        """
        try:
            rows = cursor.execute(sql).fetchall()
            for row in rows:
                if row[3] == 0:
                    obj = {
                        "folder_id": row[0],
                        "parent_id": row[1],
                        "name": row[2],
                    }
                    orphans.append(obj)
        except Exception as e:
            self.log(f"Could not find orphaned folders", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None
        return orphans

    def fetch_orphan_lightplans(self):
        orphans = []
        cursor = self.connection.cursor()
        sql = """
        SELECT lp.lightplan_id, lp.artist, lp.title, (
            CASE WHEN lp.folder_id = 0
            THEN True
            ELSE (
                CASE WHEN f.folder_id IS NULL
                THEN False
                ELSE True
                END)
            END) as parent_exists
        FROM lightplans lp
        LEFT JOIN folders f
            ON lp.folder_id = f.folder_id
        """
        try:
            rows = cursor.execute(sql).fetchall()
            for row in rows:
                    if row[3] == 0:
                        obj = {
                            "lightplan_id": row[0],
                            "song_artist": row[1],
                            "song_title": row[2]
                        }
                        orphans.append(obj)
        except Exception as e:
            self.log(f"Could not find orphaned lightplans", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None
        return orphans

    def delete_folder(self, folder_id, recurse=True):
        cursor = self.connection.cursor()
        sql = f"DELETE FROM folders WHERE folder_id = ?;"
        try:
            result = cursor.execute(sql, [folder_id])
            self.connection.commit()
            if recurse == False:
                return True

            # Cascade delete to orphaned folders
            orphan_folders = self.fetch_orphan_folders()
            while len(orphan_folders) > 0:
                for folder in orphan_folders:
                    self.log(f"Cascading delete to orphan folder {folder['name']}")
                    self.delete_folder(folder["folder_id"], False)
                orphan_folders = self.fetch_orphan_folders()

            # Cascade delete to orphaned Lightplans
            orphan_lps = self.fetch_orphan_lightplans()
            for lps in orphan_lps:
                self.log(f"Cascading delete to orphan lightplan {lps['song_artist']} - {lps['song_title']}")
                self.delete_lightplan(lps["lightplan_id"])
            return True
        except Exception as e:
            self.log(f"Could not delete folder {folder_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def delete_lightplan(self, lightplan_id):
        cursor = self.connection.cursor()
        sql = f"DELETE FROM lightplans WHERE lightplan_id = ?;"
        try:
            self.clear_events_from_lightplan(lightplan_id)
            result = cursor.execute(sql, [lightplan_id])
            self.connection.commit()
            return True
        except Exception as e:
            self.log(f"Could not delete lightplan {lightplan_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def clear_events_from_lightplan(self, lightplan_id):
        cursor = self.connection.cursor()
        sql = f"DELETE FROM events WHERE lightplan_id=?;"
        try:
            result = cursor.execute(sql, [lightplan_id])
            self.connection.commit()
            return True
        except Exception as e:
            self.log(f"Could not remove events for LightPlan {lightplan_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def rename_folder(self, folder_id, new_name):
        cursor = self.connection.cursor()
        sql = f"UPDATE folders SET name = ? WHERE folder_id = ?;"
        try:
            params = [
                new_name,
                folder_id
            ]
            result = cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.log("Could not Rename folder - id: {folder_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def create_folder(self, parent_id, name):
        cursor = self.connection.cursor()
        sql = f"INSERT INTO folders (parent_id, name) VALUES (?,?);"
        try:
            params = [
                parent_id,
                name
            ]
            result = cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.log("Could create folder ({folder_id})", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def move_folder(self, folder_id, new_parent_id):
        cursor = self.connection.cursor()
        sql = f"UPDATE folders SET parent_id = ? WHERE folder_id = ?;"
        try:
            params = [
                new_parent_id,
                folder_id
            ]
            result = cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.log(f"Error setting new parent ({new_parent_id}) for folder ({folder_id})", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def move_lightplan(self, lightplan_id, new_folder_id):
        cursor = self.connection.cursor()
        sql = f"UPDATE lightplans SET folder_id = ? WHERE lightplan_id = ?;"
        try:
            params = [
                new_folder_id,
                lightplan_id
            ]
            result = cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.log(f"Error setting new parent ({new_folder_id}) for lightplan ({lightplan_id})", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def insert_events_for_lightplan(self, lightplan_id, events):
        num_events = len(events)
        cursor = self.connection.cursor()
        try:
            rows_to_insert = []
            sql = "INSERT INTO events (lightplan_id, offset, command, comment, ignore_delay) VALUES (?,?,?,?,?);"
            for event in events:
                ignore_delay = 0
                if event["ignore_delay"]:
                    ignore_delay = 1
                rows_to_insert.append((lightplan_id,event["offset"],event["command"],event["comment"],ignore_delay))
            cursor.executemany(sql, rows_to_insert)
            self.connection.commit()
            return True
        except Exception as e:
            self.log(f"Could not insert {num_events} events for LightPlan {lightplan_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def update_lightplan(self, lp_dict):
        inserted_id = None
        self.log(f"Saving LightPlan {lp_dict['song_artist']} - {lp_dict['song_title']}", LogLevel.INFO)
        try:
            lp_dict["ssl_id"] = int(lp_dict["ssl_id"])
        except ValueError:
            lp_dict["ssl_id"] = "NULL"
        try:
            lp_dict["spotify_id"] = int(lp_dict["spotify_id"])
        except ValueError:
            lp_dict["spotify_id"] = "NULL"
        try:
            lp_dict["starting_ms"] = int(lp_dict["starting_ms"])
        except ValueError:
            lp_dict["starting_ms"] = "NULL"
        cursor = self.connection.cursor()
        sql = f"""UPDATE lightplans
            SET
                title = ?,
                artist = ?,
                author = ?,
                ssl_id = ?,
                spotify_id = ?,
                video_url = ?,
                notes = ?,
                starting_ms = ?
            WHERE lightplan_id = ?;
        """
        try:
            params = [
                lp_dict["song_title"],
                lp_dict["song_artist"],
                lp_dict["author"],
                lp_dict["ssl_id"],
                lp_dict["spotify_id"],
                lp_dict["video_url"],
                lp_dict["notes"],
                lp_dict["starting_ms"],
                lp_dict["lightplan_id"]
            ]
            result = cursor.execute(sql, params)
            self.connection.commit()
            self.clear_events_from_lightplan(lp_dict["lightplan_id"])
            self.insert_events_for_lightplan(lp_dict["lightplan_id"], lp_dict["events"])
            return True
        except Exception as e:
            self.log("Could not Save/Import LightPlan", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return False

    def insert_lightplan(self, lp_dict, folder_id=0):
        inserted_id = None
        self.log(f"Importing LightPlan {lp_dict['song_artist']} - {lp_dict['song_title']}", LogLevel.INFO)
        cursor = self.connection.cursor()
        sql = f"SELECT count(lightplan_id) FROM lightplans WHERE artist = '{lp_dict['song_artist']}' AND title = '{lp_dict['song_title']}';"
        result = cursor.execute(sql).fetchone()
        if result and result[0] > 0:
            self.log(str(result), LogLevel.DEBUG)
            self.log("This lightplan already exists!", LogLevel.INFO)
            return
        try:
            lp_dict["ssl_id"] = int(lp_dict["ssl_id"])
        except ValueError:
            lp_dict["ssl_id"] = "NULL"
        
        try:
            lp_dict["spotify_id"] = int(lp_dict["spotify_id"])
        except ValueError:
            lp_dict["spotify_id"] = "NULL"

        try:
            lp_dict["starting_ms"] = int(lp_dict["starting_ms"])
        except ValueError:
            lp_dict["starting_ms"] = "NULL"

        sql = f"""INSERT INTO lightplans (folder_id, title, artist, author, ssl_id, spotify_id, video_url,  notes, starting_ms) 
            VALUES (
                {folder_id},
                '{lp_dict['song_title']}',
                '{lp_dict['song_artist']}',
                '{lp_dict['author']}',
                {lp_dict['ssl_id']},
                {lp_dict['spotify_id']},
                '{lp_dict['youtube_url']}',
                '{lp_dict['notes']}',
                {lp_dict['starting_ms']}
            );
        """
        try:
            result = cursor.execute(sql)
            self.connection.commit()
            inserted_id = cursor.lastrowid
            lp_id = cursor.execute(f"SELECT lightplan_id FROM lightplans WHERE rowid = {cursor.lastrowid};").fetchone()[0]
            self.insert_events_for_lightplan(lp_id, lp_dict["events"])
            return inserted_id
        except Exception as e:
            self.log("Could not import LightPlan")
            self.log(str(e), LogLevel.ERROR)
            return None

    def get_children_folders(self, parent_id):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM folders WHERE parent_id=?;"
        try:
            rows = cursor.execute(sql, [parent_id]).fetchall()
        except Exception as e:
            self.log(f"Error fetching all folders", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None
        folders = []
        for row in rows:
            folder = {
                "folder_id": row[0],
                "parent_id": row[1],
                "name": row[2]
            }
            folders.append(folder)
        return folders

    def fetch_all_folders(self):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM folders;"
        try:
            rows = cursor.execute(sql).fetchall()
        except Exception as e:
            self.log(f"Error fetching all folders", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None
        folders = []
        for row in rows:
            folder = {
                "folder_id": row[0],
                "parent_id": row[1],
                "name": row[2]
            }
            folders.append(folder)
        return folders
        
    def fetch_lightplan(self, lightplan_id):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM lightplans WHERE lightplan_id=?;"
        try:
            row = cursor.execute(sql, [lightplan_id]).fetchone()
        except Exception as e:
            self.log(f"Error fetching LightPlan with Id: {lightplan_id}", LogLevel.ERROR)
            self.log(str(e), LogLevel.ERROR)
            return None
        lightplan_dict = {
            "lightplan_id": row[0],
            "folder_id": row[1],
            "song_title": row[2],
            "song_artist": row[3],
            "author": row[4],
            "ssl_id": row[5],
            "spotify_id": row[6],
            "video_url": row[7],
            "notes": row[8],
            "starting_ms": row[9],
            "events": []
        }
        sql = f"SELECT * FROM events WHERE lightplan_id = ?;"
        rows = cursor.execute(sql, [lightplan_id]).fetchall()
        for row in rows:
            ignore_delay = False
            if row[4]:
                ignore_delay = True
            event_dict = {
                "offset": row[1],
                "command": row[2],
                "comment": row[3],
                "ignore_delay": ignore_delay
            }
            lightplan_dict["events"].append(event_dict)            
        return lightplan_dict

    def fetch_all_lightplans(self, full_data=False):
        lps = []
        cursor = self.connection.cursor()
        sql = "SELECT * FROM lightplans;"
        try:
            lps_rows = cursor.execute(sql).fetchall()
        except Exception as e:
            self.log(str(e), LogLevel.ERROR)
            return None
        for lp in lps_rows:
            lightplan_dict = {
                "lightplan_id": lp[0],
                "folder_id": lp[1],
                "song_title": lp[2],
                "song_artist": lp[3],
                "author": lp[4],
                "ssl_id": lp[5],
                "spotify_id": lp[6],
                "video_url": lp[7],
                "notes": lp[8],
                "starting_ms": lp[9],
                "events": []
            }
            if full_data:
                sql = f"SELECT * FROM events WHERE lightplan_id = {lp[0]};"
                rows = cursor.execute(sql).fetchall()
                for row in rows:
                    ignore_delay = False
                    if row[4]:
                        ignore_delay = True
                    event_dict = {
                        "offset": row[1],
                        "command": row[2],
                        "comment": row[3],
                        "ignore_delay": ignore_delay
                    }
                    lightplan_dict["events"].append(event_dict)     
            lps.append(lightplan_dict)                
        return lps

    def log(self, msg, level=LogLevel.DEBUG):
        self.signals.log.emit(msg, level)


class SSLButton(QPushButton):
    def __init__(self, *args, **kwargs):
        self.data = {}
        super().__init__(*args, **kwargs)

    def setData(self, data):
        self.data = data
    

class StreamerSongList(QRunnable):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        disconnected = Signal()
        connected = Signal()
        join_room = Signal()
        queue_update = Signal(dict)

    def __init__(self, ssl_id=0, url="https://api.streamersonglist.com"):
        super(StreamerSongList, self).__init__()
        self.signals = self.Signals()
        self.sio = socketio.Client()
        self.ssl_id = ssl_id
        self.ssl_user = ""
        self.url = url
        self.sio.on("connect", self.connectEvent)
        self.sio.on("connect_error", self.connectErrorEvent)
        self.sio.on("disconnect", self.disconnectEvent)
        self.sio.on("queue-update", self.queue_update)
        self._connected = False

    @Slot()
    def run(self):
        self.sio.connect(self.url)
        self.sio.wait()
    
    def close(self):
        self.sio.disconnect()

    def fetch_queue(self):
        if not self._connected:
            return
        url = f"https://api.streamersonglist.com/v1/streamers/{self.ssl_id}/queue"
        self.log(f"Fetching SSL Queue via HTTP: {url}", LogLevel.DEBUG)
        r = requests.get(url)
        if not r.status_code == 200:
            self.log(f"Error fetching SSL Queue: HTTP Status [{r.status_code}]", LogLevel.ERROR)
            return
        jsonObj = r.json()
        self.queue_update(jsonObj)

    def queue_update(self, data):
        self.log(f"SSL Queue Update Event", LogLevel.DEBUG)
        queue = []
        for item in data["list"]:
            song = item["song"]
            queue.append(song)
        self.log(f"{queue}", LogLevel.DEBUG)
        self.signals.queue_update.emit(queue)

    def connectEvent(self):
        self._connected = True
        self.log(f"SSL Status: Connected", LogLevel.INFO)
        self.sio.emit("join-room", str(self.ssl_id))
        self.signals.log.emit(f"Joined room {self.ssl_id}", LogLevel.INFO)
        self.fetch_queue()

    def connectErrorEvent(self, msg=""):
        self.signals.log.emit(f"Connection to StreamerSongList Failed", LogLevel.ERROR)
        self.signals.log.emit(msg, LogLevel.ERROR)

    def disconnectEvent(self):
        self._connected = False
        self.signals.log.emit(f"Disconnected to StreamerSongList", LogLevel.INFO)
        self.signals.disconnected.emit()

    def disconnect(self):
        self.sio.disconnect()

    def update_sslid(self, ssl_id):
        self.ssl_id = ssl_id

    def sslId_from_user(self, ssl_user):
        url = "https://api.streamersonglist.com/v1/streamers/"+str(ssl_user)
        response = requests.get(url)
        id = 0
        if(response.status_code == 200):
            try:
                jsonObj = response.json()
                id = jsonObj["id"]
            except ValueError as err:
                self.log(repr(err), LogLevel.ERROR)
                id = 0
                return False
        if(id != 0):
            self.ssl_id = id
            self.ssl_user = ssl_user
            self.log(f"SSL ID Retrieved: {id}")
            return True
        else:
            return False

    def get_user(self):
        return self.ssl_user

    def connected(self):
        return self._connected

    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)


class LightPlanRunner(QRunnable):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        progress = Signal(int, float, str, int)
        done = Signal(str)
        privmsg = Signal(str)

    def __init__(self, lightplan_dict=None, stream_delay=0, adjust=0, start_ms=0, starting_index=0):
        super(LightPlanRunner, self).__init__()
        self.signals = self.Signals()
        self.lightplan_dict = lightplan_dict
        self.events = self.lightplan_dict["events"].copy()
        # Remember the original order
        for x in range(0, len(self.events)):
            self.events[x]["original_index"] = x
        self.stream_delay_ms = stream_delay
        self.runtime_adjust_ms = adjust
        self.running = False
        self.lp_stopped = False
        self.start_time = 0
        self.elapsed_time = 0
        self.start_ms = self.lightplan_dict["starting_ms"]
        self.cur_index = starting_index

    def update_runtime_adjustment(self, adjust_ms):
        self.runtime_adjust_ms = adjust_ms

    def stop(self):
        self.lp_stopped = True

    def is_running(self):
        return self.running

    def run(self):
        num_events = len(self.events) 

        #If no events, dont even bother
        if(num_events==0):
            self.done("No Events To Process")
            return

        # Initialize some variables
        start_time = time.time()
        self.running = True
        elapsed_time_ms = 0
        current_event = None
        played_event_count = 0
        self.log("LightPlan Started")
        
        # Calculate the true offset factoring in "ignore_delay" and start_ms
        for evt in self.events:
            calculated_offset = evt["offset"]-self.start_ms
            if(not evt["ignore_delay"]):
                calculated_offset -= self.stream_delay_ms
            evt["offset"] = calculated_offset

        #Sort the events chronologically
        self.events.sort(key = lambda i: i['offset'])

        # Initialize the first event and send progress to the GUI Thread
        current_event = self.events.pop(0)
        self.progress(0, round(current_event["offset"]/1000,1), current_event["command"], -1)

        # Begin LightPlanRunner Loop
        while self.running == True:
            # Check to see if LP has been stopped
            if(self.lp_stopped):
                self.done("LightPlan Stopped")
                return

            #Update the time elapsed since LPR started
            elapsed_time_ms = int((time.time()-start_time)*1000)

            #Check to see if any events need firing
            if(elapsed_time_ms >= (current_event["offset"]+self.runtime_adjust_ms)):
                #Calculate the error (number of ms off target)
                error_str = ""
                error = elapsed_time_ms - current_event['offset']
                if(error<0):
                    error_str = f" -{error}ms"
                if(error>0):
                    error_str = f" +{error}ms"

                #Fire the event
                self.fire(current_event['command'], error_str)

                # Send the progress update to GUI Thread
                fired_index = current_event['original_index']
                played_event_count += 1
                if(len(self.events)>0):
                    current_event = self.events.pop(0)
                    self.progress(played_event_count, round(current_event["offset"]/1000,1), current_event["command"], fired_index)
                else:
                    # No more events. Done
                    self.done("LightPlan Complete")
                    return
            time.sleep(0.0001)

    def fire(self, msg, error = ""):
        self.signals.privmsg.emit(msg)
        self.log(f"Fired: {msg}{error}")

    def progress(self, cur_evt_num, event_count, next_command, orig_index):
        self.signals.progress.emit(cur_evt_num, event_count, next_command, orig_index)

    def done(self, msg):
        self.running = False
        self.log(msg)
        self.signals.done.emit(msg)

    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)


class LightPlanTreeItem(QStandardItem):
    def __init__(self, name, item_type=TreeItemType.LIGHTPLAN):
        super(LightPlanTreeItem, self).__init__(name)
        self.name = name
        self.parent_id = 0
        self.id = 0
        self.artist = ""
        self.title = ""
        self.is_lightplan = True
        self.id = 0
        self.item_type = item_type

    def setParentId(self, id):
        self.parent_id = id
    
    def setId(self, id):
        self.id = id

    def setArtist(self, artist):
        self.artist = artist

    def setTitle(self, title):
        self.title = title

    def get_type(self):
        return self.item_type


class LightPlanTreeModel(QStandardItemModel):

    def __init__(self):
        super(LightPlanTreeModel, self).__init__()

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData(data, action, row, column, parent):
        print(f"Drop Event")
        print(data)

    def getItemAt(pos):
        pass


class KeyListener(QRunnable):

    class Signals(QObject):
        key_event = Signal()
        log = Signal(str, LogLevel)

    def __init__(self):
        super(KeyListener, self).__init__()
        self.signals = self.Signals()
        self._done = False

    def run(self):
        hotkey = keyboard.add_hotkey('space', lambda: self.signals.key_event.emit())
        self.log("KeyEvent Listener {SPACE} Started", LogLevel.DEBUG)

        while not self._done:
            time.sleep(0.1)
        
        keyboard.remove_hotkey(hotkey)
        self.log("KeyEvent Listener {SPACE} Stopped", LogLevel.DEBUG)

    def die(self):
        self._done = True
        
    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)


class KeyEventEater(QObject):
    def __init__(self):
        super(KeyEventEater, self).__init__()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.KeyPress):
            return True
        else:
            return super().eventFilter(obj, event)


class TwitchIRC(QRunnable):

    class Signals(QObject):
        log = Signal(str, LogLevel)
        irc_disconnect = Signal()
        irc_connect = Signal()
        connect_failed = Signal()

    def __init__(self, nickname, token, channel, server="irc.chat.twitch.tv", port=6667):
        super(TwitchIRC, self).__init__()
        self._connect_failed = True
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
        self._connect_failed = False
        connection.join(self.channel)
        self.signals.irc_connect.emit()

    def on_join(self, connection, event):
        self.log(f"Joined channel {self.channel}")

    def on_disconnect(self, connection, event):
        if(self._connect_failed):
            self.log("irc.chat.twitch.tv connection failed", LogLevel.ERROR)
            self.signals.connect_failed.emit()
        else:
            self.log("Disconnected from irc.chat.twitch.tv")
            self.signals.irc_disconnect.emit()
        self.stop = True
        
    def privmsg(self, text):
        if(self.connected()):
            self.log(f"Sent: {text}", LogLevel.DEBUG)
            self.connection.privmsg(self.channel, text)
    
    def disconnect(self):
        self.reactor.disconnect_all()
    
    def run(self):
        try:
            self.connect()
        except irc.client.ServerConnectionError as err:
            self.log(repr(err), LogLevel.ERROR)

        while not self.stop:
            self.reactor.process_once()
            time.sleep(0.001)
        self.disconnect()

    def die(self):
        self.stop = True

    def connect(self):
        try:
            self.connection = self.reactor.server().connect(self.server, self.port, self.nickname, self.token)
        except irc.client.ServerConnectionError as err:
            self.log(repr(err), LogLevel.ERROR)
            raise
        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("join", self.on_join)
        self.connection.add_global_handler("disconnect", self.on_disconnect)

    def log(self, msg, level=LogLevel.INFO):
        self.signals.log.emit(msg, level)
    

class YoutubeVideoInfo(QRunnable):

    class Signals(QObject):
        done = Signal(dict)
        log = Signal(str, LogLevel)
        
    def __init__(self, api_key, video_id):
        super(YoutubeVideoInfo, self).__init__()
        self.api_key = api_key
        self.video_id = video_id
        self.signals = YoutubeVideoInfo.Signals()
    
    def get_info(self):
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&id={self.video_id}&key={self.api_key}"
        headers = {
            "Accept": "application/json"
        }
        r = requests.get(url, headers=headers)
        self.signals.log.emit(r.text, LogLevel.DEBUG)
        if r.status_code >= 200 and r.status_code < 400:
            try:
                return r.json()
            except json.decoder.JSONDecodeError as e:
                self.signals.log.emit("Error processing response from Youtube API", LogLevel.INFO)
                self.signals.log.emit(str(e), LogLevel.ERROR)
        else:
            self.signals.log.emit(f"Error status code {r.status_code} from Youtube API", LogLevel.ERROR)
        return None

    @Slot()
    def run(self):
        result = {
            "error": False,
            "us_blocked": False,
            "au_blocked": False
        }
        info = self.get_info()
        if not info:
            result["error"] = True
        else:
            blocked = info["items"][0]["contentDetails"]["regionRestriction"]["blocked"]
            result["us_blocked"] = "US" in blocked
            result["au_blocked"] = "AU" in blocked
        self.signals.done.emit(result)


class YoutubeDownloader(QRunnable):

    class Signals(QObject):
        done = Signal(bool, dict)
        log = Signal(str, LogLevel)
        
    def __init__(self, youtube_url, save_dir, filename="tmp.mp4"):
        super(YoutubeDownloader, self).__init__()
        self.youtube_url = youtube_url
        self.save_dir = save_dir
        self.audio_path = ""
        self.image_path = ""
        self.filename = filename
        self.result = {}
        self.signals = YoutubeDownloader.Signals()
        
    def result(self):
        return self.result
        
    @Slot()
    def run(self):
        try:
            self.signals.log.emit(f"Youtube URL [{self.youtube_url}]", LogLevel.DEBUG)
            self.youtube_obj = YouTube(self.youtube_url)
            print(self.youtube_obj.vid_info)
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
            self.audio_path = stream.download(self.save_dir, self.filename) 
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
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.addItems([""])
        editor.addItems(self.model.commands)
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
        
    def rowCount(self, parent=None):
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
        