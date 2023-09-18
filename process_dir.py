import os

# Import the get_all_image_files function from nodules.py
from process_crop_folder import process_crop_folder

from dir_utils import find_crop_folders

from HTML_out import generate_results_page
from memory_logger import log_memory_usage
from Logger import Logger
import subprocess

def process_dir(file_name, main_logger):
    """
    1: finds all the crop folders in the directory and its subdirectories

    2: prompts the user for confirmation to continue processing

    3: for each crop folder
        1: creates a logger for that crop folder with the name of that crop folder at 'output'
        2: process all the images in the crop folder with process_crop_folder()

        
    4: prompts the user for confirmation to generate results

    """
    
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

