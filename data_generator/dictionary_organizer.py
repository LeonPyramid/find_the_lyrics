import json
import pickle
from os import path

def __rearange_dict(dict):
    return sorted(dict.items(), key=lambda kv: kv[1],reverse=True)

def write_dictionary(filename,dict):
    with open(filename, 'w') as convert_file:
        convert_file.write(json.dumps(dict))

def write_dictionnary_words(filename,dict):
    redict = __rearange_dict(dict)
    write_dictionary(filename,redict)



def read_dictionary(filename) :
    if(path.exists(filename)):
        with open(filename) as file:
            data = json.load(file)
            return data
    else:
        return {}

def write_passed_list(filename,list):
    with open(filename, 'wb') as fp:
        pickle.dump(list, fp)

def get_passed_list(filename):
    if(path.exists(filename)):
        with open (filename, 'rb') as fp:
            return pickle.load(fp)
    else:
        return []

def get_passed_lyrics(filename):
    if(path.exists(filename)):
        with open (filename, 'rb') as fp:
            return pickle.load(fp)
    else:
        return [0,0,0]

def put_passed_lyrics(filename,num):
    with open(filename, 'wb') as fp:
        pickle.dump(num, fp)