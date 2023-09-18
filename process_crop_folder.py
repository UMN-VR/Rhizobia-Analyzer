#process_crop_folder.py

# Import required libraries
import os

from image_analysis import ImageAnalyzer

from image_analysis import ImageAnalyzer

from dir_utils import get_all_image_files

from analyze_image import analyze_image


def process_crop_folder(crop_folder, logger):
    """
    Function to process all images in a crop folder, starting with the most recent one.
    Arguments:
    crop_folder -- str, path to the crop folder.
    """

    logger.info(f"\n@process_crop_folder: Processing crop folder: {crop_folder}")

    # get all the files in the crop folder and its subdirectories
    files = get_all_image_files(crop_folder)

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

        #print just the file name to the console
        print(f"{os.path.basename(file)}")

        # get the directory where the results will be saved
        output_dir = os.path.join("output", os.path.dirname(file).replace("data", "").strip("/"))


        # Call analyze_image() to process the image, this is where the magic happens
        logger.info(f"Calling analyze_image() with file: {file}, output_dir: {output_dir}")
        result_entry, matching = analyze_image(file, output_dir, next_matching=matching, external_logger=logger)
        
        logger.info(f"analyze_image() returned: {result_entry}")
        results.append(result_entry)

        logger.info(f"DONE processing image: {file}\n\n")


    #results2 = ImageAnalyzer.post_process(nodules_folders) 
    logger.info("------------------------------------")
    logger.info(f"DONE Processing crop folder: {crop_folder}")

    logger.info(f"Results: {results}")
    return results

