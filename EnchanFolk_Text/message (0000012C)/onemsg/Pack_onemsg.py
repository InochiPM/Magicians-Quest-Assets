import json
import os
import re
import glob
import numpy

def takeIndex(elem):
    return elem["Index"]

def takeNumber(elem):
    return int(elem[9:-5], 10)

def ConvertCMDtoDol(string):
    count = string.count("<CMD>")
    array = []
    for z in range(0, count):
        entry = {}
        results = re.search("<CMD>(.*?)</CMD>", string)
        entry["STRING"] = results.group(1)
        string = string.replace("<CMD>", "$", 1).replace("</CMD>", ";", 1)
        array.append(entry)
    string = string.replace("<BREAK>", "▼").encode("UTF-16-LE")
    for s in range(0, len(array)):
        string = string.replace(array[s]["STRING"].encode("UTF-16-LE"), bytes.fromhex(array[s]["STRING"]), 1)
    return string

try:
    os.mkdir("RESO_new")
except:
    pass

header_size = 0x330

file = open("json/onemsg.json", "r", encoding="UTF-8")
DUMP = json.load(file)
file.close()

offset = 0

header_info = {}

DEBUG_info = []

for i in range(0, len(DUMP)):
    entry = []
    header_info_temp = {}
    for c in range(0, len(DUMP[i]["JPN"])):
        CMDCheck = DUMP[i]["JPN"][c].count("<CMD>")
        if (CMDCheck > 0): 
            entry.append(ConvertCMDtoDol(DUMP[i]["JPN"][c]))
        else: entry.append(DUMP[i]["JPN"][c].replace("<BREAK>", "▼").encode("UTF-16-LE"))
        entry.append(b"\x00\x00")
        header_info_temp["SIZE"] = len(b"".join(entry))
    header_info_temp["OFFSET"] = offset
    offset += len(b"".join(entry))
    header_info["%d" % DUMP[i]["Index"]] = header_info_temp
    DEBUG_info.append(header_info_temp)

    file = open("RESO_new/%d.reso" % DUMP[i]["Index"], "wb")
    print("Writing RESO_new/%d.reso"  % DUMP[i]["Index"])
    file.write(b"".join(entry))
    file.close()


try:
    os.mkdir("Compiled")
except:
    pass

files = glob.glob("RESO_new/*.reso")
files.sort(key=takeNumber)

Pointers = []

main_block = open("Compiled/0003 onemsg (09F93003).rdbt", "wb")
print("Writing Compiled/0003 onemsg (09F93003).rdbt")
blob = []
offset = 0
for i in range(0, len(files)):
    file = open(files[i], "rb")
    entry = {}
    entry["Index"] = int(files[i][9:-5], 10)
    entry["Offset"] = offset
    file.seek(0, 2)
    entry["Size"] = file.tell()
    offset += entry["Size"]
    file.seek(0, 0)
    Pointers.append(entry)
    blob.append(file.read())
    file.close()

main_block.write(b"".join(blob))
main_block.close()

Pointers.sort(key=takeIndex)

file = open("Compiled/0001 onemsg (09F82E01).rndx", "wb")
print("Writing Compiled/0001 onemsg (09F82E01).rndx")

for i in range(0, len(Pointers)):
    file.write(Pointers[i]["Index"].to_bytes(4, byteorder="little"))
    file.write(Pointers[i]["Offset"].to_bytes(4, byteorder="little"))
    file.write(Pointers[i]["Size"].to_bytes(4, byteorder="little"))

file.close()