import sys
import base64
import json
import zlib
import pyperclip

wire_red = 1
wire_green = 4
bit_max = 32
signals = []
decoder = []
colour_mode = "2 bit" # "256 bit", "2 bit"

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
    entity_number_track_bottom=[]
    entity_number_track_top=[]
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
    signal_id=-1
    y_start = 0

    for z in range(splits):
        x=0
        for i in range(len(raw_signals["signals"]["split-0"])):
            y = y_start
            column_count = 1
            entity_number_track_top.append(entity_number)
            for j in range(len(raw_signals["decoder"]["split-0"])):
                if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                    column_count = 1
                    y += 2          
                column_count += 1
                print("Sgnals: ", str(i)+": ",raw_signals["signals"]["split-"+str(z)][i])
                print("Decoder: ", str(j)+": ",raw_signals["decoder"]["split-"+str(z)][j])
                blueprint["blueprint"]["entities"].append({
                    "entity_number": entity_number,
                    "name": "arithmetic-combinator",
                    "position": {"x": x, "y": y},
                    "direction": 8,
                    "control_behavior": {
                        "arithmetic_conditions": {
                                    "first_signal": {
                                        "type": "virtual",
                                        "name": raw_signals["signals"]["split-"+str(z)][i]
                                    },
                                    "second_constant": bit,
                                    "operation": ">>",
                                    "output_signal": {
                                        "type": "virtual",
                                        "name": raw_signals["decoder"]["split-"+str(z)][j]
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
                if bit == 24:
                    bit = 0
                y += 2
            entity_number_track_bottom.append(entity_number)
            x+=1
        print("before:", y_start)
    x=0
    y +=2
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
        blueprint["blueprint"]["wires"].append([
                entity_number_track_bottom[i]-1,
                wire_green,
                entity_number,
                2
            ])
        entity_number += 1
        x += 1
    for i in range(len(decoder)-1):
        blueprint["blueprint"]["wires"].append([
            entity_number_track_top[i],
            wire_red,
            entity_number_track_top[i+1],
            wire_red
        ])
    else:
        with open('debug.json', 'w+') as f:
            json.dump(blueprint, f, indent=4)
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
