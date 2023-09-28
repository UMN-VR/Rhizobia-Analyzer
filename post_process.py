import os
import imageio.v2 as imageio
import json
import matplotlib.pyplot as plt
from Logger import Logger

from generate_gifs import generate_gifs, generate_gif
from plot_nodule_json_data import plot_nodule_json_data
import time

def post_process(crop_folder, logger):
    logger.info(f"@post_process: crop_folder:{crop_folder}, logger:{logger}")

    output_dir = os.path.join("output", crop_folder.replace("data/", ""))
                
                
    dates_dir =  output_dir+ "/nodules-last-detected-on"
    logger.info(f"dates_dir:{dates_dir}")
    
    subdirs = [os.path.join(dates_dir, o) for o in os.listdir(dates_dir) if os.path.isdir(os.path.join(dates_dir,o))]
    
    #print(f"subdirs: {subdirs}")
    logger.info(f"subdirs: {subdirs}")

    

    for subdir in subdirs:

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