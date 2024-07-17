import json
import sys
import os
import numpy
import pathlib

header_size = 0x38

file = open(sys.argv[1], "r", encoding="UTF-8")
filename = pathlib.Path(sys.argv[1]).stem

JSONfile = json.load(file)
file.close()

strings = []
strings_offset_table = []
filename_offsets = []

for i in range(0, len(JSONfile["STRINGS"])):
    strings_offset_table.append(numpy.uint32(len(b"".join(strings))+header_size))
    strings.append(JSONfile["STRINGS"][i].encode("UTF-16-LE"))
    strings.append(b"\x00\x00")
filename_offsets.append(len(b"".join(strings)))
strings.append(filename.encode("UTF-8"))
strings.append(b"\x00")
filename_offsets.append(len(b"".join(strings)))
strings.append(b"\x00")

string_section_size = len(b"".join(strings))
while(len(b"".join(strings)) % 16 != 0):
    strings.append(b"\x00")
strings_section = b"".join(strings)
Offset_table_start = len(strings_section) + header_size

pointers_table_start = len(b"".join(strings_offset_table))
while (pointers_table_start % 16 != 0):
    pointers_table_start += 2
pointers_table_start += header_size + len(strings_section)

filename = os.path.basename(sys.argv[1])[:-5]
file = open("%s.bin" % filename, "wb")
file.write(numpy.uint32(len(JSONfile["STRINGS"]))) #entries_count
file.write(numpy.uint32(4)) #UNK_x4
file.write(numpy.uint32(header_size)) #header_size
file.write(numpy.uint32(string_section_size)) #string_section_size
file.write(numpy.uint32(Offset_table_start)) #Offset_table_start
file.write(numpy.uint32(len(JSONfile["STRINGS"]) * 4)) # Table_size
file.write(numpy.uint32(pointers_table_start)) #Pointers_offsets_table_start
file.write(numpy.uint32(len(JSONfile["STRINGS"]))) #entries_count_2
file.write(numpy.uint32(0)) #DUMMY
file.write(numpy.uint32(filename_offsets[0])) #filename_offset_start
file.write(numpy.uint32(filename_offsets[1])) #filename_offset_end
file.write(numpy.uint32(0)) #DUMMY
file.write(bytes.fromhex(JSONfile["HASH"]))
file.write(numpy.uint32(0)) #DUMMY
file.write(strings_section)
File_size = file.tell()
while (len(b"".join(strings_offset_table)) % 16 != 0):
    strings_offset_table.append(numpy.uint32(0))
file.write(b"".join(strings_offset_table))
for i in range(0, len(JSONfile["STRINGS"])):
    file.write(numpy.uint32(File_size + (i * 4)))
file.close()