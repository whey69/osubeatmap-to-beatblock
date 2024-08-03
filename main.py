import sys
import random
import json
import os

true = True
false = False

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

### parse the osu file

chart = {}
section = ""
while true:
    line = file.readline().removesuffix("\n")
    if (line == "[TimingPoints]"):
        section = "timing"
        chart["timing"] = []
        chart["approaches"] = []
    if (line == ""):
        if (section == "hit"):
            break # we read all of the useful info
        section = "" # assume that the section ended
    if (line == "[HitObjects]"):
        section = "hit"
        chart["hitobjects"] = []
    if (line == "[Metadata]"):
        section = "metadata"
        chart["metadata"] = {}
    if (line == "[General]"):
        section = "general"
        chart["general"] = {}

    if section == "timing":
        # parse timing points (aka bpm changes)
        data = line.split(",")
        
        if len(data) > 1: 
            # https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#timing-points
            timingpoint = {}
            timingpoint["time"] = float(data[0]) # this is supposed to be an int apparently
            timingpoint["beatLength"] = float(data[1])
            timingpoint["meter"] = int(data[2])
            timingpoint["sampleSet"] = int(data[3])
            timingpoint["sampleIndex"] = int(data[4])
            timingpoint["volume"] = int(data[5])
            timingpoint["uninherited"] = int(data[6])
            timingpoint["effects"] = int(data[7])
            timingpoint["bpm"] = round(1 / float(data[1]) * 1000 * 60) # not in docs btw
            if timingpoint["uninherited"] == 1: # store slider multipliers separately
                chart["timing"].append(timingpoint)
            elif timingpoint["beatLength"] < 0:
                # assume that since beatlength is negative, we are dealing with a approach multiplier
                timingpoint["multiplier"] = timingpoint["beatLength"] * -1 / 100
                # print(timingpoint["multiplier"])
                chart["approaches"].append(timingpoint)
    
    if section == "hit":
        # parse hit objects
        data = line.split(",")

        if len(data) > 1:
            #https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#hit-objects
            hitobject = {}
            hitobject["x"] = int(data[0])
            hitobject["y"] = int(data[1])
            hitobject["time"] = float(data[2])
            hitobject["type"] = int(data[3])
            hitobject["hitSound"] = int(data[4])
            if hitobject["type"] == 128:
                hitobject["endTime"] = float(data[5].split(":")[0]) - 10 # move the end a little bit so that there is time to jump to note far away
            else:
                hitobject["endTime"] = data[5].split(":")[0] # theres probably a better way to handle this 
                if chart["general"]["mode"] == "1":
                    if hitobject["hitSound"] == 4 or hitobject["hitSound"] == 12 or (hitobject["hitSound"] == 2 and chart["general"]["katTap"] == true):
                        hitobject["tap"] = true
                    else:
                        hitobject["tap"] = false
                else:
                    hitobject["tap"] = false
            hitobject["hitSample"] = data[5].split(":")[1:]
            chart["hitobjects"].append(hitobject)
    
    if section == "metadata":
        if line.lower().find("title:") != -1:
            chart["metadata"]["title"] = line.removeprefix("Title:").strip()
        elif line.lower().find("artist:") != -1:
            chart["metadata"]["artist"] = line.removeprefix("Artist:").strip()
        elif line.lower().find("creator:") != -1:
            chart["metadata"]["creator"] = line.removeprefix("Creator:").strip()
        elif line.lower().find("version:") != -1:
            chart["metadata"]["version"] = line.removeprefix("Version:").strip()

    if section == "general":
        if line.lower().find("audiofilename:") != -1:
            chart["general"]["audiofilename"] = line.removeprefix("AudioFilename:").strip()
        elif line.lower().find("mode:") != -1:
            chart["general"]["mode"] = line.removeprefix("Mode:").strip()
            if chart["general"]["mode"] == "1":
                ask = input("your beatmap is osu!taiko. make every kat a tap block? (y/N): ")
                if ask.lower() == "yes" or ask.lower() == "y":
                    chart["general"]["katTap"] = true
                else:
                    chart["general"]["katTap"] = false
            else:
                chart["general"]["katTap"] = false
            if chart["general"]["mode"] == "0" or chart["general"]["mode"] == "2":
                # TODO: implement catch mode
                print("your beatmap's mode is unsupported, proceed with caution")


print("finished extracting the beatmap")

### convert into beatblock format

def getSection(time):
    b = chart["timing"][0]
    for i in chart["timing"]:
        if i["time"] <= time and i["time"] >= b["time"]:
            b = i
    return b

def convert_ms_to_beats(ms, transitions):
    total_beats = 0
    reached_end = false

    # add up all of the beats between transitions
    for c, i in enumerate(transitions):
        t2 = -1
        # there are timing points left
        if c < len(transitions) - 1:
            t2 = transitions[c+1]["time"]
            if transitions[c+1]["time"] > ms:
                t2 = ms
                reached_end = true
        # there are no more timing points left, use the end note as a timing
        if c >= len(transitions) - 1:
            t2 = chart["hitobjects"][-1]["time"]
            if chart["hitobjects"][-1]["time"] > ms:
                t2 = ms
        
        if t2 != -1:
            time = abs(transitions[c]["time"] - t2)
            beats = time / transitions[c]["beatLength"]
            total_beats += beats
        if reached_end == true:
            break

    return abs(total_beats)
    
