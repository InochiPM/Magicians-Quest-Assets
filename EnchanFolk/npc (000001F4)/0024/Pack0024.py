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


os.makedirs("DAT_new", exist_ok=True)

Files = glob.glob("json/*.json")

for i in range(0, len(Files)):
	print("Converting %s to DAT" % Files[i])
	jsonfile = open(Files[i], "r", encoding="UTF-8")
	DUMP = json.load(jsonfile)
	jsonfile.close()
	dat = open("DAT_new/%s.dat" % GetNumber(Files[i]), "wb")
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

List = glob.glob("DAT_new/*.dat")
List.sort(key=GetNumber)

Data = []

for i in range(0, len(List)):
	file = open(List[i], "rb")
	Data.append(file.read())
	file.close()

main_block = []
header = []
offset = 0

try:
	os.mkdir("Compiled")
except:
	pass

RDBT = open("Compiled/0024_NpcDataVlg_09700018.npvdt", "wb")
print("Writing Compiled/0024_NpcDataVlg_09700018.npvdt")

header_size = 0xC

RDBT.write(numpy.uint32(1))
RDBT.write(numpy.uint32(header_size))
RDBT.write(numpy.uint32(0xA0))
RDBT.write(b"".join(Data))

RDBT.close()