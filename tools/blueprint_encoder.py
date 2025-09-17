import base64
import zlib
import json
import pyperclip

def encode_factorio_blueprint(blueprint_json):
    blueprint_string = json.dumps(blueprint_json)
    compressed_data = zlib.compress(blueprint_string.encode())
    encoded_data = base64.b64encode(compressed_data)
    blueprint_string = '0' + encoded_data.decode()
    return blueprint_string

def load_json_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    file_path = "blueprint.json"
    factorio_blueprint_json = load_json_from_file(file_path)
    encoded_blueprint = encode_factorio_blueprint(factorio_blueprint_json)
    pyperclip.copy(encoded_blueprint)
    print("Encoded Factorio Blueprint String has been copied to your clipboard!")
