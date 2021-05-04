from flask import Flask, render_template, request, session, redirect, jsonify, send_file
from flask_login import login_required, logout_user, current_user, login_user
from datetime import timedelta
import requests
import json
import eyed3
import base64
import re
import xml.etree.ElementTree as ET
import random
import string
import time
import hashlib

from models import login_manager, db
from models.user import User
from models.song import Song
from models.playlist import Playlist
from models.song_on_default import Song_on_default
from models.song_on_playlist import Song_on_playlist


app = Flask(__name__)
app.secret_key = 'QW#TUFEG(O)PJu9203%****'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ss_music_admin:****@localhost:3306/ss_music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SESSION_COOKIE_DOMAIN'] = ".skystar.kr"

login_manager.init_app(app)
db.init_app(app)

CROSS_AUTH_TOKEN = True


@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
	
	if CROSS_AUTH_TOKEN:
		if 'session' in request.form:
			return render_template('main.html')
		
	return render_template('main.html', current_user=current_user)

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/modal/modalSongAddOption')
def modal_songAddOption():
	return render_template('modals/modalSongAddOption.html')

@app.route('/modal/modalSelectSong')
def modal_selectSong():
	return render_template('modals/modalSelectSong.html')

@app.route('/modal/modalSongConfirm')
def modal_songConfirm():
	return render_template('modals/modalSongConfirm.html')

@app.route('/get/allsong', methods=['GET','POST'])
@login_required
def get_allsong():
	songlist = getAllSong()#getAllSong()
	return jsonify(songlist)

@app.route('/get/playlist', methods=['GET', 'POST'])
@login_required
def get_playlist():
	playlistname = None
	if 'playlist' in request.form:
		playlistname = request.form['playlist']
		
	playlist = getPlaylist(playlistname)
	"""
	playlist = [
		{'title':'마음을 드려요', 'artist':'아이유', 'cover':'gggggggggggggggggggggggggggggggg', 'file':'gggggggggggggggggggggggggggggggg'},
		{'title':'종이별 (Paper Star)', 'artist':'로켓펀치 (Rocket Punch)', 'cover':'pppppppppppppppppppppppppppppppp', 'file':'pppppppppppppppppppppppppppppppp'},
		{'title':'빔밤붐 (BIM BAM BUM)', 'artist':'로켓펀치 (Rocket Punch)', 'cover':'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'file':'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'},
		{'title':'Fallin', 'artist':'러블리즈 (Lovelyz)', 'cover':'ffffffffffffffffffffffffffffffff', 'file':'ffffffffffffffffffffffffffffffff'}
	]
	"""
	""" for test data import
	for playdict in playlist:
		song = Song(
			owner=1,
			title=playdict['title'],
			artist=playdict['artist'],
			cover=playdict['cover'],
			file=playdict['file'],
			p=playdict['file']
		)
		db.session.add(song)
	db.session.commit()
	"""
	return jsonify(playlist)

@app.route('/get/mediafile', methods=['GET'])
@login_required
def get_mediafile():
	fileparam = request.args.get('p')
	if fileparam:
		filename = getFilePathByParam(fileparam)#db.getMusicFilePathByParam(fileparam)
		return send_file(filename)
	else:
		print("wrong access")
		return "ERROR", 404

@app.route('/get/metadata', methods=['GET'])
@login_required
def get_metadata():
	fileparam = request.args.get('p')
	if fileparam:
		# find cache
		
		# get mp3 location from db
		id3_data = getID3Data(getFilePathByParam(fileparam))
		# extract cover id3
		
		return jsonify(id3_data)
	else:
		print("wrong access")
		return "ERROR", 404
	
