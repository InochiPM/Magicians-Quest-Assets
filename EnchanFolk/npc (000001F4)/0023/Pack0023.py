import json
import glob
import os
import numpy
import sys
import pathlib

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

def GetNumber(elem):
	return int(pathlib.Path(elem).stem)

def CheckStringSize(string, position, filename):
	if (SizeCheck["%d" % position] < len(string)):
		print("Size check error! Offset: %d, file name: %s" % (position, filename))
		print("Max size: %d, detected: %d" % (SizeCheck["%d" % position], len(string)))
		sys.exit()


os.makedirs("DAT_new/CAT_0", exist_ok=True)
os.makedirs("DAT_new/CAT_1", exist_ok=True)
os.makedirs("DAT_new/CAT_2", exist_ok=True)
os.makedirs("DAT_new/CAT_3", exist_ok=True)

Files = glob.glob("json/**/*.json")

for i in range(0, len(Files)):
	print("Converting %s to DAT" % Files[i])
	jsonfile = open(Files[i], "r", encoding="UTF-8")
	DUMP = json.load(jsonfile)
	jsonfile.close()
	if (Files[i].count("CAT_0") > 0):
		dat = open("DAT_new/CAT_0/%s.dat" % GetNumber(Files[i]), "wb")
	elif (Files[i].count("CAT_1") > 0):
		dat = open("DAT_new/CAT_1/%s.dat" % GetNumber(Files[i]), "wb")
	elif (Files[i].count("CAT_2") > 0):
		dat = open("DAT_new/CAT_2/%s.dat" % GetNumber(Files[i]), "wb")
	elif (Files[i].count("CAT_3") > 0):
		dat = open("DAT_new/CAT_3/%s.dat" % GetNumber(Files[i]), "wb")
	dat.write(bytes.fromhex(DUMP["Args"]))
	dat.write(b"\x0F\x0F\x0F\x0F")
	for c in range(0, len(DUMP["Strings"])):
		CheckStringSize(DUMP["Strings"][c]["Text"], DUMP["Strings"][c]["Offset"], Files[i])
		while(dat.tell() < DUMP["Strings"][c]["Offset"]):
			dat.write(b"\x00\x00")
		if (dat.tell() != DUMP["Strings"][c]["Offset"]):
			print("Error while processing %s!" % Files[i])
			sys.exit()
		dat.write(DUMP["Strings"][c]["Text"].encode("UTF-16-LE"))
		dat.write(b"\x00\x00")
	while(dat.tell() < 0x98):
		dat.write(b"\x00\x00")
	dat.write(bytes.fromhex(DUMP["Arg2"]))
	dat.close()

CAT_0_list = glob.glob("DAT_new/CAT_0/*.dat")
CAT_1_list = glob.glob("DAT_new/CAT_1/*.dat")
CAT_2_list = glob.glob("DAT_new/CAT_2/*.dat")
CAT_3_list = glob.glob("DAT_new/CAT_3/*.dat")
CAT_0_list.sort(key=GetNumber)
CAT_1_list.sort(key=GetNumber)
CAT_2_list.sort(key=GetNumber)
CAT_3_list.sort(key=GetNumber)

CAT_0_Data = []
CAT_1_Data = []
CAT_2_Data = []
CAT_3_Data = []

for i in range(0, len(CAT_0_list)):
	file = open(CAT_0_list[i], "rb")
	CAT_0_Data.append(file.read())
	file.close()

for i in range(0, len(CAT_1_list)):
	file = open(CAT_1_list[i], "rb")
	CAT_1_Data.append(file.read())
	file.close()

for i in range(0, len(CAT_2_list)):
	file = open(CAT_2_list[i], "rb")
	CAT_2_Data.append(file.read())
	file.close()

for i in range(0, len(CAT_3_list)):
	file = open(CAT_3_list[i], "rb")
	CAT_3_Data.append(file.read())
	file.close()

main_block = []
header = []
offset = 0

try:
	os.mkdir("Compiled")
except:
	pass

RDBT = open("Compiled/0023_NpcData_096E0017.npdt", "wb")
print("Writing Compiled/0023_NpcData_096E0017.npdt")

header_size = 0x24

RDBT.write(numpy.uint32(4))
RDBT.write(numpy.uint32(header_size))
RDBT.write(numpy.uint32(header_size + len(b"".join(CAT_0_Data))))
RDBT.write(numpy.uint32(header_size + len(b"".join(CAT_0_Data)) + len(b"".join(CAT_1_Data))))
RDBT.write(numpy.uint32(header_size + len(b"".join(CAT_0_Data)) + len(b"".join(CAT_1_Data)) + len(b"".join(CAT_2_Data))))
RDBT.write(numpy.uint32(0xA0))
RDBT.write(numpy.uint32(0x25))
RDBT.write(numpy.uint32(0xD))
RDBT.write(numpy.uint32(0x4A))
RDBT.write(b"".join(CAT_0_Data))
RDBT.write(b"".join(CAT_1_Data))
RDBT.write(b"".join(CAT_2_Data))
RDBT.write(b"".join(CAT_3_Data))

RDBT.close()