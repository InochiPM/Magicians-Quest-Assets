import numpy
import sys
import json
import glob
import os

def readString(string):
    chars = []
    base = []
    offset = 0
    while (offset <= len(string)):
        c = string[offset:offset+2]
        if c == b"\x24\x00":
            chars.append("<CMD>")
            while (True):
                offset += 2
                c = string[offset:offset+2]
                if (c == b"\x3B\x00"): break
                chars.append(c.hex())
            chars.append("</CMD>")
        elif c == b'\x00\x00':
             base.append("".join(chars).replace("▼", "<BREAK>"))
             chars = []
        else: chars.append(c.decode("UTF-16-LE"))
        offset += 2
    return base

def takeNumber(elem):
    return int(elem[5:-5], 10)

header_size = 0x330

file = open("0001 onemsg (09F82E01).rndx", "rb")
SCRIPT = open("0003 onemsg (09F93003).rdbt", "rb")

file.seek(0, 2)
size = file.tell()
file.seek(0,0)

table = []

while (file.tell() < size):
    entry = {}
    entry["Index"] = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
    entry["Offset"] = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
    entry["Size"] = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
    table.append(entry)

file.close()

try:
    os.mkdir("RESO")
except:
    pass

for i in range(0, len(table)):
    print("Unpacking %s.reso" % table[i]["Index"])
    file = open("RESO/%d.reso" % table[i]["Index"], "wb")
    file.write(SCRIPT.read(table[i]["Size"]))
    file.close()

file_list = glob.glob("RESO/*.reso")

file_list.sort(key=takeNumber)

try:
    os.mkdir("json")
except:
    pass

Messages = []

for x in range(0, len(file_list)):
    print("Dumping %s to JSON" % file_list[x][5:])
    file = open(file_list[x], "rb")
    temp = file.read()
    entry = {}
    entry['Index'] = int(file_list[x][5:-5], 10)
    strings = []
    count = temp.count(b"\x00\x00")
    entry["JPN"] = readString(temp)
    Messages.append(entry)

file.close()
file = open("json/onemsg.json", "w", encoding="UTF-8")
json.dump(Messages, file, indent="\t", ensure_ascii=False)
file.close()