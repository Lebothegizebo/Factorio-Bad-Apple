import sys
import base64
import json
import zlib
import pyperclip

wire_red = 2
wire_green = 2
bit_max = 32
decoder = []
decoder_type = []
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
    x = 0
    y = 0
    for i, key in enumerate(list(raw_signals["decoder"].keys())):
        decoder.extend(raw_signals["decoder"][key])
    for i, key in enumerate(list(raw_signals["decoder"].keys())):
        decoder_type.extend(raw_signals["decoder-type"][key])

    for i in range(len(decoder)):
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
                "name": decoder[i]
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
