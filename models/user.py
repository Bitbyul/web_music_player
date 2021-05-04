#import pymysql
#from model import database as db
import hashlib

from models import db

"""
TABLE users
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| no       | int(11)     | NO   | PRI | NULL    | auto_increment |
| id       | varchar(30) | NO   | UNI | NULL    |                |
| pw       | char(64)    | NO   |     | NULL    |                |
| name     | varchar(20) | NO   |     | NULL    |                |
| passthru | tinyint(1)  | NO   |     | 0       |                |
+----------+-------------+------+-----+---------+----------------+
"""

class User(db.Model):
	__tablename__ = 'users'
	no = db.Column(db.Integer, primary_key=True, autoincrement=True)
	id = db.Column(db.String(30), nullable=False, unique=True)
	pw = db.Column(db.String(64), nullable=False)
	name = db.Column(db.String(20), nullable=False)
	passthru = db.Column(db.Boolean, nullable=False, default=True)
	
	def check_password(self, pw):
		h = hashlib.sha256()
		h.update(pw.encode('utf-8'))
		
		return ( self.pw == h.hexdigest() )
	
	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
	
	def get_id(self):
		return self.no
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