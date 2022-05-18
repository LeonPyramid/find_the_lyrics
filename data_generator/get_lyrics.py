import asyncio
import time
from lyrics_getter.get_lyrics import LyricsGetter
import dictionary_organizer as do

numMusic = 100000
numbatch = 500
web_thread_count = 20

def get_lyrics():
    l_getter = LyricsGetter()
    passed_list = do.get_passed_list("data/passed.txt")
    passed_musics = set(passed_list)
    dic_list = do.read_dictionary_lyrics("data/lyrics.txt")
    start = time.time()
    cpt = 0
    for _ in range(int(numMusic/numbatch)):
        print("num of lyrics = ",len(dic_list))
        print("num of passed id = ",len(passed_musics),"\n")
        dic_list = l_getter.random_songs_lyrics_list(numbatch,web_thread_count,dic_list,passed_musics)
        do.write_dictionary("data/lyrics.txt",dic_list)
        do.write_passed_list("data/passed.txt",list(passed_musics))
        cpt += 1
        #print(cpt*numbatch)
    stop = time.time()
    print("lyrics caught in ", (stop - start))


loop = asyncio.get_event_loop()
loop.run_until_complete(get_lyrics())
