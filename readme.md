Requires:
OS INSTALL:
    https://ffmpeg.org/ (ffmpeg)
Python3:  (Run program first, it will tell you what modules you are missing)
    pyperclip
    configparser
    Pillow (PIL)
    numpy
    opencv-python 

Beta Instructions:

1: Run generate_signals.py to generate the Factorio Signals used by this program.
    IF IT ERRORS:
        Your target resolution is too high, there isint enough signals in Factorio to fully represent the display.
        Either:
            Decrease the target resoluton,
            OR Ensure use_space_age and use_quality is true in config.ini
            OR add custom signals (just unpack a blueprint containing a constant combinator of all the signals you want, and direct this program to it. An example is in Custom Signals/custom_example.json)
            OR add custom quality (Custom Quality is not implemented yet)


2: Run generate_decoder.py <video_path>, place blueprint in world.
3: Run generate_memory.py <video_path>, place blueprint next to decoder.
    IF MULTIPLE CHUNKS ARE USED:
        For each chunk, ensure that Chunk 1's Combinators (Back, Green Wire, Front, Red Wire) is connected to Chunk 2 (Back, Green wire, Front, Red Wire)

4: Connect memory to a clock by connecting: Clock Output (Green wire) (Output must be as F) -> Back of memory decider combinator (Green Wire) 
5: Connect memory to the decoder by connecting: Front of any memory decider combinator (Red Wire) -> Back of any arthimitic combinator (Red Wire)

Config.ini:
    Ensure that the target resolution is a multiple of 2 (NOT ODD, MUST BE EVEN.), FFMPEG does not play well with odd resolutions.

Feel free to contact me for any help at discord.gg/FKmACzfZxP (MY DISCORD SERVER)