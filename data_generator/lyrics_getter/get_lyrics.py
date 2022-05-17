import re
import random
from sys import maxsize
from typing import List, Tuple
from threading import Thread,local
import requests
from requests.sessions import Session
from queue import Queue

class LyricsError(Exception):
	pass

class LyricsGetter:
	def __init__(self) -> None:
		random.seed()
	#the max song id accepted for our genius id getter
	__max_id = 2243600
	#used by get_genius_artist_song
	__genius_url = "https://genius.p.rapidapi.com/songs/"

	__lyrics_url = "https://api.lyrics.ovh/v1/"

	__genius_headers = {
		"X-RapidAPI-Host": "genius.p.rapidapi.com",
		"X-RapidAPI-Key": "bacff9a267msha79d1ff7892a8d9p17eed2jsnb146330a53f0"
	}

	__pattern = r"\[.*\]|\{.*\}|\'.*\'|\".*\""


	__thread_local = local()

#	def get_genius_artist_song(self,id):
#		"""Returns as a tuple the artist and song name of this corresponding id"""
#		if id > self.__max_id:
#			raise LyricsError("Genius:Id too big "+ str(id))
#		url = self.__genius_url + str(id)
#		resp = requests.request("GET",url,headers=self.__genius_headers)
#		if resp.status_code == 404:
#			raise LyricsError("Genius:Id not in list " + str(id))
#		elif resp.status_code != 200:
#			raise LyricsError("Genius: error "+ str(resp.status_code))
#		r_json = resp.json()
#		artist = r_json["response"]["song"]["artist_names"]
#		title = r_json["response"]["song"]["title"]
#		return (artist,title)
#	
#	def get_lyrics_from_artist_song(self,art_tittle: Tuple[str,str]) -> str:
#		"""Returns the lyrics from a given song without any annotation"""
#		artist = art_tittle[0]
#		title = art_tittle[1]
#		url = self.__lyrics_url + artist + "/" + title
#		resp = requests.request("GET",url)
#		if resp.status_code == 404:
#			raise LyricsError("Lyrics.ovh: not in database " + artist + " " + title)
#		elif resp.status_code != 200:
#			raise LyricsError("Lyrics.ovh: error"+ str(resp.status_code))
#		lyrics = resp.json()["lyrics"]
#		res = re.sub(self.__pattern,'',lyrics)
#		return res
#
#
#	def random_song_lyrics(self,passed):
#		"""Gives a random song as a string"""
#		while True:
#			id = random.randrange(1,self.__max_id)
#			print(id)
#			if not (id in passed):
#				passed.add(id)
#				try:
#					art_ttl = self.get_genius_artist_song(id)
#					lyrics = self.get_lyrics_from_artist_song(art_ttl)
#					return lyrics
#				except LyricsError as e:
#					print(e)
#					pass 
#Old methods too slow for massive data gathering

	def __get_session(self) -> Session:
		if not hasattr(self.__thread_local,'session'):
			self.__thread_local.session = requests.Session() # Create a new Session if not exists
		return self.__thread_local.session


	def get_genius_session(self,id):
		if id > self.__max_id:		
			raise LyricsError("Genius:Id too big "+ str(id))
		session = self.__get_session()
		url = self.__genius_url + str(id)
		resp = session.request("GET",url,headers=self.__genius_headers)
		if resp.status_code == 404:
			raise LyricsError("Genius:Id not in list " + str(id))
		elif resp.status_code != 200:
			raise LyricsError("Genius: error "+ str(resp.status_code))
		r_json = resp.json()
		artist = r_json["response"]["song"]["artist_names"]
		title = r_json["response"]["song"]["title"]
		return (artist,title)
	
	def get_lyrics_session(self,art_tittle: Tuple[str,str]) -> str:
		"""Returns the lyrics from a given song without any annotation"""
		artist = art_tittle[0]
		title = art_tittle[1]
		url = self.__lyrics_url + artist + "/" + title
		session = self.__get_session()
		resp = session.request("GET",url)
		if resp.status_code == 404:
			raise LyricsError("Lyrics.ovh: not in database " + artist + " " + title)
		elif resp.status_code != 200:
			raise LyricsError("Lyrics.ovh: error"+ str(resp.status_code))
		lyrics = resp.json()["lyrics"]
		res = re.sub(self.__pattern,'',lyrics)
		return res
	
	def random_lyrics_session(self,q,passed,lyrics_list,count,num_mus):
		"""Gives a random song as a string"""
		while True:
			if num_mus.empty():
				break
			num_mus.get()
			while True:
				if q.empty():
					break
				id = q.get()
				if not (id in passed):
					try:
						art_ttl = self.get_genius_session(id)
						st = str(art_ttl)
						if not (st in lyrics_list.keys()):
							lyrics = self.get_lyrics_session(art_ttl)
							lyrics_list[st] = lyrics
							passed.add(id)
							break
					except LyricsError as e:
						#print(e)
						passed.add(id)
						pass
			count[0] += 1
			print(count[0])

	def random_songs_lyrics_list(self,num_music,num_thread,lyrics_list,passed):
		#First queue contains the non-tested id
		q=Queue(maxsize=0)
		for i in range(self.__max_id):
			if not (i in passed):
				q.put(i)
		print("queue filled")
		#second queue used to only add num_music in the list
		num_mus = Queue()
		for _ in range(num_music):
			num_mus.put(1)
		threads = []
		count = [0]
		for _ in range(num_thread):
			t = Thread(target=self.random_lyrics_session,args=(q,passed,lyrics_list,count,num_mus))
			threads.append(t)
			t.start()
		for t in threads:
			t.join()
		return lyrics_list
		