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

from plot_crop import plot_crop

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
    crop_result_filename = f"output/{crop_number}/{crop_number}.json"

    output_dir = os.path.join("output", crop_number)
    dif_plot_path = f"{output_dir}/plots/dif_plot"
    dif_plot_dx_dy_da_dp_path = f"{output_dir}/plots/dif_plot_dx_dy_da_dp.png"
    dif_plot_i_tq_dd_de_path = f"{output_dir}/plots/dif_plot_i_tq_dd_de.png"
    dif_plot_i_dict_path = f"{output_dir}/plots/dif_plot_i_dict.png"
    dif_plot_matching_tq_path = f"{output_dir}/plots/dif_plot_matching_tq.png"

    logger.info(f"Generating crop plots gif")
    gif_path = f"output/{crop_number}/{crop_number}.gif"
    generate_gif_from_list(files, f"output/{crop_number}/{crop_number}.gif", logger, draw_text=True, filename_is_date=True)


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
    generate_gif(f"{output_dir}/plots", 'plots.gif', logger, duration=1000)

    results = {crop_number : results, "gif_path" : gif_path, "plots_gif_path" : plots_gif_path, "dif_plot_path" : dif_plot_path}

    #save results to a json file in 'output/{crop_folder}/results.json'
    logger.info(f"Saving results to: output/{crop_folder}/results.json")

    with open(f"{crop_result_filename}", 'w') as f:
        json.dump(results, f, indent=1)


    #/output/crop980/crop980.json

    plot_crop(crop_result_filename, dif_plot_path, logger)

    logger.info(f"Calling post_process() with crop_folder: {crop_folder}")
    post_process(crop_folder, logger)




    result = {crop_folder : crop_result_filename, "gif_path" : gif_path, "plots_gif_path" : plots_gif_path, "dif_plot_dx_dy_da_dp_path" : dif_plot_dx_dy_da_dp_path, "dif_plot_i_tq_dd_de_path" : dif_plot_i_tq_dd_de_path, "dif_plot_i_dict_path" : dif_plot_i_dict_path, "dif_plot_matching_tq_path" : dif_plot_matching_tq_path}


    logger.info("------------------------------------")
    logger.info(f"DONE Processing crop folder: {crop_folder}")

    logger.info(f"Results: {results}")
    logger.info(f"Result: {result}")
    return result

