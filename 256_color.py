import sys
import os
import base64
import json
import zlib
import pyperclip
import math
from configparser import ConfigParser
from PIL import Image

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

def hex_to_encoded_rgb(hex_string):
    hex_code = hex_string.lstrip('#')
    encoded_rgb = int(hex_code, 16)
    return encoded_rgb

def palette_to_hex_list(): # turns pallete.png into a indexed list of HEX vaules, used for encoding and decoding
    im = Image.open(R'Generated_Files\ffmpeg\palette.png')
    rgb_palette_data = []
    rgb_hex_list = []
    rgb_im = im.convert('RGB')
    for y in range(16):
        for x in range(16):
            rgb_palette_data.append(rgb_im.getpixel((x, y)))
    for index in range(256):
        r = rgb_palette_data[index][0]
        g = rgb_palette_data[index][1]
        b = rgb_palette_data[index][2]
        rgb_hex_list.append('#{0:02x}{1:02x}{2:02x}'.format(r, g, b))
    return rgb_hex_list

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
number_of_splits = int(math.ceil(video_height/bit_size))# Number of Horizontal splits to split the video into to fit all binary signals
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
    dynamic_bit_max = 32

    and_constant = 1 if bit_size == 32 else round((bit_max*bit_step)-1)
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
            if bit == dynamic_bit_max:
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
    y += 4
    x = 0
    color_decoder_track = []
    column_count = 1
    y_start  = y
    for i in range(len(raw_signals["signals"]["split-0"])):
        color_decoder_track.append(entity_number)
        column_count = 1
        for k in range(256):
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                y += 2          
            column_count += 1
            blueprint["blueprint"]["entities"].append({
                "entity_number": entity_number,
                "name": "decider-combinator",
                "position": {
                "x": x,
                "y": y
                },
                "direction": 8,
                "control_behavior": {
                    "decider_conditions": {
                        "conditions": [
                        {
                            "first_signal": {
                            "type": "virtual",
                            "name": "signal-each"
                            },
                            "constant": k,
                            "comparator": "="
                        }
                        ],
                        "outputs": [
                        {
                            "signal": {
                            "type": "virtual",
                            "name": "signal-each"
                            },
                            "copy_count_from_input": False,
                            "constant": hex_to_encoded_rgb(hex_list[k])
                        }
                        ]
                    }
                }
            }
            )
            blueprint["blueprint"]["wires"].append([
                entity_number,
                wire_green,
                entity_number+1,
                wire_green
            ])
            blueprint["blueprint"]["wires"].append([
                entity_number,
                2,
                entity_number+1,
                2
            ])
            entity_number += 1
            y += 2
        x +=1
        y = y_start
    for i in range(len(color_decoder_track)):
        blueprint["blueprint"]["wires"].append([
                    each_combinator_track[i],
                    4,
                    color_decoder_track[i],
                    2,
        ])
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
        new_blueprint = json_to_blueprint(blueprint)
        pyperclip.copy(new_blueprint)
        print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    json_path = R"Generated_Files\video_player\signals\signals.json"
    if len(sys.argv) <2:
        print("Usage: generate_memory_cells.py <video_path>")
    else:
        try: 
            with open(json_path, 'r') as file:
                raw_signals = json.load(file)
        except:
            sys.exit("No signals have been defined! Run generate_signals.py to continue.")
        video_path = str(sys.argv[1])
        os.system(R"ffmpeg -y -i "+video_path+R" -vf palettegen=reserve_transparent=0 Generated_Files\ffmpeg\palette.png -hide_banner -loglevel error")
        hex_list = palette_to_hex_list()
        splits = number_of_splits
        make_blueprint()
