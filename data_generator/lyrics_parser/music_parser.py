from langcodes import Language
import spacy
from spacy_langdetect import LanguageDetector
from functools import partial
import asyncio
from asyncio import Queue

class MusicParser:
    __fr_nlp:Language = None
    __en_nlp:Language = None
    __lang_detect:LanguageDetector = None
    __dict_lock = None
    __help_lock = None
    __progress_done = 0
    __loop = None
    def __init__(self) -> None:
        self.__fr_nlp = spacy.load("fr_dep_news_trf")
        self.__en_nlp = spacy.load("en_core_web_trf")
        self.__lang_detect = LanguageDetector()
        self.__dict_lock = asyncio.Lock()
        self.__help_lock = asyncio.Lock()
        self.__loop = asyncio.get_event_loop()

        print("Parser loaded")

    def __detect_lang(self,text):
        return self.__lang_detect._language_detection_function(text)["language"]


    async def find_type(self,word):
        async with self.__help_lock:
            print("\033[95mLe mot n'est pas reconnu, quel est le type ? ",word.text,word.lemma_+'\033[0m')
            print("dans la phrase : ")
            print(word.sent)
            return input()
    
    async def __analyze_lyrics(self,words,dict):
        for word in words:
            pos = word.pos_
            lemma = word.lemma_
            #if(pos == "X"):
            #    pos = await self.find_type(word)
            if(pos == "VERB" or pos == "NOUN" or pos == "ADJ" or pos == "ADV" or pos == "PROPN") and len(lemma) > 2:
                async with self.__dict_lock:
                    if ((lemma,pos) in dict.keys()):
                        dict[(lemma,pos)] += 1
                    else:
                        dict[(lemma,pos)] = 1

    async def lyrics_analyzer(self,dictionary_dict,count,queue,size):
        #dictionary_dict = {"en" : {}, "fr": {}}
        while True:
            if (queue.empty()):
                return
            lyrics = await queue.get()
            words = self.__en_nlp(lyrics)
            lang = self.__detect_lang(words)
            if lang == "en":
                await self.__analyze_lyrics(words,dictionary_dict["en"])
                count[2] += 1
            elif lang == "fr":
                words = self.__fr_nlp(lyrics)
                await self.__analyze_lyrics(words,dictionary_dict["fr"])
                count[1] += 1
            else :
                count[0] += 1
            queue.task_done()
            self.__progress_done += 1
            prog = "{:.3f}".format(self.__progress_done / size)
            print("progress: "+ prog +"%",end="\r")
        return dictionary_dict

    async def lyrics_list_analyzer(self,list,dictionary_dict,count,numthread):
        list = list[1:1000]
        queue = Queue(maxsize=len(list))
        self.__progress_done = 0
        tasks = []
        
        for lyrics in list:
            await queue.put(lyrics)
        loop = self.__loop
        for i in range(numthread):
            t = loop.create_task(self.lyrics_analyzer(dictionary_dict,count,queue,len(list)))
            tasks.append(t)
        await queue.join()

        for t in tasks:
            t.cancel()

        asyncio.gather(*tasks)


