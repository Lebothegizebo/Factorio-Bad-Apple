import sys
import base64
import json
import zlib
import pyperclip


colour_mode = "2 bit" # "256 bit", "2 bit"
video_height = 96 # Needs to be a divisor of 8 in 256 bit colour mode, or 32 in 2 bit colour mode
video_width = 128 # Can be any width, but generally keep to video ratios

if colour_mode == "256 bit":
    bit_size = 4 # 256 bit colour
elif colour_mode == "2 bit":
    bit_size = 32 # 2 bit colour

number_of_splits = video_height/bit_size# Number of Horizontal splits to split the video into to fit all binary signals
if number_of_splits <1:
    number_of_splits = 1
splits_height = round(video_height/number_of_splits) #Vertical Height of each split, used for generating signals


