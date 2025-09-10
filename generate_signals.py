import sys
import base64
import json
import zlib
import pyperclip
import os

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

use_vanilla_signals = True #Default True
use_custom_signals = False #Default False
use_space_age = True #Default False
use_quality = False #Default False #NOT IMPLEMENTED
bypass_custom_signal_warning = False #Default False
bypass_custom_and_vanilla_signal_warning = False #Default False #REMOVE WHEN DUPLICATE SIGNAL CHECKS HAVE BEEN MADE
custom_signal_json_path = R"Custom Signals\custom_example.json" #Default: "Custom Signals\custom_example.json" # Use a decoded base64 json file of a constant combinator of all the signals you want. This uses the textplates mod as an example.

colour_mode = "2 bit" # "256 bit", "2 bit"
video_height = 96 # Needs to be a divisor of 8 in 256 bit colour mode, or 32 in 2 bit colour mode
video_width = 128 # Can be any width, but generally keep to video ratios
generated_signals = {"decoder": {}, "decoder-type": {}, "signals": {}, "signals-type": {}} #Signal list that the program uses to generate memory and the decoder

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

    if globals()["use_vanilla_signals"]: #Included Signals
        for i in range(len(raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"])):
            signals.extend([raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["name"]])
            try:
                signals_type.extend([raw_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["type"]])
            except:   
                signals_type.extend([None])

    if globals()["use_custom_signals"] == True: #Custom Signals
        for i in range(len(raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"])):
            signals.extend([raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["name"]])
            try:
                signals_type.extend([raw_custom_signal_list["blueprint"]["entities"][0]["control_behavior"]["sections"]["sections"][0]["filters"][i]["type"]])
            except:   
                signals_type.extend([None])
    
    # print("signals: ", signals)
    # print("\n")
    # print("signals length: ", len(signals))
    # print("\n")
    # print("signals_type", signals_type)
    # print("\n")
    # print("signals_type length: ", len(signals_type))
    return signals, signals_type

def factorio_signals_as_json():
    i = 0
    print(splits_height)
    for z in range(number_of_splits):
        print(i)
        globals()["generated_signals"]["decoder"]["split-"+str(z)] = []
        globals()["generated_signals"]["decoder-type"]["split-"+str(z)] = []
        globals()["generated_signals"]["signals"]["split-"+str(z)] = []
        globals()["generated_signals"]["signals-type"]["split-"+str(z)] = []
        for i in range(splits_height):
            globals()["generated_signals"]["decoder"]["split-"+str(z)].append(signal[i])
            globals()["generated_signals"]["decoder-type"]["split-"+str(z)].append(signal_type[i])
            globals()["generated_signals"]["signals"]["split-"+str(z)].append(signal[i])
            globals()["generated_signals"]["signals-type"]["split-"+str(z)].append(signal_type[i])
            i += 1
        



    with open('signalsHD.json', 'w+') as f:
        json.dump(generated_signals, f, indent=4)


if __name__ == "__main__":
        
        raw_data = generate_signal_lists_and_type()
        signal = raw_data[0]
        signal_type = raw_data [1]
        print("Generating Signal Lists...")
        factorio_signals_as_json()




