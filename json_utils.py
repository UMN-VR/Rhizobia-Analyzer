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

def initialize_json_file(filename):
    dir_name = os.path.dirname(filename)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)


def append_to_json_list(filename, item):


    #item_str = json.dumps(item, indent=1)
    item_str = json.dumps(item)


    initialize_json_file(filename)

    with open(filename, 'r+') as f:
        # Move to the position just before the last character
        f.seek(os.path.getsize(filename) - 1)
        
        if f.tell() > 1:
            f.write(',\n')
        
        f.write(f"{item_str}]")

# def initialize_json_file(filename):

#     print(f"@initialize_json_file: filename: {filename}")

#     # get dir part of filename
#     dir_name = os.path.dirname(filename)

#     # if the dir does not exist, create it
#     os.makedirs(dir_name, exist_ok=True)

#     with open(filename, 'w') as f:
#         json.dump([], f)

# def test_append_to_json_list():
#     test_filename = "test/test_list.json"

#     #initialize_json_file(test_filename)

#     # Test 1
#     append_to_json_list(test_filename, {"name": "Alice", "age": 30})
#     with open(test_filename, 'r') as f:
#         data = json.load(f)
#     assert data == [{"name": "Alice", "age": 30}]

#     # Test 2
#     append_to_json_list(test_filename, {"name": "Bob", "age": 40})
#     with open(test_filename, 'r') as f:
#         data = json.load(f)
#     assert data == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}]

#     # Test 3
#     append_to_json_list(test_filename, 100)
#     with open(test_filename, 'r') as f:
#         data = json.load(f)
#     assert data == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}, 100]

#     # Test 4
#     append_to_json_list(test_filename, "hello")
#     with open(test_filename, 'r') as f:
#         data = json.load(f)
#     assert data == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}, 100, "hello"]

#     #os.remove(test_filename)

# #Run the tests
# test_append_to_json_list()