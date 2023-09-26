#process_crop_folder.py

# Import required libraries
import os

from image_analysis import ImageAnalyzer

from image_analysis import ImageAnalyzer

from dir_utils import get_all_image_files

from analyze_image import analyze_image

from post_process import post_process

import time

import json

from generate_gifs import generate_gif_from_list, generate_gif

def process_crop_folder(crop_folder, logger):
    """
    Function to process all images in a crop folder, starting with the most recent one.
    Arguments:
    crop_folder -- str, path to the crop folder.
    """

    logger.info(f"\n@process_crop_folder: crop_folder: {crop_folder}")

    # get all the files in the crop folder and its subdirectories
    files = get_all_image_files(crop_folder)

    crop_number = os.path.basename(crop_folder)

    logger.info(f"Generating crop plots gif")
    gif_path = f"output/{crop_number}/{crop_number}.gif"
    generate_gif_from_list(files, f"output/{crop_number}/{crop_number}.gif", logger)


    # tell user which files were found
    logger.info(f"Found {len(files)} files: {files}")
    
    # Initialize the tracked objects
    objects = []
    # Initialize the results list
    results = []

    logger.info( "------------------------------------\n\n")

    matching = None

    # process each image in reverse order (newest first)
    for file in reversed(files):
        logger.info(f"Processing image: {file}")
        #logger.info(f"Objects: {objects}")
        #logger.info("\n")

        start_time = time.time()

        #print just the file name to the console
        print(f"{os.path.basename(file)}")

        # get the directory where the results will be saved
        output_dir = os.path.join("output", os.path.dirname(file).replace("data", "").strip("/"))


        # Call analyze_image() to process the image, this is where the magic happens
        logger.info(f"Calling analyze_image() with file: {file}, output_dir: {output_dir}")
        result_entry, matching = analyze_image(file, output_dir, next_matching=matching, external_logger=logger)
        
        logger.info(f"analyze_image() returned: {result_entry}")
        results.append(result_entry)

        end_time = time.time()

        dt = end_time - start_time

        logger.info(f"DONE processing image: {file}, took {dt}s\n\n")




    logger.info(f"Generating crop plots gif")

    plots_gif_path = f"{output_dir}/plots/plots.gif"
    generate_gif(f"{output_dir}/plots", 'plots.gif', logger)


    logger.info(f"Calling post_process() with crop_folder: {crop_folder}")

    post_process(crop_folder, logger)




    results = {crop_number : results, "gif_path" : gif_path, "plots_gif_path" : plots_gif_path}

    #save results to a json file in 'output/{crop_folder}/results.json'
    logger.info(f"Saving results to: output/{crop_folder}/results.json")

    crop_result_filename = f"output/{crop_number}/{crop_number}.json"

    with open(f"{crop_result_filename}", 'w') as f:
        json.dump(results, f, indent=1)

    result = {crop_folder : crop_result_filename, "gif_path" : gif_path, "plots_gif_path" : plots_gif_path}


    logger.info("------------------------------------")
    logger.info(f"DONE Processing crop folder: {crop_folder}")

    logger.info(f"Results: {results}")
    logger.info(f"Result: {result}")
    return result