transitions = []
for c, i in enumerate(chart["timing"]):
    if c == 0 and i["time"] >= 100:
        # create a fake timing point at the beggining to handle an edge case
        t = {}
        t["time"] = 0
        t["bpm"] = i["bpm"]
        t["beatLength"] = i["beatLength"]
        transitions.append(t)
    t = {}
    t["time"] = i["time"]
    t["bpm"] = i["bpm"]
    t["beatLength"] = i["beatLength"]
    transitions.append(t)

add_angle = 0
angle_multiplier = 2
taiko_multiplier = 10 # slightly random position of taiko big notes
rng_counter = 0
bchart = []
for i, val in enumerate(chart["hitobjects"]):
    note = None
    # blocks
    if val["type"] == 1:
        note = {}
        note["type"] = "block"
        # calculate approximate location (likely inaccurate if bpm changes)
        section = getSection(val["time"])
        # beatvalue = val["time"] / section["beatLength"]
        beatvalue = convert_ms_to_beats(val["time"], transitions)
        note["time"] = beatvalue
        angle = val["x"] / 128
        note["angle"] = (angle * angle_multiplier) + add_angle + (random.randint(-taiko_multiplier, taiko_multiplier) if val["tap"] else 0)
        note["tap"] = val["tap"]

    # holds
    if val["type"] == 128:
        note = {}
        note["type"] = "hold"
        section = getSection(val["time"])
        # beatvalue = val["time"] / section["beatLength"]
        # note["time"] = beatvalue
        # beatvalue2 = (val["endTime"] / section["beatLength"]) - beatvalue
        # note["duration"] = beatvalue2
        beatvalue = convert_ms_to_beats(val["time"], transitions)
        note["time"] = beatvalue
        beatvalue2 = abs(convert_ms_to_beats(val["endTime"], transitions) - beatvalue)
        note["duration"] = beatvalue2
        angle = val["x"] / 128
        note["angle"] = (angle * angle_multiplier) + add_angle
        note["angle2"] = (angle * angle_multiplier) + add_angle

    if note:
        bchart.append(note)
        rng_counter += 1
        if rng_counter >= 10:
            add_angle += random.randint(-45, 45)
            rng_counter = 0
        if chart["general"]["mode"] == "1":
            add_angle += random.randint(-10, 10)

print("finished converting the beatmap")

### write it to a file 
noaudio = false

# try to create the output folder
try:
    os.mkdir("output")
except:
    print("output folder already exists, overwriting")

# write the main chart
with open("output/chart.json", "w") as file:
    data = json.dumps(bchart)
    file.write(data)

# write the level chart
with open("output/level.json", "w") as file:
    level = {}
    level["events"] = []

    # bpm changes
    for c, i in enumerate(chart["timing"]):
        # if c == 0: # ignore the first element
        #     continue
        event = {}
        event["type"] = "setBPM"
        event["time"] = convert_ms_to_beats(i["time"], transitions)
        event["angle"] = 90
        event["bpm"] = i["bpm"]
        level["events"].append(event)

    # block approach speed changes
    for c, i in enumerate(chart["approaches"]):
        event = {}
        event["type"] = "ease"
        event["time"] = convert_ms_to_beats(i["time"], transitions)
        event["angle"] = 270
        event["value"] = i["multiplier"]
        event["var"] = "scrollSpeed"
        level["events"].append(event)
    
    # end the level
    event = {
        "time": convert_ms_to_beats(chart["hitobjects"][-1]["time"], transitions) + 1,
        "type": "showResults",
        "angle": 0
    }
    level["events"].append(event)
    
    # try to play the song
    try:
        event = {
            "type": "play",
            "angle": 180,
            "time": 0,
            "bpm": chart["timing"][0]["bpm"],
            "file": (chart["general"]["audiofilename"] if chart["general"]["audiofilename"] != None else "")
        }
        level["events"].append(event)
        if ".mp3" in event["file"]:
            print("warning: used audio file is very likely to be rejected by the game")
    except KeyError as e:
        noaudio = true
        print("no audiofile name found, proceeding without playsong element")

    # properties
    level["properties"] = {
        "formatversion": 10,
        "speed": 70,
        "startBeat": chart["timing"][0]["bpm"], # overriden by above
        "offset": 8
    }

    # metadata
    level["metadata"] = {
        "bg": false,
        "songName": chart["metadata"]["title"],
        "description": "Converted using osumania-to-beatblock",
        "charter": chart["metadata"]["creator"],
        "artistLink": "",
        "artist": chart["metadata"]["artist"],
        "difficulty": 0 
    }

    file.write(json.dumps(level))

print(f"finished!{" dont forget to put the audio file in the beatblock map directory" if not noaudio else ""}")