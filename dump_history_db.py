from __future__ import print_function
# coding: utf-8
import sqlite3
db = sqlite3.connect('history.db')
c = db.cursor()
r = c.execute('select * from history')
res = r.fetchall()
print(res)