@app.route('/get/lyrics', methods=['GET', 'POST'])
def get_lyrics():
	if not ('artist' in request.form and 'title' in request.form):
		return "ERROR", 404
	
	xml_find_sta = '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns2="ALSongWebServer/Service1Soap" xmlns:ns1="ALSongWebServer" xmlns:ns3="ALSongWebServer/Service1Soap12"><SOAP-ENV:Body><ns1:GetResembleLyricList2><ns1:encData>8456ec35caba5c981e705b0c5d76e4593e020ae5e3d469c75d1c6714b6b1244c0732f1f19cc32ee5123ef7de574fc8bc6d3b6bd38dd3c097f5a4a1aa1b438fea0e413baf8136d2d7d02bfcdcb2da4990df2f28675a3bd621f8234afa84fb4ee9caa8f853a5b06f884ea086fd3ed3b4c6e14f1efac5a4edbf6f6cb475445390b0</ns1:encData><ns1:title>{title}</ns1:title><ns1:artist>{artist_name}</ns1:artist><ns1:pageNo>{page}</ns1:pageNo></ns1:GetResembleLyricList2></SOAP-ENV:Body></SOAP-ENV:Envelope>'
	xml_get_sta = '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns2="ALSongWebServer/Service1Soap" xmlns:ns1="ALSongWebServer" xmlns:ns3="ALSongWebServer/Service1Soap12"><SOAP-ENV:Body><ns1:GetLyricByID2><ns1:encData>8456ec35caba5c981e705b0c5d76e4593e020ae5e3d469c75d1c6714b6b1244c0732f1f19cc32ee5123ef7de574fc8bc6d3b6bd38dd3c097f5a4a1aa1b438fea0e413baf8136d2d7d02bfcdcb2da4990df2f28675a3bd621f8234afa84fb4ee9caa8f853a5b06f884ea086fd3ed3b4c6e14f1efac5a4edbf6f6cb475445390b0</ns1:encData><ns1:lyricID>{lyricID}</ns1:lyricID></ns1:GetLyricByID2></SOAP-ENV:Body></SOAP-ENV:Envelope>'
	url = 'http://lyrics.alsong.co.kr/alsongwebservice/service1.asmx'
	time_pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
	namespaces = {
		'soap': 'http://www.w3.org/2003/05/soap-envelope',
		'a': 'ALSongWebServer',
	}
	resp = requests.post(
			url,
			data=xml_find_sta.format(
					title=request.form['title'],
					artist_name=request.form['artist'],
					page=0,
			).encode(),
			headers={
					'Content-Type': 'text/xml;charset=utf-8',
					'User-Agent': 'gSOAP/2.7',
					'SOAPAction': '"ALSongWebServer/GetResembleLyricList2"'
			},
	)
	
	tree = ET.fromstring(resp.text)
	ids = tree.findall(
			'./soap:Body'
			'/a:GetResembleLyricList2Response'
			'/a:GetResembleLyricList2Result'
			'/a:ST_SEARCHLYRIC_LIST'
			'/a:lyricID',
			namespaces,
	)
	#for name in names:
	#	print(name.text)
	#print(ids[0].text)
	lyricID = ids[0].text
	
	resp = requests.post(
			url,
			data=xml_get_sta.format(
					lyricID=lyricID,
			).encode(),
			headers={
					'Content-Type': 'text/xml;charset=utf-8',
					'User-Agent': 'gSOAP/2.7',
					'SOAPAction': '"ALSongWebServer/GetLyricByID2"'
			},
	)	
	
	tree = ET.fromstring(resp.text)
	datas = tree.findall(
			'./soap:Body'
			'/a:GetLyricByID2Response'
			'/a:output'
			'/a:lyric',
			namespaces,
	)
	
	#print(datas[0].text)
	lyricData = datas[0].text.replace('\n',"<br>")
	lyricDict = {}
	
	chunks = lyricData.split('<br>')
	idx = 0
	for chunk in chunks:
		match = time_pattern.match(chunk)
		if match:
			#print(int(match.group(1))*60 + float(match.group(2)))
			#print(match.group(3).strip())
			lyricDict[idx] = {'t': int(match.group(1))*60 + float(match.group(2)), 'd': match.group(3).strip()}
			idx+=1
			
	return jsonify(lyricDict)##tree.attrib#user.get('lyricID')
	
@app.route('/proc/login', methods=['GET', 'POST'])
def proc_login():
	if 'id' in request.form:
		user = User.query.filter_by(id=request.form['id']).first()
		if user and user.check_password(request.form['pw']):
			login_user(user)
		
	return redirect('/')

@app.route('/proc/logout')
def proc_logout():
	logout_user()
	return redirect('/')

@app.route('/proc/register', methods=['GET', 'POST'])
def proc_register():
	if 'id' in request.form:
		
		h = hashlib.sha256()
		h.update(request.form['pw'].encode('utf-8'))
		
		user = User(
			id=request.form['id'],
			pw=h.hexdigest(),
			name=request.form['name'],
			passthru=False
		)
		db.session.add(user)
		db.session.commit()
		
		login_user(user)
		
	return redirect('/')

