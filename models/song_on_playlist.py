from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from models import db

"""
+-------------+---------+------+-----+---------+-------+
| Field       | Type    | Null | Key | Default | Extra |
+-------------+---------+------+-----+---------+-------+
| playlist_no | int(11) | NO   | PRI | NULL    |       |
| song_no     | int(11) | NO   | PRI | NULL    |       |
| index       | int(11) | NO   | PRI | NULL    |       |
+-------------+---------+------+-----+---------+-------+
"""
class Song_on_playlist(db.Model):
	__tablename__ = 'songs_on_playlist'
	playlist_no = db.Column(db.Integer, ForeignKey('playlists.no'), primary_key=True)
	song_no = db.Column(db.Integer, ForeignKey('songs.no'), primary_key=True)
	index = db.Column(db.Integer, primary_key=True)
	
	playlist = relationship("Playlist", backref=backref('songs_on_playlist', order_by=index))
	song = relationship("Song", backref=backref('songs_on_playlist', order_by=index))
	