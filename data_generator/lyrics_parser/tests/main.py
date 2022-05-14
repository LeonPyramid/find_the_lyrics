from math import ceil, floor
from time import thread_time
from typing import List
import time
from get_lyrics import LyricsGetter
from music_parser import MusicParser
from threading import Thread
import dictionary_organizer as do
from queue import Queue

numMusic = 10000
numbatch = 100
web_thread_count = 25
num_thread = 100

def threadFunc(dicts,l_pars: MusicParser,q,count):
    while True:
        if q.empty():
            break
        lyrics = q.get()
        l_pars.lyrics_analyzer(lyrics,dicts,count)
        q.task_done()


l_getter = LyricsGetter()
#l_parser = MusicParser()
dictionnaries = {"fr":{},"en":{}}

passed_musics = set()
list = do.read_dictionary_lyrics("lyrics.txt")
start = time.time()
for _ in range(int(numMusic/numbatch)):
    list = l_getter.random_songs_lyrics_list(numbatch,web_thread_count,list,passed_musics)
    do.write_dictionary("lyrics.txt",list)
stop = time.time()
print("lyrics caught in ", (stop - start))


def parse_lyrics(list):
    q=Queue(maxsize=0)
    count = [0,0,0]
    for lir in list:
        q.put(lir)
    threads = []
    for _ in range(num_thread):
        t = Thread(target=threadFunc,args=(dictionnaries,l_parser,q,count))
        t.start()
        threads.append(t)
    q.join()
    for t in threads:
        t.join()
    print("lyrics read")
    print(count[0], " lyrics not treated")
    print(count[1], " lyrics in french ")
    print(count[2], " lyrics in english")

    do.write_dictionnary("french_dict.txt",dictionnaries["fr"])
    do.write_dictionnary("english_dict.txt",dictionnaries["en"])

