#nodules.py

# Import required libraries
import os
import cv2
import json
import sys
import subprocess
from image_analysis import ImageAnalyzer
from logger import Logger

from image_analysis import ImageAnalyzer

def get_all_image_files(directory):
    """
    Function to walk through all sub-directories and files within the given directory,
    and gather all the image files (files that end with .jpg or .png).
    Arguments:
    directory -- str, the directory to scan.
    Returns:
    image_files -- list of str, the paths to all image files in the directory and its sub-directories.
    """
    image_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(('.jpg', '.png')):
                image_files.append(os.path.join(dirpath, filename))
    # Sort the images based on their names (which encode the date), and return the list
    return sorted(image_files, key=lambda img: os.path.splitext(os.path.basename(img))[0])

def find_crop_folders(directory):
    """
    Function to walk through all sub-directories and files within the given directory,
    and gather all the crop folders (folders that start with crop).
    Arguments:
    directory -- str, the directory to scan.
    Returns:
    crop_folders -- list of str, the paths to all crop folders in the directory and its sub-directories.
    """
    crop_folders = []
    for dirpath, _, _ in os.walk(directory):
        if os.path.basename(dirpath).startswith('crop'):
            crop_folders.append(dirpath)
        
    # Sort the crop folders based on their names (which encode the date), and return the list
    return sorted(crop_folders, key=lambda img: os.path.splitext(os.path.basename(img))[0])


# loads 
def load_image(file_name):
    """
    Function to load an image using OpenCV.
    Arguments:
    file_name -- str, path to the image file.
    Returns:
    image -- numpy array, loaded image.
    """
    # Read the image
    image = cv2.imread(file_name)
    # If image reading fails, print an error message
    if image is None:
        print(f"Unable to open image file: {file_name}")
    return image


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
        result_entry, matching = ImageAnalyzer.analyze_image(file, output_dir, next_matching=matching, external_logger=logger)
        logger.info(f"analyze_image() returned: {result_entry}")
        results.append(result_entry)

        logger.info(f"DONE processing image: {file}\n\n")

    logger.info("------------------------------------")
    logger.info(f"DONE Processing crop folder: {crop_folder}")

    logger.info(f"Results: {results}")
    return results

