from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func

from models import db

"""
+---------+---------+------+-----+---------+-------+
| Field   | Type    | Null | Key | Default | Extra |
+---------+---------+------+-----+---------+-------+
| owner   | int(11) | NO   | PRI | NULL    |       |
| song_no | int(11) | NO   | PRI | NULL    |       |
| index   | int(11) | NO   | PRI | NULL    |       |
+---------+---------+------+-----+---------+-------+
"""
class Song_on_default(db.Model):
	__tablename__ = 'songs_on_default'
	owner = db.Column(db.Integer, ForeignKey('users.no'), primary_key=True)
	song_no = db.Column(db.Integer, ForeignKey('songs.no'), primary_key=True)
	index = db.Column(db.Integer, primary_key=True)
	
	user = relationship("User", backref=backref('songs_on_default', order_by=index))
	song = relationship("Song", backref=backref('songs_on_default', order_by=index))
	
	def getMaxIndexOfUser(user_no):
		return db.session.query(func.max(Song_on_default.index)).filter(Song_on_default.owner==user_no).scalar()