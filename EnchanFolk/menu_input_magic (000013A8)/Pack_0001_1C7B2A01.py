import json
import sys
import os
import numpy

file = open("0001_1C7B2A01.json", "r", encoding='utf-8')
DUMP = json.load(file)
file.close()

try:
    os.mkdir("Compiled")
except:
    pass

file = open("Compiled/0001_1C7B2A01.rdbt", "wb")
print("Writing Compiled/0001_1C7B2A01.rdbt...")

file.write(b"\x52\x45\x53\x4F\xE8\x03\x00\x00\x31\x2E\x32\x31\x01\x00\x00\x00")

offset = 0
file_offset = 0
i = 0
while (offset < len(DUMP)):
    if (DUMP[offset]["Index"] != i):
        file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        i += 1
        continue
    file.write(numpy.uint32(len(DUMP[offset]["Text"].encode("UTF-16-LE")) + 2))
    file.write(numpy.uint32(0x1F50 + file_offset))
    size = len(DUMP[offset]["Text"].encode("UTF-16-LE")) + 2
    while (size % 16 != 0):
        size += 2
    file_offset += size
    offset += 1
    i += 1

while (file.tell() < 0x1F50):
    file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")

for i in range(0, len(DUMP)):
    if (len(DUMP[i]["Text"]) == 0):
        file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        continue
    file.write(DUMP[i]["Text"].encode("UTF-16-LE"))
    file.write(b"\x00\x00")
    while (file.tell() % 16 != 0):
        file.write(b"\x00\x00")

file.close()