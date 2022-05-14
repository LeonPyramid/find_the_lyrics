from tkinter.filedialog import LoadFileDialog
from langcodes import Language
import spacy
from spacy_langdetect import LanguageDetector
import unidecode
import json
from threading import Lock


class MusicParser:
    __fr_nlp:Language = None
    __en_nlp:Language = None
    __lang_detect:LanguageDetector = None
    __mutex = Lock()
    def __init__(self) -> None:
        self.__fr_nlp = spacy.load("fr_core_news_sm")
        self.__en_nlp = spacy.load("en_core_web_sm")
        self.__lang_detect = LanguageDetector()
        print("Parser loaded")

    def __detect_lang(self,text):
        return self.__lang_detect._language_detection_function(text)["language"]


    def __analyze_lyrics(self,words,dict):
        self.__mutex.acquire()
        for word in words:
            pos = word.pos_
            lemma = unidecode.unidecode(word.lemma_)
            if(pos == "VERB" or pos == "NOUN" or pos == "ADJ")and len(lemma) > 1:
                try:
                    dict[lemma] += 1
                except KeyError:
                    dict[lemma] = 1
        self.__mutex.release()

    def lyrics_analyzer(self,lyrics,dictionary_dict,count):
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


