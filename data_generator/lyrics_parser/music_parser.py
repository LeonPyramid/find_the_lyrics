import random
from langcodes import Language
import spacy
from spacy_langdetect import LanguageDetector
import threading
import queue

from torch import rand

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
        self.__dict_lock = threading.Lock()
        self.__help_lock = threading.Lock()

        print("Parser loaded")

    def __detect_lang(self,text):
        return self.__lang_detect._language_detection_function(text)["language"]


    async def find_type(self,word):
        async with self.__help_lock:
            print("\033[95mLe mot n'est pas reconnu, quel est le type ? ",word.text,word.lemma_+'\033[0m')
            print("dans la phrase : ")
            print(word.sent)
            return input()

    def __analyze_lyrics(self,words,dict,):
        for word in words:
            pos = word.pos_
            lemma = word.lemma_
            #if(pos == "X"):
            #    pos = await self.find_type(word)
            if(pos == "VERB" or pos == "NOUN" or pos == "ADJ" or pos == "ADV" or pos == "PROPN") and len(lemma) > 2:
                self.__dict_lock.acquire()
                if ((lemma,pos) in dict.keys()):
                    dict[(lemma,pos)] += 1
                else:
                    dict[(lemma,pos)] = 1
                self.__dict_lock.release()
            del pos
            del lemma

    def lyrics_analyzer(self,dictionary_dict,count,queue,size):
        #dictionary_dict = {"en" : {}, "fr": {}}
        while True:
            if (queue.empty()):
                return
            lyrics = queue.get()
            words = self.__en_nlp(lyrics)
            lang = self.__detect_lang(words)
            if lang == "en":
                self.__analyze_lyrics(words,dictionary_dict["en"])
                count[2] += 1
            elif lang == "fr":
                words = self.__fr_nlp(lyrics)
                self.__analyze_lyrics(words,dictionary_dict["fr"])
                count[1] += 1
            else :
                count[0] += 1
            queue.task_done()
            self.__progress_done += 1
            prog = "{:.1f}".format((self.__progress_done / size)*100)
            print("progress: "+ prog +"%",end="\r")
            del lyrics
            del words 
            del lang
            del prog
        return dictionary_dict



    def lyrics_list_analyzer(self,list,dictionary_dict,count,numthread,num_music,passed):

        end = -1 if (passed+num_music > len(list)) else passed+num_music
        lst = list[passed:end]
        size = len(lst)
        
        l_queue = queue.Queue(maxsize=size)
        self.__progress_done = 0
        tasks = []
        
        for lyrics in lst:
            l_queue.put(lyrics)
        for i in range(numthread):
            t = threading.Thread(target=self.lyrics_analyzer,args=(dictionary_dict,count,l_queue,size))
            t.start()
            tasks.append(t)

        for t in tasks:
            t.join()
        l_queue.join()
        del l_queue
        del lst
        del tasks
        print("\n")
        return size


