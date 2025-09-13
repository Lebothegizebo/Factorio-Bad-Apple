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
wire_red = 1
wire_green = 4
bit_max = 32
signals = []
signals_type = []
signals_quality = []
decoder = []
decoder_type = []
decoder_quality = []
if colour_mode == "256 bit":
    bit_size = 4 # 256 bit colour
elif colour_mode == "2 bit":
    bit_size = 32 # 2 bit colour
number_of_splits = round(video_height/bit_size)# Number of Horizontal splits to split the video into to fit all binary signals
if number_of_splits <1:
    number_of_splits = 1


def blueprint_to_json(string):
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data):
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

def make_blueprint():
    blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
    entity_number=1
    column_count = 1
    max_combinators_per_column_chunk = substation_range
    x = 0
    y = 0
    bit = 0
    bit_step = round(bit_max/bit_size)
    print(bit_step)
    and_constant = 1 if bit_size != 1 else round((bit_max*bit_step)-1)
    for i, key in enumerate(list(raw_signals["signals"].keys())):
        signals.extend(raw_signals["signals"][key])
    for i, key in enumerate(list(raw_signals["signals-type"].keys())):
        signals_type.extend(raw_signals["signals-type"][key])
    for i, key in enumerate(list(raw_signals["signals-quality"].keys())):
        signals_quality.extend(raw_signals["signals-quality"][key])

    for i, key in enumerate(list(raw_signals["decoder"].keys())):
        decoder.extend(raw_signals["decoder"][key])
    for i, key in enumerate(list(raw_signals["decoder-type"].keys())):
        decoder_type.extend(raw_signals["decoder-type"][key])
    for i, key in enumerate(list(raw_signals["decoder-quality"].keys())):
        decoder_quality.extend(raw_signals["decoder-quality"][key])
    y_start = 0
    each_combinator_track = []
    entity_number_track_top = []
    entity_number_track_bottom = []
    x=0
    signal_id = 0
    for i in range(round(video_width)):
        entity_number_track_top.append(entity_number)
        y = y_start
        column_count = 1
        signal_id_offset = 0
        signal_id_offset_tracker = 0
        for j in range(round(len(decoder))):
            if signal_id_offset_tracker >= round(len(decoder)/splits):
                signal_id_offset += round(len(signals)/splits)
                signal_id_offset_tracker = 0
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                y += 2          
            column_count += 1
            if signals_type[(signal_id+signal_id_offset)] != None:
                if decoder_type[j] != None:
                    blueprint["blueprint"]["entities"].append({
                        "entity_number": entity_number,
                        "name": "arithmetic-combinator",
                        "position": {"x": x, "y": y},
                        "direction": 8,
                        "control_behavior": {
                            "arithmetic_conditions": {
                                        "first_signal": {
                                            "type" : signals_type[(signal_id+signal_id_offset)],
                                            "name": signals[(signal_id+signal_id_offset)],
                                            "quality": signals_quality[(signal_id+signal_id_offset)]
                                        },
                                        "second_constant": bit,
                                        "operation": ">>",
                                        "output_signal": {
                                            "type": decoder_type[j],
                                            "name": decoder[j],
                                            "quality": decoder_quality[j]
                                }
                            }
                        }
                    })
                else:
                    blueprint["blueprint"]["entities"].append({
                        "entity_number": entity_number,
                        "name": "arithmetic-combinator",
                        "position": {"x": x, "y": y},
                        "direction": 8,
                        "control_behavior": {
                            "arithmetic_conditions": {
                                        "first_signal": {
                                            "type" : signals_type[(signal_id+signal_id_offset)],
                                            "name": signals[(signal_id+signal_id_offset)],
                                            "quality": signals_quality[(signal_id+signal_id_offset)]
                                        },
                                        "second_constant": bit,
                                        "operation": ">>",
                                        "output_signal": {
                                            "name": decoder[j],
                                            "quality": decoder_quality[j]
                                }
                            }
                        }
                    })
            else:
                if decoder_type[j] != None:
                    blueprint["blueprint"]["entities"].append({
                        "entity_number": entity_number,
                        "name": "arithmetic-combinator",
                        "position": {"x": x, "y": y},
                        "direction": 8,
                        "control_behavior": {
                            "arithmetic_conditions": {
                                        "first_signal": {
                                            "name": signals[(signal_id+signal_id_offset)],
                                            "quality": signals_quality[(signal_id+signal_id_offset)]
                                        },
                                        "second_constant": bit,
                                        "operation": ">>",
                                        "output_signal": {
                                            "type": decoder_type[j],
                                            "name": decoder[j],
                                            "quality": decoder_quality[j]
                                }
                            }
                        }
                    })
                else:
                    blueprint["blueprint"]["entities"].append({
                        "entity_number": entity_number,
                        "name": "arithmetic-combinator",
                        "position": {"x": x, "y": y},
                        "direction": 8,
                        "control_behavior": {
                            "arithmetic_conditions": {
                                        "first_signal": {
                                            "name": signals[(signal_id+signal_id_offset)],
                                            "quality": signals_quality[(signal_id+signal_id_offset)]
                                        },
                                        "second_constant": bit,
                                        "operation": ">>",
                                        "output_signal": {
                                            "name": decoder[j],
                                            "quality": decoder_quality[j]
                                }
                            }
                        }
                    })
        

            blueprint["blueprint"]["wires"].append([
                entity_number,
                wire_green,
                entity_number+1,
                wire_green
            ])
            blueprint["blueprint"]["wires"].append([
                entity_number,
                wire_red,
                entity_number+1,
                wire_red
            ])
            entity_number += 1
            bit += bit_step
            if bit == bit_max:
                bit = 0
            y += 2
            signal_id_offset_tracker += 1 
         
        x += 1
        signal_id += 1
        entity_number_track_bottom.append(entity_number-1)
    y_start = len(decoder)
    x = 0
    y +=2
    x = 0
    for i in range(len(raw_signals["signals"]["split-0"])):
        blueprint["blueprint"]["entities"].append({
            "entity_number": entity_number,
            "name": "arithmetic-combinator",
            "position": {"x": x, "y": y},
            "direction": 8,
            "control_behavior": {
                "arithmetic_conditions": {
                            "first_signal": {
                                "type": "virtual",
                                "name": "signal-each"
                            },
                            "second_constant": and_constant,
                            "operation": "AND",
                            "output_signal": {
                                "type": "virtual",
                                "name": "signal-each"
                    }
                }
            }
        })
        each_combinator_track.append(entity_number)
        entity_number += 1
        x += 1
    for i in range(len(each_combinator_track)):
        blueprint["blueprint"]["wires"].append([
                    entity_number_track_bottom[i],
                    4,
                    each_combinator_track[i],
                    2,

        ])
    for i in range(len(raw_signals["signals"]["split-0"])-1):
        blueprint["blueprint"]["wires"].append([
            entity_number_track_top[i],
            wire_red,
            entity_number_track_top[i+1],
            wire_red
        ])
    else:
        # with open('debug.json', 'w+') as f:
        #     json.dump(blueprint, f, indent=4)
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
    splits = number_of_splits
    make_blueprint()
