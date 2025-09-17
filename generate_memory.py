import sys
import base64
import json
import zlib
import pyperclip # type: ignore
import cv2 # type: ignore
import os
import math
from configparser import ConfigParser
from PIL import Image
import numpy as np

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_gif(gif_path,frame_num):
    im = Image.open(gif_path)
    im.seek(frame_num)
    rgb_im = im.convert('RGB')
    gif_frame_data = np.array(rgb_im)
    return gif_frame_data

def rgb_to_hex(r, g, b):
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

def hex_to_rgb(hex_string):
    hex_code = hex_string.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def palette_to_hex_list(): # turns palette.png into a indexed list of HEX values, used for encoding and decoding
    im = Image.open(R'Generated_Files/ffmpeg/palette.png')
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

def get_rbg_data(frame_data): # Returns RGB values from framedata
    r, g, b = frame_data
    hex = rgb_to_hex(r,g,b)
    return hex

def hex_compare(hex_string): # Returns a value from 0-255 for the colour data of each frame depending on pallete.png
    for hex_index in range(256):
        if hex_string == hex_list[hex_index]:
            return hex_index
    lowest_distance = math.sqrt(pow(255,2)+pow(255,2)+pow(255,2))
    r2, b2, g2 = hex_to_rgb(hex_string)
    lowest_distance_index = 0
    for i in range(256): # If inputted hex does not match, finds the closet matching colour and uses that instead
        r1, b1, g1 = hex_to_rgb(hex_list[i])
        compare_value = math.sqrt(pow(r2 - r1,2)+pow(b2 - b1,2)+pow(g2 - g1,2))
        if compare_value < lowest_distance:
            lowest_distance = compare_value
            lowest_distance_index = i
        if compare_value > lowest_distance:
            return lowest_distance_index
    return lowest_distance_index

def load_config(): # Loads all config
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
        globals()["chunk_size"] = config.getint("DEFAULT","chunk_size")
        globals()["combinator_width"]  = config.getint("DEFAULT","combinator_width")
        globals()["use_artifical_video_length"] = config.getboolean("DEFAULT", "use_artifical_video_length")
        globals()["frame_limit"] = config.getint("DEFAULT","frame_limit")

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
        globals()["chunk_size"] = config.getint("VIDEO_PLAYER","chunk_size")
        globals()["combinator_width"]  = config.getint("VIDEO_PLAYER","combinator_width")
        globals()["use_artifical_video_length"] = config.getboolean("VIDEO_PLAYER", "use_artifical_video_length")
        globals()["frame_limit"] = config.getint("VIDEO_PLAYER","frame_limit")

def blueprint_to_json(string): #Thx Doshdoshington
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data): #Thx Doshdoshington
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

def list_to_32bit_int(lst): #Thanks @artucuno for this function
    result = 0
    for bit in lst:
        result = (result << bit_step) | bit
    if result >= 0x80000000:  # If the sign bit is set
        result -= 0x100000000  # Convert to negative value
    return result

load_config()

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

