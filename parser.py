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
                if hitobject["type"] == 12:
                    # TODO: handle drum rolls
                    1 == 1
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
                    print("your beatmap's mode is unsupported, proceed with caution")

    print("finished extracting the beatmap")
    return chart