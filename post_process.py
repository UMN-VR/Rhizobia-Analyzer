import os
import imageio.v2 as imageio
import json
import matplotlib.pyplot as plt
from logger import Logger

from generate_gifs import generate_gifs, generate_gif
from plot_nodule_json_data import plot_nodule_json_data
import time

def post_process(crop_folder, crop_logger):
    crop_logger.info(f"@post_process: crop_folder:{crop_folder}, logger:{crop_logger}")

    # BAD BAD BAD output_dir = os.path.join("output", crop_folder.replace("data/", ""))

    output_dir = os.path.join("output", os.path.basename(crop_folder))
                
                
    #dates_dir =  output_dir+ "/nodules-last-detected-on"
    dates_dir =  os.path.join(output_dir, "nodules-last-detected-on")
    crop_logger.info(f"dates_dir:{dates_dir}")
    
    subdirs = [os.path.join(dates_dir, o) for o in os.listdir(dates_dir) if os.path.isdir(os.path.join(dates_dir,o))]
    
    #print(f"subdirs: {subdirs}")
    crop_logger.info(f"subdirs: {subdirs}")

    

    for subdir in subdirs:

        #@post_process: subdir: output/crop1000/nodules-last-detected-on/2023-05-03

        #break up subdir into date and crop_number
        # date should be set to like 20230503
        # crop_number should be set to like crop980

        # split the subdir by '/' 
        # BAD BAD BAD subdir_split = subdir.split("/")

        subdir_split = os.path.normpath(subdir).split(os.sep)

        # get the last element of the subdir_split, remove the '-' and set it to current_date
        current_date = subdir_split[-1].replace("-", "")

        # get the second element of the subdir_split and set it to crop_number
        crop_number = subdir_split[2]

        image_output_dir = os.path.join(output_dir, current_date)

        # Create a logger for this image
        log_name = f"{crop_number}_{current_date}.log"

        logger = Logger(log_name, image_output_dir, external_logger=crop_logger).get_logger()

        #Start timer
        start_time = time.time()


        subdir_folder = subdir.split("/")[-1]
        logger.info(f"@post_process: subdir: {subdir}")
        print(f"@post_process: subdir: {subdir}", end='', flush=True)

        year, month, day = os.path.basename(subdir).split("-")
        
        nodules_subdirs = [os.path.join(subdir, o) for o in os.listdir(subdir) if os.path.isdir(os.path.join(subdir,o))]

        i_nodule = 0

        for nodule_dir in nodules_subdirs:

            i_nodule += 1
            generate_gifs(nodule_dir, logger)
            #print(f"number_of_entries: {number_of_entries}")

            print('.', end='', flush=True)

            #print(f"nodule_dir: {nodule_dir}")


            # Call the plotting function
            plot_nodule_json_data(nodule_dir, logger)


            #wait for user input
            #input("Press Enter to continue...")

        end_time = time.time()
        time_elapsed = round((end_time - start_time), 2)

        logger.info(f"@post_process: {subdir}, {i_nodule} nodules, took {time_elapsed}s")
        print(f"\n@post_process: {subdir}, {i_nodule} nodules, took {time_elapsed}s\n")

    

# logger = Logger("generate_gifs").get_logger()

# post_process("data/crop1000", logger)



#plot_nodule_json_data("output/crop1000/nodules-last-detected-on/2023-06-07/39")