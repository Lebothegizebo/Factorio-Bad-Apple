import sys
import base64
import json
import zlib
import pyperclip
import cv2

wire_copper = 1
wire_red = 2
wire_green = 3
signals = []
signals_type = []

colour_mode = "2 bit" # "256 bit", "2 bit"
video_height = 96 # Needs to be a divisor of 8 in 256 bit colour mode, or 32 in 2 bit colour mode
video_width = 128 # Can be any width, but generally keep to video ratios
bit_max = 32

if colour_mode == "256 bit":
    bit_size = 4 # 256 bit colour
elif colour_mode == "2 bit":
    bit_size = 32 # 2 bit colour

bit_step = round(bit_max/bit_size)
print("Bit Step: ", bit_step)
number_of_splits = round(video_height/bit_size)# Number of Horizontal splits to split the video into to fit all binary signals
if number_of_splits <1:
    number_of_splits = 1

splits_height = round(video_height/number_of_splits) #Vertical Height of each split, used for generating video


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
        result = (result << bit_step) | bit
    if result >= 0x80000000:  # If the sign bit is set
        result -= 0x100000000  # Convert to negative value
    return result

def process(cap, frame_number): #Processes video for each frame, where
    # Thanks @artucuno for teaching me OpenCV2

    factorio_signal_data = [] # Represents all the data created by this function and returns it as a list of signals with vaules
    l = [] # List of pixel data for each frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number) 
    ret, frame = cap.read()
    if ret:
        #initilizes video processing enviroment
        frame = cv2.resize(frame, (video_width, video_height), interpolation=cv2.INTER_AREA)
        height, width, _ = frame.shape

        #converts video into a greyscale frame
        raw_frame_data = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #converts greyscale frame into a list
        for row in raw_frame_data:
            l.append([0 if pixel < 100 else 1 for pixel in row])

        # Left in for debugging purposes, does nothing on its own (to see frame before processing is done)

        # split_pixel_count = 0
        # cv2.imshow("frame", frame)

        # for z in range(number_of_splits):
        #     globals()["split_framedata_"+str(z)] = frame[split_pixel_count:(height*(z+1))//number_of_splits, 0:width] #Frame Data
        #     split_pixel_count += splits_height
        # for z in range(number_of_splits):
        #     cv2.imshow("split-"+str(z)+":", globals()["split_framedata_"+str(z)])
        #     cv2.waitKey(0)
        
        #Turns framedata into a list
        split_pixel_count = 0
        for z in range(number_of_splits):
            globals()["split_framedata_"+str(z)] = l[split_pixel_count:(height*(z+1))//number_of_splits]
            split_pixel_count += splits_height

        
        # Split the lists vertically for each pixel column
        for z in range(number_of_splits):
            globals()["split_"+str(z)] = [[row[i] for row in (globals()["split_framedata_"+str(z)])] for i in range(width)]

        # Flip all video lists
        for z in range(number_of_splits):
            globals()["split_"+str(z)] = [list(reversed(row)) for row in globals()["split_"+str(z)]]

        #cv2.waitKey(0)
        cv2.destroyAllWindows()
        


        #Enumerate through video data (the lists) and assigns each list a 32 bit number and assigns that to a Factorio Signal
        k = 0
        for z in range(number_of_splits):
            for i, lst in enumerate(globals()["split_"+str(z)]):
                data = list_to_32bit_int(lst)
                if signals_type[z][i] != None:
                    factorio_signal_data.append({
                    "signal": {
                    "type": signals_type[z][i],
                    "name": signals[z][i],
                    },
                    "copy_count_from_input": False,
                    "constant": data
                    })
                else: 
                    factorio_signal_data.append({
                    "signal": {
                    "name": signals[z][i],
                    },
                    "copy_count_from_input": False,
                    "constant": data
                    })
                k += 1 
        return factorio_signal_data
    
def make_blueprint(blueprint, video_path, frame_count, max_combinators):
    cap = cv2.VideoCapture(video_path)
    entity_number = 1
    combinator_count = 1
    column_count = 1 # Keeps track of how many combinators in each chunk of column for POWER
    max_combinators_per_column_chunk =13
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
                "direction": 8,
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
            factorio_signal_data = process(cap, frame_number)
            blueprint["blueprint"]["entities"][j]["control_behavior"]["decider_conditions"]["outputs"] = factorio_signal_data
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


            # Iterating key vars
            entity_number += 1
            combinator_count += 1
            x -= 1
            if combinator_count > max_combinators: # Checks if combinators in column greater than allowed max combinators per column
                combinator_count = 1
                column_count += 1
                x = 0
                y -= 2
                new_wire = True
            if column_count > max_combinators_per_column_chunk: # Checks if a gap needs to be made to power combinators
                column_count = 1
                y -= 2



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
        video_data_path = str(sys.argv[2])
        frame_count = 100
        frame_count = int(cv2.VideoCapture(video_data_path).get(cv2.CAP_PROP_FRAME_COUNT))-2
        max_combinators = 225 if len(sys.argv) < 4 else int(sys.argv[3])
        with open(json_path, 'r') as file:
            raw_signals = json.load(file)
        for z in range(number_of_splits):
            signals.append(raw_signals["signals"]["split-"+str(z)])
        for z in range(number_of_splits):
            signals_type.append(raw_signals["signals-type"]["split-"+str(z)])
        make_blueprint(blueprint,video_data_path,frame_count,max_combinators)
