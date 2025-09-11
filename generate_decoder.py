import sys
import base64
import json
import zlib
import pyperclip

video_width = 64
wire_red = 1
wire_green = 4
bit_max = 32
signals = []
decoder = []
colour_mode = "2 bit" # "256 bit", "2 bit"

if colour_mode == "256 bit":
    bit_size = 4 # 256 bit colour
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
    column_count = 1
    max_combinators_per_column_chunk = 13
    x = 0
    y = 0
    bit = 0
    bit_step = bit_max/bit_size
    and_constant = 1 if bit_size != 1 else (bit_max*bit_size)-1
    for i, key in enumerate(list(raw_signals["signals"].keys())):
        signals.extend(raw_signals["signals"][key])
    for i, key in enumerate(list(raw_signals["decoder"].keys())):
        decoder.extend(raw_signals["decoder"][key])
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
        for j in range(round(len(decoder))):
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                y += 2          
            column_count += 1
            if j < round(len(decoder)/splits):
                signal_id_offset = 0
                offset_needed=True
            if j >= round(len(decoder)/splits) and offset_needed:
                offset_needed=False
                signal_id_offset = round(len(signals)/splits)
            blueprint["blueprint"]["entities"].append({
                "entity_number": entity_number,
                "name": "arithmetic-combinator",
                "position": {"x": x, "y": y},
                "direction": 8,
                "control_behavior": {
                    "arithmetic_conditions": {
                                "first_signal": {
                                    "type": "virtual",
                                    "name": signals[(signal_id+signal_id_offset)]
                                },
                                "second_constant": bit,
                                "operation": ">>",
                                "output_signal": {
                                    "type": "virtual",
                                    "name": decoder[j]
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
        new_blueprint = json_to_blueprint(blueprint)
        pyperclip.copy(new_blueprint)
        print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: generate_decoder.py <json_path>  ")
    else:
        json_path = str((sys.argv[1]))

        with open(json_path, 'r') as file:
            raw_signals = json.load(file)
        splits = len(raw_signals["signals"])
        make_blueprint()
