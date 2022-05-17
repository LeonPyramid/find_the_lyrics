import re
import json

data = {}
with open("lyrics.txt") as f:
    data = json.load(f)
    for key in data:
        lyrics = data[key]
        res = re.sub(r"\[.*\]|\{.*\}|\'.*\'|\".*\"",'',lyrics)
        data[key] = res
        print(key)
with open("lyrics.txt",'w') as f:
    f.write(json.dumps(data))