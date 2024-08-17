import random
from globals import *

### convert into beatblock format
        
def convert(chart):
    """
    function to convert chart table to format beatblock can read\n
    """
    transitions = getTransitions(chart)
    add_angle = (random.randint(-180, 180) if chart["general"]["mode"] != "2" else 0)
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
            # beatvalue = val["time"] / section["beatLength"]
            beatvalue = convertMsToBeats(val["time"], transitions, chart)
            note["time"] = beatvalue
            angle = val["x"] / 128
            note["angle"] = (angle * angle_multiplier) + add_angle + (random.randint(-taiko_multiplier, taiko_multiplier) if val["tap"] else 0)
            note["tap"] = val["tap"]

        # holds (mania)
        if val["type"] == 128:
            note = {}
            note["type"] = "hold"
            # beatvalue = val["time"] / section["beatLength"]
            # note["time"] = beatvalue
            # beatvalue2 = (val["endTime"] / section["beatLength"]) - beatvalue
            # note["duration"] = beatvalue2
            beatvalue = convertMsToBeats(val["time"], transitions, chart)
            note["time"] = beatvalue
            beatvalue2 = abs(convertMsToBeats(val["endTime"], transitions, chart) - beatvalue)
            if beatvalue2 == 0:
                continue # prevent sliders at the end which pop up for some reason every now and then
            note["duration"] = beatvalue2
            angle = val["x"] / 128
            note["angle"] = (angle * angle_multiplier) + add_angle
            note["angle2"] = (angle * angle_multiplier) + add_angle

        # holds
        if val["type"] == 2:
            print("TODO add a list of ongoing holds, and make it change the end angle based on angle change ok")
            for i, p in enumerate(val["points"]):
                if len(val["points"]) <= i + 1:
                    break
                note = {}
                note["type"] = "hold"
                beatvalue = convertMsToBeats(float(p["y"]) + val["time"], transitions, chart)
                note["time"] = beatvalue
                beatvalue2 = abs(convertMsToBeats(float(val["points"][i+1]["y"]) + val["time"], transitions, chart) - beatvalue)
                note["duration"] = beatvalue2
                angle = (float(p["x"]) / 512) * 360
                note["angle"] = (angle * angle_multiplier) + add_angle
                angle = ((float(val["points"][i+1]["x"]) / 512) * 360)
                note["angle2"] = (angle * angle_multiplier) + add_angle
                bchart.append(note)
            note = None # we already manually added all of the notes during this iteration

        if note:
            bchart.append(note)
            rng_counter += 1
            if rng_counter >= 10:
                add_angle += random.randint(-45, 45)
                rng_counter = 0
            if chart["general"]["mode"] == "1":
                # add random offset to make taiko maps less boring
                add_angle += random.randint(-10, 10)
    return bchart
