from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from models import db

"""
+-------+-------------+------+-----+---------+----------------+
| Field | Type        | Null | Key | Default | Extra          |
+-------+-------------+------+-----+---------+----------------+
| no    | int(11)     | NO   | PRI | NULL    | auto_increment |
| owner | int(11)     | NO   | MUL | NULL    |                |
| name  | varchar(50) | NO   |     | NULL    |                |
+-------+-------------+------+-----+---------+----------------+
"""
class Playlist(db.Model):
	__tablename__ = 'playlists'
	no = db.Column(db.Integer, primary_key=True, autoincrement=True)
	owner = db.Column(db.Integer, ForeignKey('users.no'))
	name = db.Column(db.String(50), nullable=False)
	
	user = relationship("User", backref=backref('playlists', order_by=no))
	