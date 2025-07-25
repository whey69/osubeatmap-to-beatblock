import json
import os
from globals import *

### write it to a file 

def write(bchart, chart):
    """
    write chart into two json files in the output directory\n
    """
    transitions = getTransitions(chart)

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
            event["time"] = convertMsToBeats(i["time"], transitions, chart)
            event["angle"] = 90
            event["bpm"] = i["bpm"]
            level["events"].append(event)

        # block approach speed changes
        for c, i in enumerate(chart["approaches"]):
            event = {}
            event["type"] = "ease"
            event["time"] = convertMsToBeats(i["time"], transitions, chart)
            event["angle"] = 270
            event["value"] = i["multiplier"]
            event["var"] = "scrollSpeed"
            level["events"].append(event)
        
        # end the level
        try:
            time = convertMsToBeats(chart["hitobjects"][-1]["time"] + chart["hitobjects"][-1]["endTime"], transitions, chart, end=true) + 1
        except Exception as e:
            time = convertMsToBeats(chart["hitobjects"][-1]["time"], transitions, chart) + 1
        event = {
            "time": time,
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
            if ".mp3" in event["file"]:
                print("warning: used audio file is very likely to be rejected by the game")
                inp = input("set the audio file extension to .ogg? youll have to convert the audio manually (y/N): ")
                if inp.strip() == "y" or inp.strip() == "yes":
                    event["file"] = event["file"].replace(".mp3", ".ogg")
            level["events"].append(event)
        except KeyError as e:
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
            "description": "Converted using osubeatmap-to-beatblock",
            "charter": chart["metadata"]["creator"],
            "artistLink": "",
            "artist": chart["metadata"]["artist"],
            "difficulty": 0 
        }

        file.write(json.dumps(level))