@app.route("/proc/multipleMp3Upload", methods=["POST"])
def proc_multipleMp3Upload():
	uploaded_files = request.files.getlist("file")
	
	upload_files_info_dict = {}
	
	print(uploaded_files)
	for f in uploaded_files:
		mfilename = f.filename + "-" + str(int(time.time()*10000))
		f.save("upload/mp3temp/"+mfilename)
		
		file_info_dict = {'result': True, 'filename': f.filename}
		file_info_dict.update(getID3Data("upload/mp3temp/"+mfilename))
		
		upload_files_info_dict[mfilename] = file_info_dict
		
	return jsonify(upload_files_info_dict)

@app.route("/proc/addSongsByMp3Upload", methods=["POST"]) # confirmsongs
def proc_addSongsByMp3Upload():
	#print(request.data)
	filesdict = request.json
	for mfilename in filesdict:
		file_info_dict = filesdict[mfilename]
		addSong(mfilename, file_info_dict['title'], file_info_dict['artist'])
	
	return jsonify({'status':0})

@app.route("/proc/addSongsByExistingSong", methods=["POST"])
def proc_addSongsByExistingSong():
	songsdict = request.json
	for idx in songsdict:
		print(songsdict[idx])
		addSongToPlaylistByParam(songsdict[idx])
	
	return jsonify({'status':0})

@app.route("/proc/deleteSong", methods=["POST"])
def proc_deleteSong():
	p = request.form['p']
	print(p)
	return jsonify({'status':0})
	
@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=60)

# for login mamanger 
@login_manager.user_loader
def load_user(user_id):
	"""Check if user is logged-in on every page load."""
	if user_id is not None:
		return User.query.get(user_id)
	return None

@login_manager.unauthorized_handler
def unauthorized():
	"""Redirect unauthorized users to Login page."""
	
	return redirect('/login') # "unauthorized", 401

def getAllSong():
	playlist = []
	
	for s in Song.query.filter_by(owner=current_user.no):
		song = s.__dict__
		song.pop('_sa_instance_state')
		playlist.append(song)
		
	return playlist

def getPlaylist(playlist_no=None):
	playlist = []
	
	if(playlist_no):
		for s in Song.query.filter_by(owner=current_user.no):
			song = s.__dict__
			song.pop('_sa_instance_state')
			playlist.append(song)
	else:
		song_no_list = []
		# return default playlist
		# select * from songs where no=
		#					(select song_no from songs_on_default where owner=3);
		print("Returning Default Playlist")
		songs_on_default = User.query.filter_by(no=current_user.no).first().songs_on_default
		
		for sn in songs_on_default:
			song_no_list.append(sn.song_no)
		
		for s in Song.query.filter(Song.no.in_(song_no_list)):
			song = s.__dict__
			song.pop('_sa_instance_state')
			playlist.append(song)
			
	return playlist
	
def getFilePathByParam(p):
	return 'upload/mp3temp/'+Song.query.filter_by(owner=current_user.no, p=p).first().file

def addSong(file, title, artist=None, cover=None):
	song = Song(
		owner=current_user.no,
		title=title,
		artist=artist,
		cover=cover,
		file=file,
		p=randomStringDigits(32)
	)
	db.session.add(song)
	db.session.commit()
	
def getID3Data(filepath):
	f = eyed3.load(filepath)
	id3_data = {
		'artist':f.tag.artist,
		'title':f.tag.title,
		'album':f.tag.album,
	}

	if(len(f.tag.images) < 1):
		id3_data['is_image_existed'] = 0
	else:
		id3_data['is_image_existed'] = 1
		e = base64.b64encode(f.tag.images[0].image_data)
		id3_data['image'] = e.decode("UTF-8")
		
	return id3_data

def addSongToPlaylistByParam(p, playlist_no=None):
	song = getSongByParam(p)
	#max_idx = Song_on_default.query(func.max(Song_on_default.index)).scalar()
	max_idx = Song_on_default.getMaxIndexOfUser(current_user.no)
	if max_idx is None: # first check
		max_idx = 0
	print("max_index is {}".format(max_idx))
	song_on_default = Song_on_default(
		owner=current_user.no,
		song_no=song.no,
		index=max_idx+1
	)
	db.session.add(song_on_default)
	db.session.commit()
	
	return True
	
def getSongByParam(p):
	return Song.query.filter_by(owner=current_user.no, p=p).first()
	
def randomStringDigits(stringLength=32):
	"""Generate a random string of letters and digits """
	lettersAndDigits = string.ascii_letters + string.digits
	return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
	
if __name__ == '__main__':
	models.db.init_app(app)
	app.run()
