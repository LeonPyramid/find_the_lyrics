import json
from multiprocessing.connection import wait
import re
import random
from sys import maxsize
import time
from typing import List, Tuple
from threading import Thread,local
from numpy import true_divide
import requests
from requests.sessions import Session
from queue import Queue
from bs4 import BeautifulSoup

class LyricsError(Exception):
	pass

class NeedToWait(Exception):
	pass

class LyricsGetter:
	def __init__(self) -> None:
		random.seed()
		with open("lyrics_getter/genius_api_key.txt") as f:
			self.__genius_headers["X-RapidAPI-Key"]=f.readline()
	#the max song id accepted for our genius id getter
	__max_id = 2243600
	#used by get_genius_artist_song
	__genius_url = "https://genius.p.rapidapi.com/songs/"

	__lyrics_url = "https://api.lyrics.ovh/v1/"

	__genius_headers = {
		"X-RapidAPI-Host": "genius.p.rapidapi.com",
		"X-RapidAPI-Key": ""
	}

	__pattern = r"\[.*\]|\{.*\}|\'.*\'|\".*\""


	__thread_local = local()
	__passed = 0

	__thread_list = []

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
		elif resp.status_code == 429:
			raise NeedToWait(resp.headers['Retry-After'])
		elif resp.status_code != 200:
			raise LyricsError("Genius: error "+ str(resp.status_code))
		r_json = resp.json()
		artist = r_json["response"]["song"]["artist_names"]
		title = r_json["response"]["song"]["title"]
		return (artist,title,r_json["response"]["song"]["url"])
	
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
	
	def get_lyrics_from_genius(self,url) -> str:
		session = self.__get_session()
		page  = session.get(url)
		if page.status_code == 404:
			raise LyricsError("Genius:Id not in list " + str(id))
		elif page.status_code == 429:
			raise NeedToWait(page.headers['Retry-After'])
		elif page.status_code != 200:
			raise LyricsError("Genius: error "+ str(page.status_code))
		html = BeautifulSoup(page.text, 'html.parser')
		lyrics1 = html.find("div", class_="lyrics")
		lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 jYfhrf")
		if lyrics1:
			lyrics = lyrics1.get_text()
		elif lyrics2:
			lyrics = lyrics2.get_text()
		elif lyrics1 == lyrics2 == None:
			lyrics = None
		return lyrics

	def random_lyrics_session(self,q,passed,lyrics_list,count,num_mus):
		"""Gives a random song as a string"""
		try:
			while True:
				if num_mus.empty():
					return
				num_mus.get()
				while True:
					if q.empty():
						return
					id = q.get()
					valid = False
					if not (id in passed):
						while True:
							try:
								art_ttl_html = self.get_genius_session(id)
								art_ttl = (art_ttl_html[0],art_ttl_html[1])
								st = str(art_ttl)
								html = art_ttl_html[2]
								if not (st in lyrics_list.keys()):
									lyrics = self.get_lyrics_from_genius(html)
									passed.add(id)
									if(lyrics != None):
										lyrics_list[st] = lyrics
										valid = True
										print('\033[92m',id,"added\033[0m")
										break
									else:
										print('\033[94m',id,"has no lyrics\033[0m")
										break
								else:
									passed.add(id)
									print('\033[94m',id,"already in list\033[0m")
									valid = True
									break
							except LyricsError as e:
								#print(e)
								print('\033[94m'+"failure for "+str(id)+" : "+ str(e)+ '\033[0m')
								passed.add(id)
								break
							except NeedToWait as e:
								print('\033[93m'+"need to wait "+str(id)+" : "+ str(e)+ '\033[0m')
								time.sleep(int(e.args[0]))
					if valid:
						break
				count[0] += 1
				print(count[0])
		except Exception as e:
			print('\033[93m'+ str(e)+ '\033[0m')

	def random_songs_lyrics_list(self,num_music,num_thread,lyrics_list,passed):
		#First queue contains the non-tested id
		self.__passed = 0
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
			time.sleep(1)
		for t in threads:
			t.join()
		print("all done")
		return lyrics_list

	