from langcodes import Language
import spacy
from profanity_check import predict

min_count = 10

class DictionaryTreater:
    __fr_nlp:Language = None
    __en_nlp:Language = None
    __prof_filter = None

    def __init__(self) -> None:
        #self.__fr_nlp = spacy.load("fr_dep_news_trf")
        #self.__en_nlp = spacy.load("en_core_web_trf")
        print("Parser loaded")

    def get_elt(self,elt):
        (key,val) = elt
        try:
            (name,pos) = key
        except Exception as e:
            print(key)
            raise Exception
        return ((name,pos),val)

    def remove_less_than(self,dictionary,min):
        ret = {}
        for elt in dictionary.items():
            ((name,pos),val) = elt
            if val >= min:
                ret[(name,pos)] = val
        return ret


    def get_total(self,dictionary) -> int:
        return sum(val for val in dictionary.values())

    def english_remove_profanity(self,dictionary):
        ret = {}
        for elt in dictionary.items():
            ((name,pos),val) = elt
            if (predict([name])[0] == 0):
                ret[(name,pos)] = val
        return ret

    def set_verb_form(self,dictionary):
        ret = {}
        for elt in dictionary.items():
            ((name,pos),val) = elt
            if pos == "VERB":
                ret[("(to) "+name,pos)]=val
            else:
                ret[(name,pos)] = val
        return ret

    def set_as_dict(self,dictionary):
        ret = {}
        for elt in dictionary:
            ((name,pos),val) = elt
            ret[(name,pos)] = val
        return ret

        
    def french_get_feminine_adj_from(self,word):
        if word[-1] == "c":
            return word+"·que"
        if word[-1] == "f":
            return word+"·f"
        if word[-1] == "x":
            return word+"·se"
        #TODO: OSKOUR NATACHA, help me c'est l'enfer

    def treat_english_dictionary(self,dictionary):
        dictionary = self.set_as_dict(dictionary)
        ret = self.remove_less_than(dictionary,min_count)
        #print( dictionary)
        ret = self.english_remove_profanity(ret)
        ret = self.set_verb_form(ret)
        tot = self.get_total(ret)
        out = {}
        for elt in ret.items():
            ((name,_),val) = self.get_elt(elt)
            prob = 100*val/tot
            prob = float(f'{prob:.3f}')
            if not( name in out.keys()):
                out[name] = prob
        return out

