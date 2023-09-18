# main.py

import os
import time

from Logger import Logger

from dir_utils import change_working_directory, prompt_clear_output_directory
from process_dir import process_dir
from process_file import process_file



def while_loop_process_images():
    """
    Main Loop: 
    
    1: Prompts user for file name or directory, exits if user enters 'exit'

    2: Creates logger with the name of the file or directory entered by the user at 'output'

    3: 

    If the user enters a directory, process all the images in the directory with process_dir()
    
    Else if the user enters a file name, process that file with process_file()
    
    """

    # Main Loop: process images until the user enters 'exit'
    while True:

        # ask user for file name or directory
        file_name = input("Enter the file name (or 'exit' to stop): ")

        #start timer
        start_time = time.time()
        
        # if the user enters 'exit', stop the program
        if file_name.lower() == 'exit':
            break
        
        main_logger = Logger(file_name).get_logger()
        
        
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
    """
    Main function, called when this script is run.
    
    1: Change the working directory to the directory of this file
    2: Check if the output directory exists and is empty, if not make one or clear it
    3: Main Loop: process images until the user enters 'exit'
    4: Done!

    """



    # Change the working directory to the directory of this file
    script_dir = change_working_directory()

    # Check if the output directory exists, if not make one
    prompt_clear_output_directory()

    # Main Loop: process images until the user enters 'exit'
    while_loop_process_images()
    


    print("--------------------------------------------------")
    print("Exiting program...")


# This is the standard boilerplate that calls the main() function.    
if __name__ == '__main__':
    main()
