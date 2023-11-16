import numpy
import sys
import json
import glob
import os

SizeCheck = {
    "12": 9,
    "32": 5,
    "44": 17,
    "80": 5,
    "92": 5,
    "104": 5,
    "116": 5,
    "128": 5,
    "140": 5
}

def takeNumber(elem):
    return int(elem[5:-5], 10)

def CheckSize(file):
    file.seek(0, 2)
    if (file.tell() != 0xB0):
        print("Size error! %s" % file)
        sys.exit()
    file.seek(0, 0)

def CheckStringUnderSize(string, position, file):
    if (len(string) > SizeCheck["%d" % position]):
        print("Error! %s" % file)
        sys.exit()
    return

def readString(myfile):
    chars = []
    while True:
        c = myfile.read(2)
        if c == b'\x00\x00':
            return str(b"".join(chars).decode("UTF-16-LE"))
        chars.append(c)

file = open("0000_NpcDataOfs_098C2E00.rndx", "rb")
SCRIPT = open("0004_NpcDataOfs_098D3004.rdbt", "rb")

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
    os.mkdir("DAT")
except:
    pass

for i in range(0, len(table)):
    print("Unpacking %s.dat" % table[i]["Index"])
    file = open("DAT/%d.dat" % table[i]["Index"], "wb")
    file.write(SCRIPT.read(table[i]["Size"]))
    file.close()

Files = glob.glob("DAT/*.dat")

try:
    os.mkdir("json")
except:
    pass

for i in range(0, len(Files)):
    print("Dumping %s to JSON" % Files[i])
    file = open(Files[i], "rb")
    CheckSize(file)
    entry = {}
    entry["Args"] = file.read(0x8).hex()
    entry["Strings"] = []
    if (file.read(0x4) != b"\x0F\x0F\x0F\x0F"):
        print("Error! %s" % Files[i])
        sys.exit()
    while (file.tell() < 0x98):
        position = file.tell()
        string = readString(file)
        if (string != ""): 
            CheckStringUnderSize(string, position, Files[i])
            stringjson = {}
            stringjson["Offset"] = position
            stringjson["Text"] = string
            entry["Strings"].append(stringjson)
    entry["Arg2"] = file.read(0x18).hex()
    file.close()
    file = open("json/%s.json" % Files[i][4:-4], "w", encoding="UTF-8")
    json.dump(entry, file, indent="\t", ensure_ascii=False)
    file.close()