import sys
import base64
import json
import zlib
import os

video_path = "bad-apple.mp4"
os.system(R"ffmpeg -i "+video_path+R" -vf palettegen Generated_Files\ffmpeg\palette.png -hide_banner -loglevel error")
os.system(R"ffmpeg -i "+video_path+R" -i Generated_Files\ffmpeg\palette.png -filter_complex 'paletteuse' Generated_Files\ffmpeg\out.gif -hide_banner -loglevel error")