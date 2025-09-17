import base64
import zlib
import json
import pyperclip

def decode_factorio_blueprint(blueprint_string):
    blueprint_string = blueprint_string[1:] # remove the first character '0' which is used by Factorio to indicate the blueprint version
    decoded_data = base64.b64decode(blueprint_string)
    decompressed_data = zlib.decompress(decoded_data)
    blueprint_json = json.loads(decompressed_data)

    return blueprint_json

def save_json_to_file(json_data, file_name="blueprint.json"):
    with open(file_name, 'w') as file:
        json.dump(json_data, file, indent=2)

if __name__ == "__main__":
    factorio_blueprint_string = pyperclip.paste()
    decoded_blueprint = decode_factorio_blueprint(factorio_blueprint_string)
    save_json_to_file(decoded_blueprint)
    print("Saved blueprint as a JSON")
