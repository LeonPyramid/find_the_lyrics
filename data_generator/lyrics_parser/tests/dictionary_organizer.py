import json
import collections

def __rearange_dict(dict):
    inv_map = {int(v): k for k, v in dict.items()}
    return collections.OrderedDict(sorted(inv_map.items(),reverse=True))

def write_dictionary(filename,dict):
    with open(filename, 'w') as convert_file:
        convert_file.write(json.dumps(dict))

def write_dictionnary_words(filename,dict):
    redict = __rearange_dict(dict)
    write_dictionary(filename,redict)



def read_dictionary_lyrics(filename) :
    with open(filename) as file:
        data = json.load(file)
        return data