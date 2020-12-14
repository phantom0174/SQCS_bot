import json
import sqlite3

with open('./jsons/setting.json', mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

connection = sqlite3.connect('DataBase.db')
info = connection.cursor()

# info.execute('DROP TABLE quiz;')

info.execute("""CREATE TABLE IF NOT EXISTS quiz (
      Id INTEGER,
      Crt INTEGER);""")

info.execute("""CREATE TABLE IF NOT EXISTS lecture (
      Id INTEGER,
      Score REAL,
      Count INTEGER);""")

info.execute("""CREATE TABLE IF NOT EXISTS lecture_list (
      Name TEXT,
      Week INTEGER);""")

info.connection.commit()
