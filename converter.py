import random
from globals import *

### convert into beatblock format
        
def convert(chart):
    """
    function to convert chart table to format beatblock can read\n
    """
    transitions = getTransitions(chart)
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
                # add random offset to make taiko maps less boring
                add_angle += random.randint(-10, 10)
    return bchart
