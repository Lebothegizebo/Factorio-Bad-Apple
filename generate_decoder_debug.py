import sys
import base64
import json
import zlib
import pyperclip

wire_copper = 1
wire_red = 2
wire_green = 3
signals = {}

def blueprint_to_json(string):
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data):
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

def make_blueprint(signal_list, indexes):
    blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
    combinator_count = 1
    column_count = 1
    max_combinators_per_column_chunk =13
    signal_data = []
    new_wire = False
    x = 0
    y = 0
    bitshift = 0
    and_compare = 15

    for i in range(indexes)-1:
        blueprint["blueprint"]["entities"].append({
            "entity_number": entity_number,
            "name": "arithmetic-combinator",
            "position": {"x": x, "y": y},
            "direction": 12,
            "control_behavior": {
                "decider_conditions": {
                    "conditions": [
                        {
                            "first_signal": {
                                "type": "virtual",
                                "name": "signal-F"
                            },
                            "constant": entity_number,
                            "comparator": "="
                        }
                    ]
                }
            }
        })
        signal_data = []
        signal_data = process(cap, frame_number)
        blueprint["blueprint"]["entities"][j]["control_behavior"]["decider_conditions"]["outputs"] = signal_data
        if entity_number != 1:
            blueprint["blueprint"]["wires"].append([
                entity_number-1,
                wire_red,
                entity_number,
                wire_red
            ])
            blueprint["blueprint"]["wires"].append([
                entity_number-1,
                wire_green,
                entity_number,
                wire_green
            ])
        if new_wire == True:
            new_wire = False
            blueprint["blueprint"]["wires"].append([
                entity_number-1,
                wire_red,
                entity_number,
                wire_red
            ])
            blueprint["blueprint"]["wires"].append([
                entity_number-1,
                wire_green,
                entity_number,
                wire_green
            ])
            # Iterating key vars
            entity_number += 1
            combinator_count += 1
            x -= 1
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                y -= 2


    for i, entity in enumerate(blueprint['blueprint']['entities']):
        if entity['name'] == "arithmetic-combinator":
            if "first_signal" not in entity['control_behavior']['arithmetic_conditions']:
                if top_or_bottom == "bottom":
                    k=k-1
                else:
                    k=k+1
                if len(signal_list["signals"]["decoder"]) > k:
                    if signal_list["signals"]["decoder"][k] == 0:

                        entity['control_behavior']['arithmetic_conditions']['first_signal'] = {
                            "constant": 0
                        }
                        entity['control_behavior']['arithmetic_conditions']['output_signal'] = {
                            "constant": 0
                    }
                    else:  
                        entity['control_behavior']['arithmetic_conditions']['first_signal'] = {
                            "type": "virtual",
                            "name": signal_list["signals"][top_or_bottom][index]
                        }
                        entity['control_behavior']['arithmetic_conditions']['output_signal'] = {
                        "type": "virtual",
                        "name": signal_list["signals"]["decoder"][k]
                        }
                    j=j+1
            else:
                j=j+1
    else:
        new_blueprint = json_to_blueprint(blueprint)
        pyperclip.copy(new_blueprint)
        print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: generate_decoder.py <json_path> <index> <top_or_bottom>?  ")
    else:
        json_path = str((sys.argv[1]))
        index = int(sys.argv[2])
        top_or_bottom = (sys.argv[3])

        with open(json_path, 'r') as file:
            signal_list = json.load(file)

        make_blueprint(signal_list,top_or_bottom)
