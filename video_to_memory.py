import sys
import base64
import json
import zlib
import pyperclip
import cv2

wire_cooper = 1
wire_red = 2
wire_green = 3
signals = {}


def blueprint_to_json(string): #Thx Doshdoshington
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data): #Thx Doshdoshington
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

# Convert into signed 32 bit integers adding 8 trailing zeros
def list_to_32bit_int(lst): #Thanks @artucuno for this function
    result = 0
    for bit in lst:
        result = (result << 1) | bit
    result = result << 8  # Add 8 trailing zeros
    if result >= 0x80000000:  # If the sign bit is set
        result -= 0x100000000  # Convert to negative value
    return result

def process(cap, frame_number): # Thanks @artucuno for teaching me OpenCV2 and contributing code
    signal_data = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB (256 bit)
        frame = cv2.resize(frame, (64, 48), interpolation=cv2.INTER_AREA)
        # split frame into 2 on the horizontal axis
        height, width, _ = frame.shape
        top_half = frame[0:height//2, 0:width]
        bottom_half = frame[height//2:height, 0:width]
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        l = []
        for row in gray_frame:
            l.append([0 if pixel < 128 else 1 for pixel in row])
            # l.append([pixel for pixel in row])

        # Split the list into two 2 halves
        top_half = l[0:height//2]
        bottom_half = l[height//2:height]

        # Split the lists vertically for each pixel column
        top_half_split = [[row[i] for row in top_half] for i in range(width)]
        bottom_half_split = [[row[i] for row in bottom_half] for i in range(width)]
        
        # Flip both lists
        top_half_split = [list(reversed(row)) for row in top_half_split]
        bottom_half_split = [list(reversed(row)) for row in bottom_half_split]
        index = 0


        length = len(top_half_split)
        k = 0
        for i, lst in enumerate(top_half_split):
            k = i+1
            data = list_to_32bit_int(lst)
            signal_data.append({
            "signal": {
            "type": "virtual",
            "name": signals["combined"][k-1],
            },
            "copy_count_from_input": False,
            "constant": data
            })
        for i, lst in enumerate(bottom_half_split):

            data = list_to_32bit_int(lst)
            signal_data.append({
            "signal": {
            "type": "virtual",
            "name": signals["combined"][k+i],
            },
            "copy_count_from_input": False,
            "constant": data
            })
        return signal_data
    
         




def make_blueprint(blueprint, signals, video_path, frame_count, max_combinators):
    cap = cv2.VideoCapture(video_path)
    entity_number = 1
    combinator_count = 1
    column_count = 1 # Keeps track of how many combinators in each chunk of column for POWER
    max_combinators_per_column_chunk = 4
    signal_data = []
    new_wire = False
    x = 0
    y = 0
    frame_number = 0
    for j in range(frame_count): #Frame Number
            blueprint["blueprint"]["entities"].append({
                "entity_number": entity_number,
                "name": "decider-combinator",
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
            frame_number += 1
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
                    entity_number-max_combinators,
                    wire_red,
                    entity_number,
                    wire_red
                ])
                blueprint["blueprint"]["wires"].append([
                    entity_number-max_combinators,
                    wire_green,
                    entity_number,
                    wire_green
                ])


            # Iterating key varibles
            entity_number += 1
            combinator_count += 1
            y += 1
            if combinator_count > max_combinators: # Checks if combinators in column greater than allowed max combinators per column
                combinator_count = 1
                column_count += 1
                x += 2
                y = 0
                new_wire = True
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                x += 2



    new_blueprint = json_to_blueprint(blueprint)
    pyperclip.copy(new_blueprint)
    cap.release()
    print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) <3:
        print("Usage: generate_memory_cells.py <json_path> <video_path> <max_combinators_per_column>?")
    else:
        blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
        json_path = str(sys.argv[1])

        #video_path = "bad-apple.mp4"
        #frame_count = int(sys.argv[2])
        video_data_path = str(sys.argv[2])
        frame_count = int(cv2.VideoCapture(video_data_path).get(cv2.CAP_PROP_FRAME_COUNT))
        
        max_combinators = 206 if len(sys.argv) < 4 else int(sys.argv[3])
        with open(json_path, 'r') as file:
            raw_signals = json.load(file)
        signals["combined"] = raw_signals["signals"]["top"] + raw_signals["signals"]["bottom"]

        make_blueprint(blueprint,signals,video_data_path,frame_count,max_combinators)
