import os
import csv


def initialize_csv_file(filename):
    dir_name = os.path.dirname(filename)

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csv.writer(f).writerow(



def append_to_csv_list(filename, item):
    
        #item_str = json.dumps(item, indent=1)
        #item_str = json.dumps(item)
    
        initialize_csv_file(filename)
    
        with open(filename, 'a', newline='') as f:
            # Move to the position just before the last character
            #f.seek(os.path.getsize(filename) - 1)
            
            #if f.tell() > 1:
            #    f.write(',\n')
            
            #f.write(f"{item_str}]")
            writer = csv.writer(f)
            writer.writerow(item)