import json
import os
import re
import glob
import numpy

def RepeatedText(Dump, index):
    for i in range(0, index):
        if (DUMP[i]["JPN"] == DUMP[index]["JPN"]): 
            return True, i
    return False, -1

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

file_list = glob.glob("json/*.json")

for x in range(0, len(file_list)):
    print("Converting %s to RESO_new" % file_list[x])
    file = open(file_list[x], "r", encoding="UTF-8")
    DUMP = json.load(file)
    file.close()

    header = []
    header.append(b"\x52\x45\x53\x4F\x64\x00\x00\x00\x31\x2E\x32\x31\x01\x00\x00\x00")
    header_info = {}

    main_block = []

    offset = 0x330

    DEBUG_info = []

    for i in range(0, len(DUMP)):
        entry = []
        header_info_temp = {}
        RepeatCheck, index = RepeatedText(DUMP, i)
        if (RepeatCheck == True): 
            header_info_temp["SIZE"] = DEBUG_info[index]["SIZE"]
            header_info_temp["OFFSET"] = DEBUG_info[index]["OFFSET"]
            header_info["%d" % DUMP[i]["Index"]] = header_info_temp
            DEBUG_info.append(header_info_temp)
            continue
        for c in range(0, len(DUMP[i]["JPN"])):
            CMDCheck = DUMP[i]["JPN"][c].count("<CMD>")
            if (CMDCheck > 0): 
                entry.append(ConvertCMDtoDol(DUMP[i]["JPN"][c]))
            else: entry.append(DUMP[i]["JPN"][c].replace("<BREAK>", "▼").encode("UTF-16-LE"))
            if (c != (len(DUMP[i]["JPN"])-1)): entry.append(b"\x00\x00")
            header_info_temp["SIZE"] = len(b"".join(entry))
        while (len(b"".join(entry)) % 16 != 0):
            entry.append(b"\x00\x00")
        header_info_temp["OFFSET"] = offset
        offset += len(b"".join(entry))
        header_info["%d" % DUMP[i]["Index"]] = header_info_temp
        DEBUG_info.append(header_info_temp)
        main_block.append(b"".join(entry))

    for i in range(0, 100):
        try:
            header.append(header_info["%d" % i]["SIZE"].to_bytes(4, byteorder="little"))
        except:
            header.append(b"\x00\x00\x00\x00\x00\x00\x00\x00")
            continue
        header.append(header_info["%d" % i]["OFFSET"].to_bytes(4, byteorder="little"))
    file = open("RESO_new/%s.reso" % file_list[x][5:-5], "wb")
    file.write(b"".join(header))
    file.write(b"".join(main_block))
    file.close()


try:
    os.mkdir("Compiled")
except:
    pass

files = glob.glob("RESO_new/*.reso")
files.sort(key=takeNumber)

Pointers = []

main_block = open("Compiled/0002_message_09693002.rdbt", "wb")
print("Writing Compiled/0002_message_09693002.rdbt")

offset = 0
for i in range(0, len(files)):
    file = open(files[i], "rb")
    entry = {}
    entry["Index"] = int(files[i][9:-5], 10)
    entry["Offset"] = offset
    file.seek(0, 2)
    entry["Size"] = file.tell()
    offset += file.tell()
    file.seek(0, 0)
    Pointers.append(entry)
    main_block.write(file.read())
    file.close()

main_block.close()

Pointers.sort(key=takeIndex)

file = open("Compiled/0000_message_09682E00.rndx", "wb")
print("Writing Compiled/0000_message_09682E00.rndx")

for i in range(0, len(Pointers)):
    file.write(Pointers[i]["Index"].to_bytes(4, byteorder="little"))
    file.write(Pointers[i]["Offset"].to_bytes(4, byteorder="little"))
    file.write(Pointers[i]["Size"].to_bytes(4, byteorder="little"))

file.close()