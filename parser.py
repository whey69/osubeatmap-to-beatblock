from globals import *

### parse the osu file

def parse(file):
    """
    function to parse an osu beatmap \n
    accepts file as the first argument, returns the extracted chart
    """
    chart = {}
    section = ""
    while true:
        line = file.readline().removesuffix("\n")
        if (line == "[TimingPoints]"):
            section = "timing"
            chart["timing"] = []
            chart["approaches"] = []
            chart["kiais"] = []
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
                timingpoint = {
                    "time": float(data[0]), # this is supposed to be an int apparently
                    "beatLength": float(data[1]),
                    "meter": int(data[2]),
                    "sampleSet": int(data[3]),
                    "sampleIndex": int(data[4]),
                    "volume": int(data[5]),
                    "uninherited": int(data[6]),
                    "effects": int(data[7]),
                    "bpm": 1 / float(data[1]) * 1000 * 60 # not in docs btw
                }
                if timingpoint["uninherited"] == 1: # store slider multipliers separately
                    chart["timing"].append(timingpoint)
                elif timingpoint["beatLength"] < 0:
                    # assume that since beatlength is negative, we are dealing with a approach multiplier
                    timingpoint["multiplier"] = timingpoint["beatLength"] * -1 / 100
                    # print(timingpoint["multiplier"])
                    chart["approaches"].append(timingpoint)
                if timingpoint["effects"] & 0x00000001 == 0x00000001: # i should probably go around the code and include these in
                    chart["kiais"].append(timingpoint)
        
        if section == "hit":
            # parse hit objects
            data = line.split(",")

            if len(data) > 1:
                #https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#hit-objects
                hitobject = {
                    "x": int(data[0]),
                    "y": int(data[1]),
                    "time": float(data[2]),
                    "type": int(data[3]),
                    "hitSound": int(data[4]),
                    "hitSample": data[5].split(":")[1:]
                }
                if hitobject["type"] & 0b10000000 == 0b10000000:
                    hitobject["endTime"] = float(data[5].split(":")[0]) - 10 # move the end a little bit so that there is time to jump to note far away
                else:
                    hitobject["endTime"] = data[5].split(":")[0] # theres probably a better way to handle this 
                    if chart["general"]["mode"] == "1":
                        if hitobject["hitSound"] == 4 or hitobject["hitSound"] == 12 or (hitobject["hitSound"] == 2 or hitobject["hitSound"] == 8 and chart["general"]["katTap"] == true):
                            hitobject["tap"] = true
                        else:
                            hitobject["tap"] = false
                    else:
                        hitobject["tap"] = false
                if chart["general"]["mode"] == "1":
                    if hitobject["type"] & 0b00000010 == 0b10:
                        hitobject["endTime"] = float(data[7])
                    if hitobject["type"] & 0b00001000 == 0b1000:
                        hitobject["endTime"] = float(data[5])
                        hitobject["hitSample"] = data[6].split(":")[1:]
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
                    if ask.lower().strip() == "yes" or ask.lower().strip() == "y":
                        chart["general"]["katTap"] = true
                    else:
                        chart["general"]["katTap"] = false
                else:
                    chart["general"]["katTap"] = false
                if chart["general"]["mode"] == "0" or chart["general"]["mode"] == "2":
                    print("your beatmap's mode is unsupported, proceed with caution")

    print("finished extracting the beatmap")
    return chart