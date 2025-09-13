import sys
import base64
import json
import zlib
import pyperclip
from configparser import ConfigParser

def load_config():
    config = ConfigParser()
    config.read("config.ini")
    if config.getboolean("VIDEO_PLAYER","use_default_settings") == True: #Load Default Settings
        globals()["use_vanilla_signals"] = config.getboolean("DEFAULT","use_vanilla_signals")
        globals()["use_custom_signals"] = config.getboolean("DEFAULT","use_custom_signals")
        globals()["use_space_age"] = config.getboolean("DEFAULT","use_space_age")
        globals()["use_quality"] = config.getboolean("DEFAULT","use_quality")
        globals()["bypass_custom_signal_warning"] = config.getboolean("DEFAULT","bypass_custom_signal_warning")
        globals()["bypass_custom_and_vanilla_signal_warning"] = config.getboolean("DEFAULT","bypass_custom_and_vanilla_signal_warning")
        globals()["custom_signal_json_path"] = config["DEFAULT"]["custom_signal_json_path"]
        globals()["colour_mode"] = config.read_string("DEFAULT","colour_mode")
        globals()["video_height"] = config.getint("DEFAULT", "video_height")
        globals()["video_width"] = config.getint("DEFAULT", "video_width")
        globals()["use_data_cache"] = config.getboolean("DEFAULT","use_data_cache")
        globals()["substation_range"]  = config.getint("DEFAULT","substation_range")
    else: #Load Custom Settings
        globals()["use_vanilla_signals"] = config.getboolean("VIDEO_PLAYER","use_vanilla_signals")
        globals()["use_custom_signals"] = config.getboolean("VIDEO_PLAYER","use_custom_signals")
        globals()["use_space_age"] = config.getboolean("VIDEO_PLAYER","use_space_age")
        globals()["use_quality"] = config.getboolean("VIDEO_PLAYER","use_quality")
        globals()["bypass_custom_signal_warning"] = config.getboolean("VIDEO_PLAYER","bypass_custom_signal_warning")
        globals()["bypass_custom_and_vanilla_signal_warning"] = config.getboolean("VIDEO_PLAYER","bypass_custom_and_vanilla_signal_warning")
        globals()["custom_signal_json_path"] = config["VIDEO_PLAYER"]["custom_signal_json_path"]
        globals()["colour_mode"] = config["VIDEO_PLAYER"]["colour_mode"]
        globals()["video_height"] = config.getint("VIDEO_PLAYER", "video_height")
        globals()["video_width"] = config.getint("VIDEO_PLAYER", "video_width")
        globals()["use_data_cache"] = config.getboolean("VIDEO_PLAYER","use_data_cache")
        globals()["substation_range"]  = config.getint("VIDEO_PLAYER","substation_range")

load_config()
wire_red = 2
wire_green = 2
bit_max = 32
decoder = []
decoder_type = []
decoder_quality = []

if colour_mode == "256 bit":
    bit_size = 8 # 256 bit colour
elif colour_mode == "2 bit":
    bit_size = 32 # 2 bit colour

def blueprint_to_json(string):
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data):
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

def make_blueprint():
    blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
    entity_number=1
    x = 0
    y = 0
    for i, key in enumerate(list(raw_signals["decoder"].keys())):
        decoder.extend(raw_signals["decoder"][key])
    for i, key in enumerate(list(raw_signals["decoder-type"].keys())):
        decoder_type.extend(raw_signals["decoder-type"][key])
    for i, key in enumerate(list(raw_signals["decoder-quality"].keys())):
        decoder_quality.extend(raw_signals["decoder-quality"][key])
    for i in range(len(decoder)):
        if decoder_type[i] != None: 
            blueprint["blueprint"]["entities"].append({
                "entity_number": entity_number,
                "name": "small-lamp",
                "position": {
                "x": x,
                "y": y
                },
                "control_behavior": {
                "use_colors": True,
                "rgb_signal": {
                    "type": decoder_type[i],
                    "name": decoder[i],
                    "quality": decoder_quality[i]
                },
                "color_mode": 2
                },
                "color": {
                "r": 1,
                "g": 1,
                "b": 1,
                "a": 1
                },
                "always_on": True
            })
        else:
            blueprint["blueprint"]["entities"].append({
            "entity_number": entity_number,
            "name": "small-lamp",
            "position": {
            "x": x,
            "y": y
            },
            "control_behavior": {
            "use_colors": True,
            "rgb_signal": {
                "name": decoder[i],
                "quality": decoder_quality[i]
            },
            "color_mode": 2
            },
            "color": {
            "r": 1,
            "g": 1,
            "b": 1,
            "a": 1
            },
            "always_on": True
            })
        blueprint["blueprint"]["wires"].append([
            entity_number,
            wire_green,
            entity_number+1,
            wire_green
        ])
        entity_number += 1
        y += 1
    else:
        new_blueprint = json_to_blueprint(blueprint)
        pyperclip.copy(new_blueprint)
        print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    json_path = R"Generated_Files\video_player\signals\signals.json"
    try: 
        with open(json_path, 'r') as file:
            raw_signals = json.load(file)
    except:
        sys.exit("No signals have been defined! Run generate_signals.py to continue.")
    splits = len(raw_signals["signals"])
    make_blueprint()
