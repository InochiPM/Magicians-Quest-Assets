import json
import sys
import os
import numpy

def RepeatedText(Dump, index):
    for i in range(0, index):
        if (DUMP[i]["Text"] == DUMP[index]["Text"]): 
            return True, i
    return False, -1

file = open("0000 (09BB2A00).json", "r", encoding='utf-8')
DUMP = json.load(file)
file.close()

header_size = 0x1A05 * 8 + 0x10
while (header_size % 16 != 0):
    header_size += 8

try:
    os.mkdir("Compiled")
except:
    pass

file = open("Compiled/0000 (09BB2A00).rdbt", "wb")
print("Writing Compiled/0000 (09BB2A00).rdbt...")

file.write(b"\x52\x45\x53\x4F\x05\x1A\x00\x00\x31\x2E\x32\x31\x01\x00\x00\x00")

main_block = []
offsets = []
offset = 0
file_offset = 0
i = 0
null_pointer = False
flag = False
while (offset < len(DUMP)):
    if (DUMP[offset]["Index"] != i):
        file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        i += 1
        continue
    if ((len(DUMP[i]["Text"]) == 0) and (null_pointer == False)):
        main_block.append(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        null_pointer = True
    Check, index = RepeatedText(DUMP, offset)
    if (Check == True):
        file.write(numpy.uint32(len(DUMP[index]["Text"].encode("UTF-16-LE")) + 2))
        file.write(numpy.uint32(offsets[index]))
        offsets.append(offsets[index])
    else:
        file.write(numpy.uint32(len(DUMP[offset]["Text"].encode("UTF-16-LE")) + 2))
        file.write(numpy.uint32(header_size + file_offset))
        offsets.append(header_size + file_offset)
        if (len(DUMP[offset]["Text"].encode("UTF-16-LE")) != 0):
            main_block.append(DUMP[i]["Text"].encode("UTF-16-LE"))
            main_block.append(b"\x00\x00")
            while (len(b"".join(main_block)) % 16 != 0):
                main_block.append(b"\x00\x00")
            size = len(DUMP[offset]["Text"].encode("UTF-16-LE")) + 2
            while (size % 16 != 0):
                size += 2
            file_offset += size
        else:
            file_offset += 0x10
    offset += 1
    i += 1

while (file.tell() < header_size):
    file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")

file.write(b"".join(main_block))

file.close()
