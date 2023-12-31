# main.py

import os
import time

from Logger import Logger

from dir_utils import change_working_directory, prompt_clear_output_directory
from process_dir import process_dir
from process_file import process_file

program_name = "Rhizobia Analyser"
program_version = "8.0"


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
        command = input("Enter crop folder dir ie: 'data', 'data/crop1000', etc. (or 'exit' to stop): ")

        # split command by 'start_at:' to get the file name to start at
        commands = command.split('start_at:')
        if len(commands) == 1:
            command = commands[0]
            #remove any spaces in command
            command = command.replace(' ', '')
            start_at = None
        elif len(commands) == 2:
            command = commands[0]
            #remove any spaces in command
            command = command.replace(' ', '')

            start_at = commands[1]
        
        print(f"command: {command}, start_at: {start_at}")

        #start timer
        start_time = time.time()
        
        # if the user enters 'exit', stop the program
        if command.lower() == 'exit':
            break

        
        # if command.startswith('data/'):
        #     print(f"command: {command} starts with 'data/' ")
        #     pass

        file_name=command

        print(f"file_name: {file_name}")
        main_log = 'exec_'+file_name.replace('/', '_')

        print(f"Starting log at {main_log}")

        main_logger = Logger(main_log).get_logger()
        
        
        # if the user enters a directory, process all the images in the directory
        if os.path.isdir(file_name):
            main_logger.info(f"{file_name} is a directory, starting process_dir()")
            process_dir(file_name, main_logger, start_at)
            
                
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
    print("--------------------------------------------------")
    print(f"Starting {program_name} v{program_version}...")


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
