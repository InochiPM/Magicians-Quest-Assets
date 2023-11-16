import json
import glob
import os
import numpy
import sys

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

def CheckStringSize(string, position, filename):
	if (SizeCheck["%d" % position] < len(string)):
		print("Size check error! Offset: %d, file name: %s" % (position, filename))
		print("Max size: %d, detected: %d" % (SizeCheck["%d" % position], len(string)))
		sys.exit()

try:
	os.mkdir("DAT_new")
except:
	pass

Files = glob.glob("json/*.json")

for i in range(0, len(Files)):
	print("Converting %s to DAT" % Files[i])
	jsonfile = open(Files[i], "r", encoding="UTF-8")
	DUMP = json.load(jsonfile)
	jsonfile.close()
	dat = open("DAT_new/%s.dat" % Files[i][5:-5], "wb")
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

DAT_list = glob.glob("DAT_new/*.dat")

main_block = []
header = []
offset = 0

try:
	os.mkdir("Compiled")
except:
	pass

RDBT = open("Compiled/0004_NpcDataOfs_098D3004.rdbt", "wb")
print("Writing Compiled/0004_NpcDataOfs_098D3004.rdbt")

for i in range(0, len(DAT_list)):
	entry = {}
	file = open(DAT_list[i], "rb")
	file.seek(0, 2)
	filesize = file.tell()
	file.seek(0, 0)
	if (filesize != 0xB0):
		print("File size error! %s" % Files[i])
		sys.exit()
	entry["Index"] = int(DAT_list[i][8:-4], 10)
	entry["Offset"] = offset
	entry["Size"] = filesize
	offset += filesize
	header.append(entry)
	RDBT.write(file.read())
	file.close()

RDBT.close()

RNDX = open("Compiled/0000_NpcDataOfs_098C2E00.rndx", "wb")
print("Compiled/0000_NpcDataOfs_098C2E00.rndx")
for i in range(0, len(header)):
	RNDX.write(numpy.uint32(header[i]["Index"]))
	RNDX.write(numpy.uint32(header[i]["Offset"]))
	RNDX.write(numpy.uint32(header[i]["Size"]))

RNDX.close()