#import pymysql
#from model import database as db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import hashlib

from models import db

"""
TABLE songs
+--------+--------------+------+-----+---------+----------------+
| Field  | Type         | Null | Key | Default | Extra          |
+--------+--------------+------+-----+---------+----------------+
| no     | int(11)      | NO   | PRI | NULL    | auto_increment |
| owner  | int(11)      | NO   | PRI | NULL    |                |
| title  | varchar(100) | NO   |     | NULL    |                |
| artist | varchar(100) | YES  |     | NULL    |                |
| cover  | char(32)     | YES  |     | NULL    |                |
| file   | varchar(100) | NO   |     | NULL    |                |
| p      | char(32)     | NO   |     | NULL    |                |
+--------+--------------+------+-----+---------+----------------+
"""

class Song(db.Model):
	__tablename__ = 'songs'
	no = db.Column(db.Integer, primary_key=True, autoincrement=True)
	owner = db.Column(db.Integer, ForeignKey('users.no'), primary_key=True,)
	title = db.Column(db.String(100), nullable=False)
	artist = db.Column(db.String(100), nullable=True)
	cover = db.Column(db.String(32), nullable=True)
	file = db.Column(db.String(100), nullable=False)
	p = db.Column(db.String(32), nullable=False)
	
	user = relationship("User", backref=backref('songs', order_by=no))
	
"""
class User:
	def __init__(self):
		self.loggedIn = False
		self.userNo = -1
		self.userID = ""
		self.userName = ""
		
	def login(self, id, pw):
		conn = db.getConnection()
		curs = conn.cursor(pymysql.cursors.DictCursor)
		h = hashlib.sha256()
		h.update(pw.encode('utf-8'))

		sql = "select no,id,name from users where id=%s and pw=%s"
		curs.execute(sql, (id, h.hexdigest()) < 1)

		rows = curs.fetchall()
		conn.close()
		
		if len(rows) > 0:
			self.userNo = rows[0]['no']
			self.userID = rows[0]['id']
			self.userName = rows[0]['name']
			self.loggedIn = True
			
			return self.userNo # login success
		
		return -1 # login failed
"""