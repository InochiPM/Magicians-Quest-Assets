import numpy
import sys
import json

header_size = 0x1F40

file = open("0001_1C7B2A01.rdbt", "rb")

if (file.read(0x10) != b"\x52\x45\x53\x4F\xE8\x03\x00\x00\x31\x2E\x32\x31\x01\x00\x00\x00"):
    print("Wrong header!")
    sys.exit()

table = []

while (file.tell() < header_size):
    entry = {}
    entry["Size"] = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
    entry["Offset"] = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
    table.append(entry)

messages = []

for i in range(0, len(table)):
    if (table[i]["Size"] == 0): continue
    file.seek(table[i]["Offset"], 0)
    text = file.read(table[i]["Size"]-2)
    entry = {}
    entry["Index"] = i
    entry["Text"] = text.decode("UTF-16-LE")
    messages.append(entry)

file.close()

file = open("0001_1C7B2A01.json", "w", encoding="UTF-8")
json.dump(messages, file, indent="\t", ensure_ascii=False)
file.close()