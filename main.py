import sys

import parser
import converter
import writer
from globals import *

file = None
filename = ""

filenames = sys.argv[1:] # get all of the words in the filename, incase there are spaces
for i in filenames:
    filename += i + " "
if filename.strip() == "":
    print("no file name provided. command syntax is: main.py path/to/your/beatmap.osu")
    exit()
try:
    file = open(filename, "r", encoding="utf-8")
except:
    print("error occurred while trying to open the beatmap, maybe you put the wrong file name in?")
    exit()

# parse
chart = parser.parse(file)

# convert
bchart = converter.converter(chart).convert()

# write
writer.write(bchart, chart)

print(f"finished!")