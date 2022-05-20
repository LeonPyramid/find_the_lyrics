import asyncio
import time 
import time
from lyrics_parser.music_parser import MusicParser
import dictionary_organizer as do
from pympler import muppy,summary

numthread = 10
num_music = 151000
bach = 10000

def set_as_dict(dictionary):
    ret = {}
    for elt in dictionary:
        ((name,pos),val) = elt
        ret[(name,pos)] = val
    return ret

def parse_lyrics():
    lst = list(do.read_dictionary("data/lyrics.txt").values())
    l_parser = MusicParser()
    dictionnaries = {"fr":{},"en":{}}
    dictionnaries["fr"] = set_as_dict(do.read_dictionary("data/french_dict.txt"))
    dictionnaries["en"] = set_as_dict(do.read_dictionary("data/english_dict.txt"))
    start = time.time()
    count = do.get_passed_lyrics("data/passed_lyrics.txt")
    passed = sum(count)

    for _ in range(int((num_music-passed)/bach)):
        ret = l_parser.lyrics_list_analyzer(lst,dictionnaries,count,numthread,bach,passed)
        if(ret == 0):
            break
        passed += bach
        print(count[0], " lyrics not treated")
        print(count[1], " lyrics in french ")
        print(count[2], " lyrics in english")
        do.write_dictionnary_words("data/french_dict.txt",dictionnaries["fr"])
        do.write_dictionnary_words("data/english_dict.txt",dictionnaries["en"])
        do.put_passed_lyrics("data/passed_lyrics.txt",count)
        all = muppy.get_objects()
        summ = summary.summarize(all)
        summary.print_(summ)


    stop = time.time()
    print("lyrics read in ", (stop - start))


parse_lyrics()