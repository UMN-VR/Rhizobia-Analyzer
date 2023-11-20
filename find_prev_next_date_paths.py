# find_prev_next_date_paths.py
import os
from datetime import datetime

def find_prev_next_date_paths(image_output_dir, logger):

        logger.info(f"\n@find_prev_next_date: image_output_dir: {image_output_dir}")
        
        # Log the entire path for debugging
        logger.info(f"Full image_output_dir path: {os.path.abspath(image_output_dir)}")

        # get the crop number from the image output directory
        crop_number = os.path.basename(os.path.dirname(image_output_dir))
        logger.info(f"Crop number extracted: {crop_number}")

        # construct the data directory path
        data_dir = os.path.join('data', crop_number)
        logger.info(f"data_dir constructed: {data_dir}")

        # Check if data_dir exists
        if not os.path.exists(data_dir):
            logger.error(f"Data directory not found: {data_dir}")
            return None, None
        
        # get the current date from the image output directory
        current_date = os.path.basename(image_output_dir)
        date_format = "%Y%m%d"
        current_date_obj = datetime.strptime(current_date, date_format)

        # initialize previous and next date as None
        prev_date_path = None
        next_date_path = None
        prev_date_obj = None
        next_date_obj = None

        # check every file in the data directory
        for file in os.listdir(data_dir):
            # print the file name to the console
            # logger.info(f"File: {file}")
            # check if the file name is a date
            if file[:8].isdigit() and len(file[:8]) == 8:
                file_date_obj = datetime.strptime(file[:8], date_format)
                # if the file date is earlier than current date
                if file_date_obj < current_date_obj:
                    # if there's no previous date yet, or this date is later than the currently found previous date
                    if prev_date_obj is None or file_date_obj > prev_date_obj:
                        prev_date_path = os.path.join(data_dir, file)
                        prev_date_obj = file_date_obj
                # if the file date is later than current date
                elif file_date_obj > current_date_obj:
                    # if there's no next date yet, or this date is earlier than the currently found next date
                    if next_date_obj is None or file_date_obj < next_date_obj:
                        next_date_path = os.path.join(data_dir, file)
                        next_date_obj = file_date_obj

        logger.info(f"Previous date file: {prev_date_path}, Next date file: {next_date_path}\n\n")

        return prev_date_path, next_date_path