def process(frame_number): # Thanks @artucuno for teaching me OpenCV2
    factorio_signal_data = []
    l = []
    if colour_mode == "2 bit": # type: ignore # Get Frame Data
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number) 
        ret, frame = cap.read()
        if ret:
            height, width, _ = frame.shape
            raw_frame_data = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for row in raw_frame_data:
                l.append([0 if pixel < 128 else 1 for pixel in row])
    else:
        raw_frame_data = read_gif(R"Generated_Files\ffmpeg\out.gif", frame_number)
        for row in raw_frame_data:
            l.append([hex_compare(get_rbg_data(pixel)) for pixel in row])
    
    #Turns framedata into a list
    split_pixel_count = 0
    for z in range(number_of_splits):
        globals()["split_framedata_"+str(z)] = l[split_pixel_count:(video_height*(z+1))//number_of_splits] # type: ignore
        split_pixel_count += splits_height

    # Split the lists vertically for each pixel column
    for z in range(number_of_splits):
        globals()["split_"+str(z)] = [[row[i] for row in (globals()["split_framedata_"+str(z)])] for i in range(video_width)] # type: ignore

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
    
def make_blueprint(frame_count, max_combinators):
    entity_number = 1
    combinator_count = 1
    column_count = 1 # Keeps track of how many combinators in each chunk of column for POWER
    new_wire = False
    x = 0
    y = 0
    frame_number = 0
    chunk_number = 1
    chunk_max = math.ceil(frame_count/chunk_size) # type: ignore
    chunk_track = 0
    base_blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
    blueprint = base_blueprint
    for j in range(frame_count): #Frame Number
        if chunk_track >= chunk_size: # type: ignore
            cls()
            print("Encoding Data to a Factorio Blueprint String. This may take a while.")
            new_blueprint = json_to_blueprint(blueprint)
            pyperclip.copy(new_blueprint)
            with open("blueprint.txt", "w+") as file:
                file.write(new_blueprint)
            cls()
            print("Chunk succesfulyl generated! Chunk Number:",chunk_number)
            print("Encoded Factorio Blueprint String has been copied to your clipboard!")
            print("Please paste this in Factorio, and then press Enter to continue.")
            blueprint = {"blueprint":{"entities":[], "wires":[], "item": "blueprint", "version":562949957353472} }
            chunk_number += 1
            chunk_track = 0
            input()
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
                            "constant": frame_number+1,
                            "comparator": "="
                        }
                    ]
                }
            }
        })
        factorio_signal_data = process(frame_number)
        blueprint["blueprint"]["entities"][chunk_track]["control_behavior"]["decider_conditions"]["outputs"] = factorio_signal_data
        chunk_track += 1
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
            f"\rFrame: {frame_number}/{frame_count} | Pos: (x={x}, y={y})| Chunk: {chunk_number}/{chunk_max}"
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
    with open("blueprint.txt", "w+") as file:
        file.write(new_blueprint)
    try:
        cap.release()
    except:
        pass
    cls()
    print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) <2:
        print("Usage: generate_memory.py <video_path>")
    else:
        json_path = R"Generated_Files/video_player/signals/signals.json"
        video_path = str(sys.argv[1])
        max_combinators = combinator_width # type: ignore
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
        if colour_mode == "256 bit": # type: ignore
            cls()
            print("Generating ffmpeg pallette.png")
            modulus = video_height % 4
            if modulus != 0:
                while modulus != 0:
                    video_height += 1
                    modulus = video_height % 4   
            os.system(R'ffmpeg -y -i '+video_path+R' -vf "scale='+str(video_width)+R':'+str(video_height)+R'" Generated_Files/ffmpeg/small.mp4 -hide_banner -loglevel error') # type: ignore
            os.system(R"ffmpeg -y -i Generated_Files/ffmpeg/small.mp4 -vf palettegen=reserve_transparent=0 Generated_Files/ffmpeg/palette.png -hide_banner -loglevel error")
            cls()
            print("Generating ffmpeg encoded video (out.mp4)") 
            print("This may take a while.")
            os.system(R"ffmpeg -y -i Generated_Files/ffmpeg/small.mp4 -i Generated_Files/ffmpeg/palette.png -filter_complex 'paletteuse' Generated_Files/ffmpeg/out.gif -hide_banner -loglevel error")
            os.system(R'ffmpeg -y -i Generated_Files/ffmpeg/out.gif -vf Generated_Files/ffmpeg/out.mp4 -hide_banner -loglevel error')
        else:
            os.system(R'ffmpeg -y -i '+video_path+R' -vf "scale='+str(video_width)+R':'+str(video_height)+R'" Generated_Files/ffmpeg/out.mp4 -hide_banner -loglevel error') # type: ignore
        cls()
        if use_artifical_video_length == True:
            frame_count = frame_limit
        else:
            frame_count = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FRAME_COUNT))
        if colour_mode == "2 bit": # type: ignore
            cap = cv2.VideoCapture(R"Generated_Files/ffmpeg/out.mp4")
        else: 
            hex_list = palette_to_hex_list()
        print("Generating Combinators. This may take a while.")
        make_blueprint(frame_count,max_combinators)
