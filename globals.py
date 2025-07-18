import json
import os

true = True
false = False

config = None
if not os.path.isfile("config.json"):
    print("couldnt find config.json, make sure to rename \"example_config.json\" to just \"config.json\".")
    exit()
else:
    with open("config.json", "r") as f:
        try:
            config = json.loads(f.read())
        except:
            print("couldnt load config.json. using defaults")
            config = {
                "add_angle_min": -180, 
                "add_angle_max": 180, 
                "angle_multiplier": 2, 
                "taiko_multiplier": 10, 
                "switch_position_every_min": 5, 
                "switch_position_every_max": 15,
                "switch_slider_once_every": 5,
                "jump_distance_min": -45,
                "jump_distance_max": 45
            }

def getSection(time, chart):
    b = chart["timing"][0]
    for i in chart["timing"]:
        if i["time"] <= time and i["time"] >= b["time"]:
            b = i
    return b

def convertMsToBeats(ms, transitions, chart, endTime=None, end=false):
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
        if end:
            if c >= len(transitions) - 1:
                # im going insanse
                try:
                    t2 = chart["hitobjects"][-1]["endTime"]
                    if chart["hitobjects"][-1]["endTime"] > ms:
                        t2 = ms
                except Exception as e:
                    t2 = chart["hitobjects"][-1]["time"]
                    if chart["hitobjects"][-1]["time"] > ms:
                        t2 = ms
        else:
            t2 = chart["hitobjects"][-1]["time"]
            if chart["hitobjects"][-1]["time"] > ms:
                t2 = ms


        # use provided endtime as a timing
        if endTime != None:
            t2 = endTime
        
        if t2 != -1:
            time = abs(transitions[c]["time"] - t2)
            beats = time / transitions[c]["beatLength"]
            total_beats += beats
        if reached_end == true:
            break

    return abs(total_beats)

def getTransitions(chart):
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
    return transitions