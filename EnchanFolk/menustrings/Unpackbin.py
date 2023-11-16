import json
import numpy
import sys

def readString(myfile):
    chars = []
    while True:
        c = myfile.read(2)
        if c == b'\x00\x00':
            return str(b"".join(chars).decode("UTF-16-LE"))
        chars.append(c)

file = open("itemslot.bin", 'rb')

entries_count = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
UNK_x4 = file.read(4)

header_size = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
string_section_size = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
Offset_table_start = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
# Size matches both tables (string offsets and pointer offsets)
Table_size = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
Pointers_offsets_table_start = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
entries_count_2 = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
DUMMY = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
# Filename offsets are ignoring header
filename_offset_start = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
filename_offset_end = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
DUMMY = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]
CRC32 = file.read(4)
DUMMY = numpy.fromfile(file, dtype=numpy.uint32, count=1)[0]

offset_table = []

file.seek(-1 * Table_size, 2)
for i in range(0, entries_count):
    offset_table.append(numpy.fromfile(file, dtype=numpy.uint32, count=1)[0])

string_offset_table = []

for i in range(0, entries_count):
    file.seek(offset_table[i], 0)
    string_offset_table.append(numpy.fromfile(file, dtype=numpy.uint32, count=1)[0])

strings = []

for i in range(0, entries_count):
    file.seek(string_offset_table[i], 0)
    strings.append(readString(file))
    
file.seek(header_size, 0)
file.seek(filename_offset_start, 1)
name = file.read(filename_offset_end-filename_offset_start-1).decode("UTF-8")
file.close()

file = open("%s.json" % name, "w", encoding="UTF-8")
JSON = {}
JSON["HASH"] = CRC32.hex()
JSON["STRINGS"] = strings
json.dump(JSON, file, indent="\t", ensure_ascii=False)
file.close()