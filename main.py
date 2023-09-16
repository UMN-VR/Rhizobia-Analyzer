# main.py
# Import required libraries

import os
import cv2
import json
import sys
import subprocess
from image_analysis import ImageAnalyzer
from logger import Logger
import psutil

# Import the get_all_image_files function from nodules.py
from nodules import get_all_image_files, find_crop_folders, load_image, process_crop_folder

from HTML_out import generate_results_page
from memory_logger import log_memory_usage

def change_working_directory():
    # Change the working directory to the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__)) # get the path of this script, log will be saved here
    os.chdir(script_dir) # change the working directory to the directory of of this script
    return script_dir

def prepare_output_directory():
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
            os.system("rm -rf output")
            os.makedirs("output")



def create_logger(file_name):
    # remove the extension
    log_name, _ = os.path.splitext(file_name)
    # replace / with _ and capitalize the result
    log_name = log_name.replace('/', '_')
    # creates the logger in /output
    logger = Logger(f'{log_name}.log', "output").get_logger()
    logger.info(f"@main.create_logger(file_name: {file_name})")
    return logger

def process_dir(file_name, main_logger):
    
    # Initialize the results list
    results = []

    # print the directory name to the console
    main_logger.info(f"@main.process_dir(User Input: {file_name}, main_logger: {main_logger})")

    # get all the files in the directory and its subdirectories
    #files = get_all_image_files(file_name)

    # now we have a list of image files
    #main_logger.info(f"Found {len(files)} image files in directory: {file_name}")
    #print(f"Found {len(files)} image files in directory: {file_name}")

    #main_logger.info(f"{files}")  # prints all files found in directory

    # Tell user where the files will be written
    script_output_dir = os.path.join("output", file_name.replace("data", "").strip("/"))
    main_logger.info(f"script_output_dir: {script_output_dir}")
    

    # get all the crop folders in the directory and its subdirectories
    crop_folders = find_crop_folders(file_name)

    print(f"Found {len(crop_folders)} crop folders: {crop_folders}")

    main_logger.info(f"Found {len(crop_folders)} crop folders: {crop_folders}")
    
    # ask the user to continue
    continue_processing = input("Continue processing? (y/n): ")
    if continue_processing.lower() == 'n':
        main_logger.info("User chose to stop processing images")
        return
    
    main_logger.info("User chose to continue processing images")

    for crop_folder in crop_folders:
        log_memory_usage(main_logger)
        main_logger.info(f"Processing crop folder: {crop_folder}")
        print(f"{crop_folder}/")

        # Replace / with _ and capitalize the result
        crop_log_name = crop_folder.replace('/', '_')
        # Create the logger for this specific crop folder
        crop_logger = Logger(f'{crop_log_name}.log', "output").get_logger()
        # Process all images in the crop folder
        result_crop_folder = process_crop_folder(crop_folder, crop_logger)

        entry = [crop_folder, result_crop_folder]
        results.append(entry)
            

    generate_results = input("Generate results? (y/n): ")
    if generate_results.lower() != 'n':
        main_logger.info("User chose to generate results")

        
        generate_results_page(results, script_output_dir, main_logger)


    # Open the last HTML file generated
    if results and results[-1]:
        subprocess.run(["xdg-open", results[-1][-1]], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null



def process_file(file_name, main_logger):
    # get the directory where the results will be saved
    output_dir = os.path.join("output", os.path.dirname(file_name).replace("data", "").strip("/"))
    # Call analyze_image() to process the image, this is where the magic happens
    result_file_name, new_objects = ImageAnalyzer.analyze_image(file_name, output_dir, external_logger=main_logger)
    # Open the HTML file generated
    subprocess.run(["xdg-open", result_file_name], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null


def while_loop_process_images():

    # Main Loop: process images until the user enters 'exit'
    while True:

        # ask user for file name or directory
        file_name = input("Enter the file name (or 'exit' to stop): ")
        
        # if the user enters 'exit', stop the program
        if file_name.lower() == 'exit':
            break
        
        main_logger = create_logger(file_name)
        
        
        # if the user enters a directory, process all the images in the directory
        if os.path.isdir(file_name):
            main_logger.info(f"{file_name} is a directory, starting process_dir()")
            process_dir(file_name, main_logger)
            
                
        # if the user enters a file name, process that file
        elif os.path.isfile(file_name):
            main_logger.info(f"{file_name} is a file, starting process_file()")
            process_file(file_name, main_logger)
        else:
            print("Invalid file name or directory.")
            main_logger.error(f"Invalid file name or directory: {file_name}")
            continue

        # Print Done! to the console and a line 
        print("--------------------------------------------------")
        print("Done!")




def main():

    # Change the working directory to the directory of this file
    script_dir = change_working_directory()

    # Check if the output directory exists, if not make one
    prepare_output_directory()

    # Main Loop: process images until the user enters 'exit'
    while_loop_process_images()
    
    print("Exiting program...")
if __name__ == '__main__':
    main()
