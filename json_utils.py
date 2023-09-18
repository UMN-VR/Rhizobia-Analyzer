import os
import sys
import json

def load_json(file_name):
    """
    Load JSON data from the file.
    """
    json_file_name = os.path.splitext(file_name)[0] + '.json'
    with open(json_file_name, 'r') as json_file:
        json_data = json.load(json_file)
    if json_data is None:
        print(f'Unable to load JSON file: {json_file_name}!')
        sys.exit(1)
    return json_data



def scale_json(json_data, scalar_position=0.5, scalar_size=0.5):
    """
    Scale the coordinates of the JSON data.
    """

    for json_obj in json_data:
        json_obj["x"] = int(json_obj["x"] * scalar_position)
        json_obj["y"] = int(json_obj["y"] * scalar_position)
        json_obj["d"] = int(json_obj["d"] * scalar_size)
    return json_data