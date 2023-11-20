#dir_utils.py 
import os
import shutil

def change_working_directory():
    # Change the working directory to the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__)) # get the path of this script, log will be saved here
    os.chdir(script_dir) # change the working directory to the directory of of this script
    return script_dir

def prompt_clear_output_directory():
    directory = "output"
    # Check if the output directory exists, if not make one
    if not os.path.isdir("output"):
        os.makedirs("output")
    else:
        # ask the user if they want to clear the output directory
        print("It is recommended to clear the output directory before running this script.")
        user_input = input("Would you like to clear the output directory? (y/n): ")
        if not user_input.lower() == 'n':
            # delete the output directory
            print("Clearing output directory...")
            if os.path.exists(directory):
                shutil.rmtree(directory)

            os.makedirs("output")


def get_all_image_files(directory):
    """
    Function to walk through all sub-directories and files within the given directory,
    and gather all the image files (files that end with .jpg or .png).
    Arguments:
    directory -- str, the directory to scan.
    Returns:
    image_files -- list of str, the paths to all image files in the directory and its sub-directories.
    """
    image_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(('.jpg', '.png')):
                image_files.append(os.path.join(dirpath, filename))
    # Sort the images based on their names (which encode the date), and return the list
    return sorted(image_files, key=lambda img: os.path.splitext(os.path.basename(img))[0])

def find_crop_folders(directory):
    """
    Function to walk through all sub-directories and files within the given directory,
    and gather all the crop folders (folders that start with crop).
    Arguments:
    directory -- str, the directory to scan.
    Returns:
    crop_folders -- list of str, the paths to all crop folders in the directory and its sub-directories.
    """
    crop_folders = []
    for dirpath, _, _ in os.walk(directory):
        if os.path.basename(dirpath).startswith('crop'):
            crop_folders.append(dirpath)
        
    # Sort the crop folders based on their names (which encode the date), and return the list
    return sorted(crop_folders, key=lambda img: os.path.splitext(os.path.basename(img))[0])



