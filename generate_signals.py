import sys
import json
import os
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

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

load_config()

generated_signals = {"decoder": {}, "decoder-type": {}, "decoder-quality": {}, "signals": {}, "signals-type": {}, "signals-quality": {}} #Signal list that the program uses to generate memory and the decoder

if colour_mode == "256 bit":
    bit_size = 4 # 256 bit colour
elif colour_mode == "2 bit":
    bit_size = 32 # 2 bit colour

number_of_splits = round(video_height/bit_size)# Number of Horizontal splits to split the video into to fit all binary signals
if number_of_splits <1:
    number_of_splits = 1

splits_height = round(video_height/number_of_splits) #Vertical Height of each split, used for generating signals

def generate_signal_lists_and_type():
    signals = []
    signals_type = []
    signals_quality = []
    if globals()["use_quality"] == True:
        quality_list = [{"normal"},{"uncommon"},{"rare"},{"epic"},{"legendary"}]
    else:
        quality_list = [{"normal"}]
    if globals()["use_vanilla_signals"] == False and globals()["use_custom_signals"] == False:
        sys.exit("ERROR: No signals have been defined, please either allow use of custom signals or the included factorio signals in config.ini")
    if globals()["use_custom_signals"]: #Warning about Custom Signals.
            if globals()["bypass_custom_signal_warning"] == False: 
                cls()
                print("The video player is now using signals that are user defined, including modded signals.")
                print("Ensure all modded signals have the correct mod enabled, or else Factorio will throw an error if the required mods are not enabled. Continue at your own risk.")
                print("\n")
                print("This warning can be bypassed using config (bypass_custom_signal_warning)")
                print("To continue, press Enter.")
                input()
                cls()
                with open(custom_signal_json_path, 'r') as file:
                    raw_custom_signal_list = json.load(file)

    if globals()["use_custom_signals"] and globals()["use_vanilla_signals"]: #TEMPORARY, disables vanilla signals if custom signals are being used since the checks that duplicate signals are not being used have not been implemented yet.
        if globals()["bypass_custom_and_vanilla_signal_warning"] == False: 
            cls()
            print("Disabling use of included Vanilla signals, since custom signals are being used and the checks to make sure duplicate signals are not being used have not been implemented yet.")
            print("You will need to manually add all the signals the program can use, including vanilla signals, at least untill this program gets updated to do duplicate signal checks.")
            print("If this warning is bypassed, Custom signals will be used with the included Vanilla Signals.)")
            print("USE ONLY MODDED SIGNALS IF YOU BYPASS THIS WARNING")
            print("\n")
            print("This warning can be bypassed using config (bypass_custom_and_vanilla_signal_warning)")
            print("To continue, press Enter.")
            input()
            cls()
            globals()["use_vanilla_signals"] = False # Disables Vanilla Signals (For now, will make checks that duplicate signals are not used.)

    if globals()["use_vanilla_signals"]: #Customisation to enable automatic use of Vanilla Signals
        if globals()["use_space_age"]:
            print("INFO: Using Signals from Space Age DLC.")
            print("INFO: The video player now requires Space Age DLC.")
            globals()["vanilla_json_path"] = R"Factorio Signals\space_age.json"
        else:
            print("INFO: Using Basegame Factorio Signals.")
            print("INFO: Set use_space_age to True to use Space Age DLC")
            globals()["vanilla_json_path"] = R"Factorio Signals\basegame_factorio.json"
        with open(globals()["vanilla_json_path"], 'r') as file:
            raw_signal_list = json.load(file)

    if globals()["use_custom_signals"]: #Customisation to enable automatic use of Custom/Modded Signals (FOR ADVANCED USERS ONLY)
        print("INFO: Using User Defined Custom Signals.")
        with open(globals()["custom_signal_json_path"], 'r') as file:
            raw_custom_signal_list = json.load(file)

    #Generate Raw Signal Lists
    if globals()["use_vanilla_signals"]: #Included Signals
        for quality_index in range(len(quality_list)):
            for i in range(len(raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"])):
                signals.extend([raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["name"]])
                signals_quality.extend(quality_list[quality_index])
                try:
                    signals_type.extend([raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["type"]])
                except:   
                    signals_type.extend([None])

    if globals()["use_custom_signals"] == True: #Custom Signals
        for quality_index in range(len(quality_list)):
            for i in range(len(raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"])):
                signals.extend([raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["name"]])
                signals_quality.extend(quality_list[quality_index])
                try:
                    signals_type.extend([raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["type"]])
                except:   
                    signals_type.extend([None])

    return signals, signals_type, signals_quality

def factorio_signals_as_json():
    k = 0
    for z in range(number_of_splits):
        globals()["generated_signals"]["decoder"]["split-"+str(z)] = []
        globals()["generated_signals"]["decoder-type"]["split-"+str(z)] = []
        globals()["generated_signals"]["decoder-quality"]["split-"+str(z)] = []
        for i in range(splits_height):
            globals()["generated_signals"]["decoder"]["split-"+str(z)].append(signal[k])
            globals()["generated_signals"]["decoder-type"]["split-"+str(z)].append(signal_type[k])
            globals()["generated_signals"]["decoder-quality"]["split-"+str(z)].append(signal_quality[k])
            k += 1
    k = 0
    for z in range(number_of_splits):
        globals()["generated_signals"]["signals"]["split-"+str(z)] = []
        globals()["generated_signals"]["signals-type"]["split-"+str(z)] = []
        globals()["generated_signals"]["signals-quality"]["split-"+str(z)] = []
        for i in range(video_width):
            globals()["generated_signals"]["signals"]["split-"+str(z)].append(signal[k])
            globals()["generated_signals"]["signals-type"]["split-"+str(z)].append(signal_type[k])
            globals()["generated_signals"]["signals-quality"]["split-"+str(z)].append(signal_quality[k])
            k += 1
        



    with open('Generated_Files\signals.json', 'w+') as f:
        json.dump(generated_signals, f, indent=4)


if __name__ == "__main__":
        raw_data = generate_signal_lists_and_type()
        signal = raw_data[0]
        signal_type = raw_data[1]
        signal_quality = raw_data[2]
        print("Generating Signal Lists...")
        factorio_signals_as_json()




