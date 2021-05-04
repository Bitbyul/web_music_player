import pymysql
import hashlib
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
TABLE songs
+--------+--------------+------+-----+---------+----------------+
| Field  | Type         | Null | Key | Default | Extra          |
+--------+--------------+------+-----+---------+----------------+
| no     | int(11)      | NO   | PRI | NULL    | auto_increment |
| owner  | int(11)      | NO   | PRI | NULL    |                |
| title  | varchar(100) | NO   |     | NULL    |                |
| artist | varchar(100) | YES  |     | NULL    |                |
| cover  | char(32)     | YES  |     | NULL    |                |
| file   | char(32)     | NO   |     | NULL    |                |
+--------+--------------+------+-----+---------+----------------+
"""
def getConnection():
	return pymysql.connect(host='localhost', user='ss_music_admin', password='ssmus!c!#!#', db='ss_music', charset='utf8')

def login(id, pw):
	conn = getConnection()
	curs = conn.cursor(pymysql.cursors.DictCursor)
	h = hashlib.sha256()
	h.update(pw.encode('utf-8'))
	
	sql = "select no from users where id=%s and pw=%s"
	curs.execute(sql, (id, h.hexdigest()) < 1)
	
	rows = curs.fetchall()
	conn.close()
	
	if len(rows) < 1:
		return -1 # login failed
	
	return rows[0]['no']

def getMusicFilePathByParam(p):
	if p == 'bbb':
		return "static/mp3temp/bbb.mp3"
	elif p == 'paperstar':
		return "static/mp3temp/paperstar.mp3"
	elif p == 'fallin':
		return "static/mp3temp/fallin.mp3"
	elif p == 'gumh':
		return "static/mp3temp/gumh.mp3"