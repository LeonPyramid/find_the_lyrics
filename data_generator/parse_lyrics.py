import asyncio
import time 
import time
from lyrics_parser.music_parser import MusicParser
import dictionary_organizer as do

numthread = 10


async def parse_lyrics():
    lst = list(do.read_dictionary("data/lyrics.txt").values())
    l_parser = MusicParser()
    dictionnaries = {"fr":{},"en":{}}
    count = [0,0,0]
    start = time.time()
    l_parser.lyrics_list_analyzer(lst,dictionnaries,count,numthread)
    stop = time.time()
    print("lyrics read in ", (stop - start))
    print(count[0], " lyrics not treated")
    print(count[1], " lyrics in french ")
    print(count[2], " lyrics in english")

    do.write_dictionnary_words("data/french_dict.txt",dictionnaries["fr"])
    do.write_dictionnary_words("data/english_dict.txt",dictionnaries["en"])


loop = asyncio.get_event_loop()
loop.run_until_complete(parse_lyrics())