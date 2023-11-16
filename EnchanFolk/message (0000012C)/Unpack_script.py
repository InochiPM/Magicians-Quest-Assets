import sys
import json
import glob
import os

def readString(string):
	chars = []
	base = []
	offset = 0
	while (offset <= len(string)):
		c = string[offset:offset+2]
		if c == b"\x24\x00":
			chars.append("<CMD>")
			while (True):
				offset += 2
				c = string[offset:offset+2]
				if (c == b"\x3B\x00"): break
				chars.append(c.hex())
			chars.append("</CMD>")
		elif c == b'\x00\x00':
			base.append("".join(chars).replace("▼", "<BREAK>"))
			chars = []
		elif c == b'\x5B\x00':
			chars.append(c.decode("UTF-16-LE"))
			while (True):
				offset += 2
				c = string[offset:offset+2]
				chars.append(c.decode("UTF-16-LE"))
				if (c == b"\x5D\x00"):
					break
		else: chars.append(c.decode("UTF-16-LE"))
		offset += 2
	return base

header_size = 0x330

file = open("message.rndx", "rb")
SCRIPT = open("message.rdbt", "rb")

file.seek(0, 2)
size = file.tell()
file.seek(0,0)

table = []

while (file.tell() < size):
	entry = {}
	entry["Index"] = int.from_bytes(file.read(4), "little")
	entry["Offset"] = int.from_bytes(file.read(4), "little")
	entry["Size"] = int.from_bytes(file.read(4), "little")
	table.append(entry)

file.close()

try:
	os.mkdir("RESO")
except:
	pass

for i in range(0, len(table)):
	print("Unpacking %s.reso" % table[i]["Index"])
	file = open("RESO/%d.reso" % table[i]["Index"], "wb")
	file.write(SCRIPT.read(table[i]["Size"]))
	file.close()

file_list = glob.glob("RESO/*.reso")

try:
	os.mkdir("json")
except:
	pass

for x in range(0, len(file_list)):
	print("Dumping %s to JSON" % file_list[x][5:])
	file = open(file_list[x], "rb")
	header = file.read(0x10)
	if (header != b"\x52\x45\x53\x4F\x64\x00\x00\x00\x31\x2E\x32\x31\x01\x00\x00\x00"):
		print("Wrong header!")
		sys.exit()

	table = []

	i = 0
	while(file.tell() < header_size):
		size = int.from_bytes(file.read(4), "little")
		if (size == 0):
			file.seek(4, 1)
			i += 1
			continue
		entry = {}
		entry['Index'] = i
		entry['Size'] = size
		entry['Offset'] = int.from_bytes(file.read(4), "little")
		table.append(entry)
		i += 1

	Messages = []

	for s in range(0, len(table)):
		file.seek(table[s]["Offset"])
		temp = file.read(table[s]["Size"])
		entry = {}
		entry['Index'] = table[s]["Index"]
		strings = []
		count = temp.count(b"\x00\x00")
		entry["JPN"] = readString(temp)
		if (temp[-2:] == b"\x0c\x00"): entry["JPN"].append(temp[-2:].decode("UTF-16-LE"))
		else: 
			print("Something went wrong. %s" % bytes(temp[-2:]))
			sys.exit()
		Messages.append(entry)

	file.close()
	file = open("json/%s.json" % file_list[x][5:-5], "w", encoding="UTF-8")
	json.dump(Messages, file, indent="\t", ensure_ascii=False)
	file.close()