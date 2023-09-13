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


def main():
    # Change the working directory to the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__)) # get the path of this script, log will be saved here
    os.chdir(script_dir) # change the working directory to the directory of of this script
    
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

    # Main Loop: process images until the user enters 'exit'
    while True:
        # ask user for file name or directory
        file_name = input("Enter the file name (or 'exit' to stop): ")
        # if the user enters 'exit', stop the program
        if file_name.lower() == 'exit':
            break
            
        # remove the extension
        log_name, _ = os.path.splitext(file_name)
        # replace / with _ and capitalize the result
        log_name = log_name.replace('/', '_')
        # creates the logger in /output
        logger = Logger(f'{log_name}.log', "output").get_logger()
        # Initialize the results list
        results = []
        # if the user enters a directory, process all the images in the directory
        if os.path.isdir(file_name):
            logger.info(f"Detected directory: {file_name}")
            # get all the files in the directory and its subdirectories
            files = get_all_image_files(file_name)
            # now we have a list of image files
            logger.info(f"Found {len(files)} image files in directory: {file_name}")
            
            logger.info(f"{files}")  # prints all files found in directory
            print(f"Found {len(files)} image files in directory: {file_name}")
            # Tell user where the files will be written
            script_output_dir = os.path.join("output", file_name.replace("data", "").strip("/"))
            print(f"Will write files to directory: {script_output_dir}")
            
            # if the user typed 'data' then there are multiple crop folders 
            # for each crop folder that will be created a separate log file will be created, and an empty list of objects will be created
            crop_folders = find_crop_folders(file_name)    
            print(f"Found {len(crop_folders)} crop folders: {crop_folders}")
            
            # ask the user to continue
            continue_processing = input("Continue processing? (y/n): ")
            if continue_processing.lower() == 'n':
                logger.info("User chose to stop processing images")
                break
            
            logger.info("User chose to continue processing images")
            for crop_folder in crop_folders:
                log_memory_usage(logger)
                logger.info(f"Processing crop folder: {crop_folder}")
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
                logger.info("User chose to generate results")

                
                generate_results_page(results, script_output_dir, logger)
        


            # Open the last HTML file generated
            if results and results[-1]:
                subprocess.run(["xdg-open", results[-1][-1]], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null
                
        # if the user enters a file name, process that file
        elif os.path.isfile(file_name):
            # get the directory where the results will be saved
            output_dir = os.path.join("output", os.path.dirname(file_name).replace("data", "").strip("/"))
            # Call analyze_image() to process the image, this is where the magic happens
            result_file_name, new_objects = ImageAnalyzer.analyze_image(file_name, output_dir, external_logger=logger)
            # Open the HTML file generated
            subprocess.run(["xdg-open", result_file_name], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null
        else:
            print("Invalid file name or directory.")
            logger.error(f"Invalid file name or directory: {file_name}")
            continue

        # Print Done! to the console and a line 
        print("--------------------------------------------------")
        print("Done!")
    
    print("Exiting program...")
if __name__ == '__main__':
    main()
