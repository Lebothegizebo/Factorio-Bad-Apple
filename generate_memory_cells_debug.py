import sys
import base64
import json
import zlib
import pyperclip # type: ignore
import cv2 # type: ignore
import os
import math
from configparser import ConfigParser
import numpy as np
from PIL import Image

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def rgb_to_hex(r, g, b):
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

def palette_to_hex_list(index):
    im = Image.open(R'Generated_Files\ffmpeg\palette.png')
    rgb_palette_data = []
    rgb_im = im.convert('RGB')
    for y in range(16):
        for x in range(16):
            rgb_palette_data.append(rgb_im.getpixel((x, y)))
    r = rgb_palette_data[index][0]
    g = rgb_palette_data[index][1]
    b = rgb_palette_data[index][2]
    return r, g, b

def hex_compare(hex_string):
    for hex_index in range(255):
        if hex_string == rgb_to_hex((palette_to_hex_list(hex_index)[0]),palette_to_hex_list(hex_index)[1],palette_to_hex_list(hex_index)[2]):
            print("HEX:", hex_string)
            return hex_index


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
hex_compare("#000000")
wire_copper = 1
wire_red = 2
wire_green = 3
signals = []
signals_type = []
signals_quality = []
bit_max = 32
if colour_mode == "256 bit": # type: ignore
    bit_size = 4 # 256 bit colour
elif colour_mode == "2 bit": # type: ignore
    bit_size = 32 # 2 bit colour
bit_step = round(bit_max/bit_size)
number_of_splits = int(math.ceil(video_height/bit_size)) # type: ignore # Number of Horizontal splits to split the video into to fit all binary signals
if number_of_splits <1:
    number_of_splits = 1
splits_height = round(video_height/number_of_splits) # type: ignore #Vertical Height of each split, used for generating video

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
    cap.set(cv2.CAP_PROP_POS_FRAMES, 100)#frame_number) 
    ret, frame = cap.read()
    if ret:
        #initilizes video processing enviroment
        frame = cv2.resize(frame, (video_width, video_height), interpolation=cv2.INTER_AREA) # type: ignore
        height, width, _ = frame.shape
        if colour_mode == "2 bit": # type: ignore #Black or White Colour
            raw_frame_data = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for row in raw_frame_data:
                l.append([0 if pixel < 128 else 1 for pixel in row])
                print(l)
                input()
                sys.exit("debug")

        else: # 256 colour from colour pallete
            raw_frame_data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pixels = raw_frame_data.reshape(-1, 3)
            pixel_hex_data = []
            for pixels_index in range(len(pixels)):
                print(pixels_index)
                pixel_hex_data.append(rgb_to_hex(pixels[0][0],pixels[0][1],pixels[0][2]))
            
            print(pixels)
            for row in raw_frame_data:
                l.append([hex_compare(pixel_hex_data[i]) for i in row ])
                # l_raw_color_data.append([pixel for pixel in row])
                # print(l_raw_color_data)

                # l.append([rgb_colour_data for pixel in row])
            print(l)
            input()
            sys.exit("debug")



        # Left in for debugging purposes, does nothing on its own (to see frame before processing is done)

        #DEBUG FRAME DATA
        # cv2.imshow("frame", frame)
        # cv2.imshow("converted frame", raw_frame_data)
        # cv2.waitKey(0)

        # DEBUG: SPLITS
        # split_pixel_count = 0
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
                    "quality": signals_quality[z][i]
                    },
                    "copy_count_from_input": False,
                    "constant": data
                    })
                else: 
                    factorio_signal_data.append({
                    "signal": {
                    "name": signals[z][i],
                    "quality": signals_quality[z][i]
                    },
                    "copy_count_from_input": False,
                    "constant": data
                    })
                k += 1 
        cv2.destroyAllWindows()
        return factorio_signal_data
    
def make_blueprint(blueprint, frame_count, max_combinators):
    cap = cv2.VideoCapture(R"Generated_Files\ffmpeg\out.mp4")
    entity_number = 1
    combinator_count = 1
    column_count = 1 # Keeps track of how many combinators in each chunk of column for POWER
    new_wire = False
    x = 0
    y = 0
    frame_number = 1
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
                                "constant": frame_number,
                                "comparator": "="
                            }
                        ]
                    }
                }
            })
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

            sys.stdout.write(
                f"\rFrame: {frame_number}/{frame_count} | Pos: (x={x}, y={y})"
            )
            sys.stdout.flush()
            # Iterating key vars
            frame_number += 1
            entity_number += 1
            combinator_count += 1
            x -= 1
            if combinator_count > max_combinators: # Checks if combinators in column greater than allowed max combinators per column
                combinator_count = 1
                column_count += 1
                x = 0
                y -= 2
                new_wire = True
            if column_count > substation_range: # type: ignore # Checks if a gap needs to be made to power combinators
                column_count = 1
                y -= 2

    cls()
    print("Encoding Data to a Factorio Blueprint String. This may take a while.")
    new_blueprint = json_to_blueprint(blueprint)
    pyperclip.copy(new_blueprint)
    cap.release()
    cls()
    print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) <2:
        print("Usage: generate_memory_cells.py <video_path>")
    else:
        blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
        json_path = R"Generated_Files\video_player\signals\signals.json"
        video_path = "test.gif"
        video_path = str(sys.argv[1])
        frame_count = 1
        #frame_count = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FRAME_COUNT))
        max_combinators = 200 if len(sys.argv) < 4 else int(sys.argv[3])
        try: 
            with open(json_path, 'r') as file:
                raw_signals = json.load(file)
        except:
            sys.exit("No signals have been defined! Run generate_signals.py to continue.")
        for z in range(number_of_splits):
            signals.append(raw_signals["signals"]["split-"+str(z)])
        for z in range(number_of_splits):
            signals_type.append(raw_signals["signals-type"]["split-"+str(z)])
        for z in range(number_of_splits):
            signals_quality.append(raw_signals["signals-quality"]["split-"+str(z)])
        # if colour_mode == "256 bit": # type: ignore
        #     cls()
        #     print("Generating ffmpeg pallette.png")
        #     os.system(R"ffmpeg -y -i "+video_path+R" -vf palettegen Generated_Files\ffmpeg\palette.png -hide_banner -loglevel error")
        # cls()
        # print("Generating ffmpeg encoded video (out.mp4)") 
        # print("This may take a while.")
        # os.system(R"ffmpeg -y -i "+video_path+R" -i Generated_Files\ffmpeg\palette.png -filter_complex 'paletteuse' Generated_Files\ffmpeg\out.mp4 -hide_banner -loglevel error")
        # cls()
        print("Generating Combinators. This may take a while.")
        make_blueprint(blueprint,frame_count,max_combinators)
