import random
from globals import *

### convert into beatblock format
        
def convert(chart):
    """
    function to convert chart table to format beatblock can read\n
    """
    transitions = getTransitions(chart)
    add_angle = (random.randint(-180, 180) if chart["general"]["mode"] != "2" else 0)
    angle_multiplier = config["angle_multiplier"]
    taiko_multiplier = config["taiko_multiplier"] # slightly random position of taiko big notes
    rng_counter = -random.randint(config["switch_position_every_min"], config["switch_position_every_max"])
    ongoingholds = []
    bchart = []
    for i, val in enumerate(chart["hitobjects"]):
        note = None
        # blocks
        if val["type"] & 0b1 == 0b1:
            # calculate approximate location (likely inaccurate if bpm changes)
            beatvalue = convertMsToBeats(val["time"], transitions, chart)
            angle = (val["x"] / 128) * angle_multiplier + add_angle 
            note = {
                "type": "block",
                "time": beatvalue,
                "angle": angle + (random.randint(-taiko_multiplier, taiko_multiplier) if val["tap"] else 0),
                "tap": val["tap"],
                "spinner": false # please dont do this
            }

        # holds and spinners (theyre the same)
        if val["type"] & 0b10000000 == 0b10000000 or val["type"] & 0b00000010 == 0b10 or val["type"] & 0b00001000 == 0b1000:
            beatvalue = convertMsToBeats(val["time"], transitions, chart)   
            beatvalue2 = abs(convertMsToBeats(val["endTime"], transitions, chart) - beatvalue)
            if beatvalue2 == 0:
                # try harder
                beatvalue2 = abs(convertMsToBeats(val["endTime"], transitions, chart, val["endTime"] + 10) - beatvalue)
            angle = val["x"] / 128
            note = {
                "type": "hold",
                "time": beatvalue,
                "duration": beatvalue2,
                "angle": (angle * angle_multiplier) + add_angle,
                "angle2": (angle * angle_multiplier) + add_angle,
                "segments": 1,
                "x": val["x"],
                "spinner": val["type"] & 0b00001000 == 0b1000,
                "debug": "yes"
            }
            if note["duration"] == 0:
                note["type"] = "block" # thats it (hopefully)
            if note["spinner"] == false:
                ongoingholds.append(note)

        if note:
            if note["type"] != "hold":
                bchart.append(note)
                rng_counter += 1
                if rng_counter >= 0:
                    add_angle += random.randint(config["jump_distance_min"], config["jump_distance_max"])
                    rng_counter = -random.randint(config["switch_position_every_min"], config["switch_position_every_max"]) # we do a bit of trolling
                if chart["general"]["mode"] == "1":
                    # add random offset to make taiko maps less boring
                    add_angle += random.randint(-10, 10)

            if note["spinner"] == true:
                bchart.append(note) 

            for i in ongoingholds:
                if i["time"] + i["duration"] <= note["time"]:
                    i["angle2"] = ((i["x"] / 128) * angle_multiplier) + add_angle 
                    if i["angle"] != ((i["x"] / 128) * angle_multiplier) + add_angle:
                        i["segments"] = 30 # idk what the default is
                    bchart.append(i) 
                    try:
                        ongoingholds.remove(i)
                    except:
                        pass
                if random.randint(1, config["switch_slider_once_every"]) == 1:
                    add_angle += random.randint(config["jump_distance_min"], config["jump_distance_max"])
                    rng_counter = -random.randint(config["switch_position_every_min"], config["switch_position_every_max"]) 

    return bchart
