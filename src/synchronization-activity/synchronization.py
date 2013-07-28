import goocanvas
import gcompris
import gcompris.utils
import gcompris.skin
import gcompris.admin
import gtk
import gtk.gdk
import pango
import urllib2
import json
import datetime
import sys
import datetime
import time
import traceback

from gcompris import gcompris_gettext as _

import math

# Database
try:
  from sqlite3 import dbapi2 as sqlite # python 2.5
except:
  try:
    from pysqlite2 import dbapi2 as sqlite
  except:
    print 'This program requires pysqlite2\n',\
        'http://initd.org/tracker/pysqlite/'
    sys.exit(1)

#
# The name of the class is important. It must start with the prefix
# 'Gcompris_' and the last part 'synchronization' here is the name of
# the activity and of the file in which you put this code. The name of
# the activity must be used in your menu.xml file to reference this
# class like this: type="python:synchronization"
#
class Gcompris_synchronization:
  """Empty gcompris Python class"""


  def __init__(self, gcomprisBoard):
    print "synchronization init"
    self.gcomprisBoard = gcomprisBoard

    self.gcomprisBoard.disable_im_context = True
    # Connect to our database
    self.con = sqlite.connect(gcompris.get_database())
    self.cur = self.con.cursor()

  def start(self):
    self.gcomprisBoard.level=1
    self.gcomprisBoard.maxlevel=1
    self.gcomprisBoard.sublevel=1
    self.gcomprisBoard.number_of_sublevel=1
    
    self.user = gcompris.admin.get_current_user()

    # Get the default profile
    self.Prop = gcompris.get_properties()

    # get the user date
    self.cur.execute("select to_server_date from sync_status where login = '"+self.user.login+"'");
    sync_status_data = self.cur.fetchall();
    to_server_date = None

    for sync_status_row in sync_status_data:
      to_server_date = sync_status_row[0]

    # Grab the user log data
    if to_server_date is None :
      query = "select date as Date, duration as Duration, u.login as Login ,b.name as BoardName, level as Level, \
                     sublevel as SubLevel, status as Status from logs l inner join users u on u.user_id = l.user_id \
                     inner join boards b on b.board_id = l.board_id"
    else :
      query = "select date as Date, duration as Duration, u.login as Login ,b.name as BoardName, level as Level, \
                     sublevel as SubLevel, status as Status from logs l inner join users u on u.user_id = l.user_id \
                     inner join boards b on b.board_id = l.board_id where l.date > '" + str(to_server_date) + "'"


    self.cur.execute(query)
    log_data = self.cur.fetchall()

    logs = []

    for log_row in log_data:
      log = dict()
      log_date = datetime.datetime.strptime(log_row[0], '%Y-%m-%d %H:%M:%S')
      log_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.mktime(log_date.timetuple())))
      log["date"] = log_date_utc
      log["duration"] = log_row[1]
      log["login"] = log_row[2]
      log["boardname"] = log_row[3]
      log["level"] = log_row[4]
      log["sublevel"] = log_row[5]
      log["status"] = log_row[6]
      logs.append(log)

    if(len(logs) > 0) :
      json_data = json.dumps(logs)

      #post data to /logs/{login}
      print "JSON POST: " + json_data
      url =  self.Prop.backendurl + 'logs'
      print url
      req = urllib2.Request(url, json_data, {"Content-Type": "application/json", "accept": "application/json"})
      f = urllib2.urlopen(req)
      response = f.read()
      print response
      f.close()
      self.cur.execute("update sync_status set to_server_date = '" + str(datetime.datetime.now()) + 
                       "', from_server_date = '" + str(datetime.datetime.now()) + # this is to ensure that same records don't come back
                       "' where login = '" + self.user.login + "'");
      self.con.commit();
      self.end();

  def end(self):
    print "synchronization end"
