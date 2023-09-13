```python
#nodule_analysis.py
# nodule_analysis.py
import json
import os
from logger import Logger
from html_generator import HtmlGenerator
import matplotlib.pyplot as plt

class NoduleAnalysis:
    def __init__(self, logger):
        self.logger = logger

    def generate_flow_fields(self, json_file, output_dir):
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
        logger = Logger("nodule_analysis.log", output_dir).get_logger()
        logger.info('Loading data from JSON file.')
        nodule_info = self.load_data(json_file)
        
        if nodule_info is None:
            print("Program failed to load JSON")

        dates = sorted(nodule_info.keys())

        logger.info('Data loaded successfully. Starting analysis.')

        for i in range(len(dates) - 1):
            current_date = dates[i]
            next_date = dates[i + 1]
            logger.info(f'Matching IDs for dates: {current_date} and {next_date}.')
            id_mapping = self.match_ids(nodule_info, current_date, next_date)
            logger.info(f'Plotting flow field for dates: {current_date} and {next_date}.')
            self.plot_flow_field(nodule_info, current_date, next_date, id_mapping, output_dir, logger)
            logger.info(f'Flow field for dates: {current_date} and {next_date} plotted successfully.')

            # Collect the data between the transition into a dictionary
            transition_data = {
                'cd': current_date,
                'nd': next_date,
                'c_nodules': [[round(nodule['x'], 2), round(nodule['y'], 2), round(nodule['diameter'], 2),
                               round(nodule['perimeter'], 2), round(nodule['eccentricity'], 4)]
                              for nodule in nodule_info[current_date]],
                'n_nodules': [[round(nodule['x'], 2), round(nodule['y'], 2), round(nodule['diameter'], 2),
                               round(nodule['perimeter'], 2), round(nodule['eccentricity'], 4)]
                              for nodule in nodule_info[next_date]],
                'id_map': id_mapping,
                'output_dir': output_dir
            }

            # Save the transition data as a separate JSON file for each transition
            transition_file = os.path.join(output_dir, f'transition_data_{current_date}_{next_date}.json')
            with open(transition_file, 'w') as f:
                json.dump(transition_data, f, indent=4)

            logger.info(f'Transition data saved to {transition_file}.')

        logger.info('Analysis complete.')

    @staticmethod
    def load_data(json_file):
        """
        Load nodule information from the JSON file.

        :param json_file: Path to the JSON file containing the nodule information.
        :return: The loaded nodule information as a Python dictionary.
        """

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"No file found for the name {json_file}")
            return None

    @staticmethod
    def match_ids(nodule_info, current_date, next_date):
        """
        Find the closest nodule at the next date for each nodule at the current date and match their IDs.

        :param nodule_info: The nodule information.
        :param current_date: The current date.
        :param next_date: The next date.
        :return: A dictionary with the IDs of the nodules at the current date as the keys and the IDs of the closest nodules
                 at the next date as the values.
        """
        current_nodules = nodule_info[current_date]
        next_nodules = nodule_info[next_date]
        id_mapping = {}

        # Iterate over current nodules
        for i, current_nodule in enumerate(current_nodules):
            current_x = current_nodule['x']
            current_y = current_nodule['y']
            closest_nodule = None
            min_distance = float('inf')

            # Find the closest nodule in the next date
            for j, next_nodule in enumerate(next_nodules):
                next_x = next_nodule['x']
                next_y = next_nodule['y']
                distance = ((current_x - next_x) ** 2 + (current_y - next_y) ** 2) ** 0.5

                if distance < min_distance:
                    closest_nodule = next_nodule
                    min_distance = distance

            if closest_nodule:
                current_id = i + 1
                next_id = next_nodules.index(closest_nodule) + 1
                id_mapping[current_id] = next_id

        return id_mapping

    @staticmethod
    def plot_flow_field(nodule_info, current_date, next_date, id_mapping, output_dir, logger):
        """
        Plot the movement of the nodules from the current date to the next date as a flow field.

        :param nodule_info: The nodule information.
        :param current_date: The current date.
        :param next_date: The next date.
        :param id_mapping: The ID mapping from the current date to the next date.
        """
        current_nodules = nodule_info[current_date]
        next_nodules = nodule_info[next_date]

        # Set up the plot
        plt.figure(figsize=(8, 6))

        # Plot current nodules
        for nodule in current_nodules:
            x = nodule['x']
            y = nodule['y']
            nodule_id = nodule['id']
    

            # Check if the current nodule is in the id_mapping dictionary
            if nodule_id in id_mapping:
                # Get the ID of the matched nodule in the next date
                matched_id = id_mapping[nodule_id]
                # Find the matched nodule in the next date
                matched_nodule = next_nodules[matched_id - 1]
                matched_x = matched_nodule['x']
                matched_y = matched_nodule['y']
                # Draw a line connecting the current nodule and the matched nodule
                plt.plot([x, matched_x], [y, matched_y], color='black')

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(f'Flow Field: {current_date} to {next_date}')
        plt.axis('equal')

        # Save the plot as an image
        plt.savefig(os.path.join(output_dir, f'flow_field_{current_date}_{next_date}.png'))
        plt.close()

        logger.info(f'Flow field for dates: {current_date} and {next_date} plotted successfully.')



```





```python
#image_processing.py
import os
import cv2
import json
import sys
import numpy as np
from logger import Logger

import image_analysis




class ImageProcessor:

    @staticmethod
    def get_max_id(tracked_objects):
        """ Find the maximum ID in the list of tracked objects. """
        if tracked_objects is not None and len(tracked_objects) > 0:
            # Extract date and id components from id string
            id_components = [(obj['id'].split('_')[0], int(obj['id'].split('_')[1])) for obj in tracked_objects if obj['id'] is not None]
            # Find the maximum id component
            max_id = max(id_components, key=lambda x: x[1])
            # Reconstruct the id string
            max_id_str = f"{max_id[0]}_{max_id[1]}"
            return max_id_str
        else:
            return None



        

    @staticmethod
    def find_dayJSON_match_for_contour(x, y, w, h, area, json_data, logger):
        """
        Match contour with JSON data and return matched object.

        JSON_data example:
        {'x': 186, 'y': 92, 'd': 13, 'a': 541.0, 'p': 87.3553, 'e': 0.681415}, {'x': 241, 'y': 95, 'd': 7, 'a': 186.0, 'p': 48.0416, 'e': 0.57267}, {'x': 164, 'y': 98, 'd': 4, 'a': 63.0, 'p': 26.7279, 'e': 0.383255},


        
        Checks if any of the rectangle generated from the contour encloses the centroid of any of the JSON objects.

        If a match is found, return the matched object, otherwise return None and print closest match to logger. 
        """

        logger.info(f"@find_dayJSON_match_for_contour: x: {x}, y: {y}, w: {w}, h: {h}, area: {area}")
        #logger.info(f"JSON data: {json_data}")

        #logger.info(f"JSON data: {json_data}")

        # Initialize the closest match
        closest_match = None

        distances = []

        i = 0
        # Process each JSON object
        for json_obj in json_data:
            i += 1
            # parse the JSON object
            json_x, json_y, json_d, json_a, json_p, json_e = json_obj["x"], json_obj["y"], json_obj["d"], json_obj["a"], json_obj["p"], json_obj["e"]

            # calculate if the centroid of the JSON object is inside the rectangle
            if x <= json_x <= x + w and y <= json_y <= y + h:

                # Print the results to the console
                logger.info(f"Matched with JSON#{i}: ({json_x}, {json_y}, {json_d}, {json_a}, {json_p}, {json_e})")

                # add ID as i to JSON object
                json_obj["id"] = i

                # add tq (Tracking Confidence) to JSON object
                json_obj["tq"] = 100

                # return the matched object

                return json_obj

            # if not inside of rectangle calculate distance from centroid to rectangle
            else:
                # calculate the distance between the centroid of the contour and the centroid of the JSON object
                distance = np.sqrt((json_x - (x + w / 2)) ** 2 + (json_y - (y + h / 2)) ** 2)
                distances.append(distance)

                # if the closest match is None or the distance is smaller than the closest match, update the closest match
                if closest_match is None or distance < closest_match["distance"]:
                    closest_match = {"id": i, "distance": distance}
        
        # if here, no match was found, fetch details of closest match
        closest_match = json_data[closest_match["id"] - 1]

        # Print the closest match to the logger
        logger.info(f"Closest match: {closest_match}")
        return None


    @staticmethod
    def extract_segment(right_image, left_image, cX, cY):
        """
        Extract the image segment corresponding to the contour from both right and left images.
        """
        right_nodule_img = right_image[max(0, cY - 25):min(right_image.shape[0], cY + 25),
                          max(0, cX - 25):min(right_image.shape[1], cX + 25)]
        left_nodule_img = left_image[max(0, cY - 25):min(left_image.shape[0], cY + 25),
                         max(0, cX - 25):min(left_image.shape[1], cX + 25)]
        return right_nodule_img, left_nodule_img
    


    @staticmethod
    def process_image(image, output_dir, image_name, logger, json_data, matching, date_string):
        """
        Function to process an image, detect objects in the image, and segment the objects.
        """

        logger.info(f"\n@process_image: output_dir: {output_dir}, image_name: {image_name}, date_string: {date_string}")
        #logger.info(f"tracked_objects: {tracked_objects}")
        logger.info(f"{len(json_data)} json_data entries")
        logger.info(f"{len(matching)} matching entries")

        #logger.info(f"json_data: {json_data}")
        #logger.info(f"matching: {matching}")

        # Create folder to store 50x50 chopped images of nodules
        #nodules_dir = os.path.join(output_dir, 'nodules') 
        # when output_dir = 'output/crop1001/20230424', nodules_dir = 'output/crop1001/20230424/nodules' instead we want to use 'output/crop1001/nodules/20230424' 

        # get the 'output/crop1001' part of the output_dir
        crop_dir = os.path.dirname(output_dir) # 'output/crop1001'
        logger.info(f"crop_dir: {crop_dir}")
        # for the '20230424' part use date_string

        # create the nodules_dir
        nodules_dir = os.path.join(crop_dir, 'nodules') # 'output/crop1001/nodules'
        logger.info(f"nodules_dir: {nodules_dir}")

        # Split the image into left and right images
        mid_x = image.shape[1] // 2
        left_image = image[:, :mid_x]
        right_image = image[:, mid_x:]
        logger.info(f"Split image into left and right images: {left_image.shape}, {right_image.shape}")

        # Convert the right image to HSV and apply a mask to detect nodules
        hsv = cv2.cvtColor(right_image, cv2.COLOR_BGR2HSV)
        logger.info(f"Converted right image to HSV: {hsv.shape}")

        # Create a mask to detect nodules
        mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        logger.info(f"Created mask to detect nodules: {mask.shape}")

        # Optional: show mask to user
        # cv2.imshow("Mask", mask)
        # cv2.waitKey(0)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize the empty list of results
        results = []

        max_id = f"{date_string}_0"
        

        logger.info(f"\nFound {len(contours)} contours in mask, processing each contour...\n")
        # Process each contour
        for i, contour in enumerate(contours):

            date_component, id_component = max_id.split('_')

            # Extract date and id components from max_id string
            logger.info(f"max_id: {max_id}, i: {i}")
            # logger.info("Contour:")
            # logger.info(f"{contour}\n"

            
            # Find the moments of the contour
            # Moments are used to find the centroid of the contour, a moment is a weighted average of the image pixels
            M = cv2.moments(contour)
            logger.info(f"Moments: {M}")

            # If the area of the contour is 0, skip it
            if M["m00"] == 0:
                logger.info(f"Skipping contour#{i + 1} because area is 0.\n\n")
                continue
            
            # Find the centroid of the contour
            cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            logger.info(f"Centroid: {cX}, {cY}")

            # Calculate the bounding rectangle of the contour
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate the area of the contour
            area = cv2.contourArea(contour)

            cords = (cX, cY)

            # Print the results to the console
            logger.info(f"Processing contour#{i + 1}: area: {area} centroid: {cX}, {cY} rectangle: ({x}, {y}, {w}, {h})")
            
            # Find the matching contour in the JSON data 
            # NEEDS WORK

            matched_contour = ImageProcessor.find_dayJSON_match_for_contour(x, y, w, h, area, json_data, logger)

            # If a matching contour was found, use its ID, otherwise create a new ID
            if matched_contour is not None:
                logger.info(f"Match with input JSON(nodules) ID: {matched_contour['id']}")

            # If no matching contour was found, create a new ID
            else:
                
                logger.info(f"No input JSON(nodules) match, ID:{max_id} area: {area} position: {cords}")

            # Get the JSON entry corresponding to the matched contour
            logger.info(f"Matched contour: {matched_contour}")
            JSON_entry = matched_contour['id']-1 if matched_contour is not None else 'ERROR'


            entry_id = max_id
            match = []
            #look through the matching and find the corresponding entry, the set the entry_id to the 'name' in the matching entry in one line
            if matching is not None:
                for match_entry in matching:
                    first_id = match_entry['c']
                    second_id = match_entry['p']
                    name = match_entry['id']
                    
                    #logger.info(f"first_id: {first_id} second_id: {second_id} name: {name}")

                    if JSON_entry == first_id:
                        logger.info(f"Matched with first_id: {first_id} second_id: {second_id} name: {name}")

                        # Save the name of the matching entry [first_id, second_id, name]
                        match = [first_id, second_id, name]

                        entry_id = name
                        break


            #look through the matching and find the corresponding entry, the set the entry_id to the 'name' in the matching entry
            # for first_id, second_id, name in matching:
            #     logger.info(f"first_id: {first_id} second_id: {second_id} name: {name}")

            #     if JSON_entry == first_id:
            #         logger.info(f"Matched with {name}")
            #         entry_id = name
            #         break


            # Create a new entry for the results list 'm' is the matching entry in the matching list
            entry = {'id': entry_id, 'jsID': JSON_entry, 'c': cords, 'a': area, 'r': (x, y, w, h), 'e': matched_contour, 'm':match}

            # Add the entry to the results list
            results.append(entry)


            logger.info(f"entry_id:{entry_id}, entry saved to results list")

            # Nodule images will be saved to 'output/crop1001/nodules/{last_detected_string}/{entry_id_number_component}/current_date.jpg'

            # separate the date and number from the entry_id, entry_id = '20210401_0' -> date_component = '20210401', id_component = '0'

            # get the date_component
            entry_id_date_component = entry_id.split('_')[0]
            # get the id_component
            entry_id_number_component = entry_id.split('_')[1]

            
            #nodule_images_path = os.path.join(nodules_dir, entry_id) 
            #os.makedirs(nodule_images_path, exist_ok=True)
            # # instead of output/crop975/nodules/20230607_202 use output/crop975/nodules/20230607/202
            

            #make sure the 'ouput/crop1001/nodules/{last_detected_string}/{entry_id_number_component}' directory exists, otherwise create it
            formatted_entry_id_date_component = entry_id_date_component[0:4] + '-' + entry_id_date_component[4:6] + '-' + entry_id_date_component[6:8]
            last_detected_string = f"Last-Detected-{formatted_entry_id_date_component}"

            nodule_images_path = os.path.join(nodules_dir, last_detected_string, entry_id_number_component)
            os.makedirs(nodule_images_path, exist_ok=True)
            

            # convert date_string to format '20210401' to '2021-04-01'
            formated_date_string = date_string[0:4] + '-' + date_string[4:6] + '-' + date_string[6:8]

            # Extract the image segment corresponding to the contour from both right and left images
            right_nodule_img, left_nodule_img = ImageProcessor.extract_segment(right_image, left_image, cX, cY)

            right_nodule_image_file_name = f"{formated_date_string}_d.jpg" 
            right_nodule_image_file_path = os.path.join(nodule_images_path, right_nodule_image_file_name)

            cv2.imwrite(right_nodule_image_file_path, right_nodule_img)

            logger.info(f"Segmented nodule image saved as {right_nodule_image_file_path}")

            left_nodule_image_file_name = f"{formated_date_string}_o.jpg"
            left_nodule_image_file_path = os.path.join(nodule_images_path, left_nodule_image_file_name)

            cv2.imwrite(left_nodule_image_file_path, left_nodule_img)

            logger.info(f"Original nodule image saved as {left_nodule_image_file_path}")


            # Increment the id component
            id_component = int(id_component) + 1
            # Reconstruct the max_id string
            max_id = f"{date_component}_{id_component}"

            logger.info(f"\n")




        logger.info(f"Done analyzing contours, found {len(results)} nodules.\n\n")

        # Save the results to a JSON file
        json_file_name = os.path.join(output_dir, f'{image_name}.json')
        with open(json_file_name, 'w') as json_file:
            json.dump(results, json_file, indent=2)
        
        return image, json_file_name, results



```





```python
#logger.py
# logger.py
import logging
import os
class Logger:
    def __init__(self, log_name, output_dir, external_logger=None):

        if external_logger is not None:
            external_logger.info(f"Creating logger: {log_name}, {output_dir}, {external_logger}")

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        # create file handler which logs even info messages
        fh = logging.FileHandler(os.path.join(output_dir, log_name), 'w')

        fh.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger


```





```python
#HTML_out.py
import os
import shutil

#i made this to create a link to view the images in the browser, 
def generate_HTML_results_page(results, script_output_dir, logger):
    html_dir = os.path.join(script_output_dir, 'HTML')
    os.makedirs(html_dir, exist_ok=True)
    
    results_page_path = os.path.join(html_dir, 'results_page.html')
    
    with open(results_page_path, 'w') as results_page:
        results_page.write('<html>\n<body>\n<ul>\n')

        for files in results:
            for file in files:
                crop_number = file.split('/')[1].replace('crop', '')  # Extract crop number
                new_file_name = f"{crop_number}_{os.path.basename(file)}"
                destination = os.path.join(html_dir, new_file_name)
                
                # Copy file
                shutil.copy2(file, destination)
                
                # Generate link
                link = f"https://htmlpreview.github.io/?https://github.com/UMN-VR/FramingV2-DetectionV5-PreProcessor-Output/blob/main/HTML/{new_file_name}"
                
                # Write link to HTML file
                results_page.write(f'<li><a href="{link}">{new_file_name}</a></li>\n')

        results_page.write('</ul>\n</body>\n</html>')

    logger.info(f"Results page generated at {results_page_path}")

def generate_offline_HTML_results_page(results, script_output_dir, logger):
    html_dir = os.path.join(script_output_dir, 'HTML')
    os.makedirs(html_dir, exist_ok=True)
    
    results_page_path = os.path.join(html_dir, 'offline_results_page.html')
    
    with open(results_page_path, 'w') as results_page:
        results_page.write('<html>\n<body>\n<ul>\n')

        for files in results:
            for file in files:
                crop_number = file.split('/')[1].replace('crop', '')  # Extract crop number
                new_file_name = f"{crop_number}_{os.path.basename(file)}"
                destination = os.path.join(html_dir, new_file_name)
                
                # Copy file
                shutil.copy2(file, destination)
                
                # Generate link
                link = destination  # local path to the file
                
                # Write link to HTML file
                results_page.write(f'<li><a href="file://{link}">{new_file_name}</a></li>\n')

        results_page.write('</ul>\n</body>\n</html>')

    logger.info(f"Offline results page generated at {results_page_path}")


def generate_results_page(results, script_output_dir, logger):

    user_input = input("Generate Offline HTML Results Page? (y/n): ")
    if user_input.lower() != 'n':
        generate_offline_HTML_results_page(results, script_output_dir, logger)


    user_input = input("Generate Online HTML Results Page? (y/n): ")
    if user_input.lower() != 'n':
        generate_HTML_results_page(results, script_output_dir, logger)
   







```





```python
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




```





```python
#image_analysis.py
import os
import cv2
import json
import sys
import numpy as np

from logger import Logger
from html_generator import HtmlGenerator
from datetime import datetime

from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt
from skimage import io, filters, measure
from skimage.segmentation import clear_border
from skimage.color import label2rgb
from skimage.morphology import closing, square

from image_processing import ImageProcessor

import uuid

def normalize(arr):
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

class ImageAnalyzer:

    @staticmethod
    def extract_points_and_attributes(data):
        """Extract the points and their attributes from the data."""
        points = np.array([[point['x'], point['y']] for point in data])
        attributes = np.array([[point['d'], point['a'], point['p'], point['e']] for point in data])
        return points, attributes

    @staticmethod
    def normalize_attributes(attributes):
        """Normalize the attributes to have zero mean and unit variance."""
        attributes = (attributes - np.mean(attributes, axis=0)) / np.std(attributes, axis=0)
        return attributes

    @staticmethod
    def compute_distances(normalized_points, normalized_prev_points, attributes, attributes_prev):
        """Compute the spatial and attribute distances between all pairs of points."""
        spatial_distances = cdist(normalized_points, normalized_prev_points)
        attribute_distances = cdist(attributes, attributes_prev)
        return spatial_distances, attribute_distances

    @staticmethod
    def combine_distances(spatial_distances, attribute_distances, spatial_weight, attribute_weight):
        """Compute the combined distances."""
        combined_distances = spatial_weight * spatial_distances + attribute_weight * attribute_distances
        return combined_distances

    @staticmethod
    def find_matching(combined_distances, next_matching=None, current_date_string=None, scalar_distance_threshold=3):
        """Find the matching between the current and previous points.
        Returns: matching, unmatched_current, unmatched_previous, distance_threshold

            format of matching: [(i, j, ID), ...] where i is the index of the current point, j is the index of the previous point, and ID is the ID of the nodule
        
        """



        row_ind, col_ind = linear_sum_assignment(combined_distances)
        unmatched_current = set(range(combined_distances.shape[0])) - set(row_ind)
        unmatched_previous = set(range(combined_distances.shape[1])) - set(col_ind)

        distance_threshold = np.median(combined_distances[row_ind, col_ind]) * scalar_distance_threshold
        matching = []

        if next_matching is not None:
            #next_ids = {match[2] for match in next_matching}  # Extract IDs from next matching
            next_ids = {match_entry['id'] for match_entry in next_matching}
        else:
            next_ids = set()

        for idx, (i, j) in enumerate(zip(row_ind, col_ind)):
            if combined_distances[i, j] <= distance_threshold:
                # If the nodule was matched below the distance threshold, keep its ID from the next matching
                matched = [match_entry['id'] for match_entry in next_matching if match_entry['p'] == i] if next_matching is not None else []
                ID = matched[0] if matched else f"{current_date_string}_{len(matching)}"

                # give i name 'c' for current, and j name 'p' for previous
                match_entry = {'c': i, 'p': j, 'id': ID}
                matching.append(match_entry)


            else:
                # If the nodule was not matched below the distance threshold, create a new ID
                ID = f"{current_date_string}_{len(matching)}"
                # give i name 'c' for current, and j name 'p' for previous
                match_entry = {'c': i, 'p': j, 'id': ID}
                matching.append(match_entry)



        return matching, unmatched_current, unmatched_previous, distance_threshold


        
    @staticmethod
    def plot_data(logger, normalized_points, normalized_prev_points, current_points, prev_points, current_data, prev_data, matching, unmatched_current, unmatched_prev, combined_distances, distance_threshold, current_date_string, previous_date_string, filename):

        logger.info(f"@plot_data: normalized_points: {normalized_points.shape}, normalized_prev_points: {normalized_prev_points.shape}, current_points: {current_points.shape}, prev_points: {prev_points.shape}, current_data: {len(current_data)}, prev_data: {len(prev_data)}, matching: {len(matching)}, unmatched_current: {len(unmatched_current)}, unmatched_prev: {len(unmatched_prev)}, combined_distances: {combined_distances.shape}, distance_threshold: {distance_threshold}, current_date_string: {current_date_string}, previous_date_string: {previous_date_string}, filename: {filename}")

        """Plot the data with matching."""
        fig, ax = plt.subplots(1, 2, figsize=(10, 10))
        logger.info("Plots created")

        # Define colors
        colors = {
            'matched_current': 'red',
            'matched_previous': 'blue',
            'unmatched_current': '#ff9999',  # light red
            'unmatched_previous': '#9999ff',  # light blue
        }

        # Plot the normalized points
        ax[0].scatter(normalized_prev_points[:, 0], normalized_prev_points[:, 1], color='blue', label=previous_date_string, s=10)
        ax[0].scatter(normalized_points[:, 0], normalized_points[:, 1], color='red', label=current_date_string, s=10)
        ax[0].legend(loc='upper left')
        logger.info("Plotted the normalized points")

        logger.info("Drawing lines between the matched points")
        # Draw lines between the matched points
        for match_entry in matching:
            #logger.info(f"match_entry: {match_entry}")
            i = match_entry['c']
            j = match_entry['p']
            ID = match_entry['id']

            x1, y1 = normalized_prev_points[j]
            x2, y2 = normalized_points[i]
            distance = combined_distances[i, j]
            if distance > distance_threshold:
                # The point is considered matched, draw a line between the matched points
                ax[0].plot([x1, x2], [y1, y2], color='yellow', linewidth=2.0)
                # The point is considered unmatched, draw a yellow circle around it
                ax[0].add_patch(plt.Circle((x1, y1), 0.005, color='yellow', fill=False))
                ax[0].add_patch(plt.Circle((x2, y2), 0.005, color='yellow', fill=False))
                # print IDs of matched points
                color = colors['unmatched_previous']
                ax[0].text(x1, y1, str(j), fontsize=8, color=color)
                color = colors['unmatched_current']
                ax[0].text(x2, y2, str(i), fontsize=8, color=color)

            else:
                # The point is considered matched, draw a line between the matched points
                ax[0].plot([x1, x2], [y1, y2], color='green', linewidth=2.0)
                # print IDs of matched points
                ax[0].text(x1, y1, str(j), fontsize=8, color='blue')
                ax[0].text(x2, y2, str(i), fontsize=8, color='red')
        
        # Plot the unmatched points
        logger.info("Plotting the unmatched points")
        for i in unmatched_prev:
            x, y = normalized_prev_points[i]
            color = colors['unmatched_current']
            ax[0].add_patch(plt.Circle((x, y), 0.005, color=color, fill=False))
        
        for i in unmatched_current:
            x, y = normalized_points[i]
            color = colors['unmatched_previous']
            ax[0].add_patch(plt.Circle((x, y), 0.005, color=color, fill=False))


        ax[0].set_aspect('equal')  # Ensures circles, not ovals, are plotted
        ax[0].invert_yaxis()  # Flip the y-axis

        # Plot the original points with diameter as size
        for i, point in enumerate(current_data):
            #match = any(i == pair[0] for pair in matching)
            match = any(i == match_entry['c'] for match_entry in matching)

            color = colors['matched_current'] if match else colors['unmatched_current']
            color2 = colors['matched_current'] if match else colors['unmatched_previous']
            ax[1].scatter(point['x'], point['y'], color=color, s=10)
            ax[1].add_patch(plt.Circle((point['x'], point['y']), point['d'], color=color2, fill=False))
        for i, point in enumerate(prev_data):
            #match = any(i == pair[1] for pair in matching)
            match = any(i == match_entry['p'] for match_entry in matching)
            color = colors['matched_previous'] if match else colors['unmatched_previous']
            color2 = colors['matched_previous'] if match else colors['unmatched_current']
            ax[1].scatter(point['x'], point['y'], color=color, s=10)
            ax[1].add_patch(plt.Circle((point['x'], point['y']), point['d'], color=color2, fill=False))
        
        logger.info("Plotted the original points with diameter as size")

        ax[1].set_aspect('equal')  # Ensures circles, not ovals, are plotted
        ax[1].invert_yaxis()  # Flip the y-axis

        # Draw lines between the matched points and add the indices to the plots with color coding
        logger.info("Drawing lines between the matched points and add the indices to the plots with color coding")
        for match_entry in matching:
            i = match_entry['c']
            j = match_entry['p']
            distance = combined_distances[i, j]
            if distance > distance_threshold:
                # The point is considered unmatched, draw a yellow circle around it
                ax[1].add_patch(plt.Circle((current_data[i]['x'], current_data[i]['y']), 2 * current_data[i]['d'], color='yellow', fill=False, zorder=3))
                ax[1].add_patch(plt.Circle((prev_data[j]['x'], prev_data[j]['y']), 2 * prev_data[j]['d'], color='yellow', fill=False, zorder=3))
                ax[1].text(current_data[i]['x'], current_data[i]['y'], str(i), fontsize=8, color=colors['unmatched_current'])
                ax[1].text(prev_data[j]['x'], prev_data[j]['y'], str(j), fontsize=8, color=colors['unmatched_previous'])
            else:
                # The point is considered matched, draw a line between the matched points
                ax[1].plot([current_data[i]['x'], prev_data[j]['x']], [current_data[i]['y'], prev_data[j]['y']], color='green', linewidth=2.0, zorder=3)
                ax[1].text(current_data[i]['x'], current_data[i]['y'], str(i), fontsize=8, color=colors['matched_current'])
                ax[1].text(prev_data[j]['x'], prev_data[j]['y'], str(j), fontsize=8, color=colors['matched_previous'])


        # set the titles
        ax[0].set_title('Normalized')
        ax[1].set_title('Yellow = above threshold, ring = unmatched')

        #set the labels
        ax[0].set_xlabel('X Normalized')
        ax[0].set_ylabel('Y Normalized')

        ax[1].set_xlabel('X')
        ax[1].set_ylabel('Y')

        logger.info("Setting the titles and labels")

        logger.info("Done plotting")

        # Save the plot
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()








    @staticmethod
    def load_image(file_name):
        """
        Load image from the file.
        """
        image = cv2.imread(file_name)
        if image is None:
            print(f'Unable to load image file: {file_name}!')
            sys.exit(1)
        return image

    @staticmethod
    def load_json(file_name):
        """
        Load JSON data from the file.
        """
        json_file_name = os.path.splitext(file_name)[0] + '.json'
        with open(json_file_name, 'r') as json_file:
            json_data = json.load(json_file)
        if json_data is None:
            print(f'Unable to load JSON file: {json_file_name}!')
            sys.exit(1)
        return json_data

    @staticmethod
    def scale_json(json_data, scalar_position=0.5, scalar_size=0.5):
        """
        Scale the coordinates of the JSON data.
        """

        for json_obj in json_data:
            json_obj["x"] = int(json_obj["x"] * scalar_position)
            json_obj["y"] = int(json_obj["y"] * scalar_position)
            json_obj["d"] = int(json_obj["d"] * scalar_size)
        return json_data

    @staticmethod
    def generate_HTML_file(image, results, prev_results, next_results, image_output_dir, base_name, logger, json_data):
        """
        Store processed results to HTML and modified image file.
        """

        # Directory to store the modified image file
        modified_image_file = os.path.join(image_output_dir, f"{base_name}_rectangles.jpg")

        # for result in results:
        #     x, y, w, h = result['rect_coords']
        #     #logger.info(f"ID: {result['id']}, Location: {result['position']}, Size: {result['size']}")

        #save the image with the rectangles drawn on it
        cv2.imwrite(modified_image_file, image)
        logger.info(f"Modified image saved as: {modified_image_file}")

        result_file_name = os.path.join(image_output_dir, f"{base_name}_result.html")

        # Create an instance of HtmlGenerator
        html_generator = HtmlGenerator(logger)

        logger.info(f"Generating HTML with:")

        logger.info(f"modified_image_file: {modified_image_file}")
        logger.info(f"result_file_name: {result_file_name}")
        #logger.info(f"results: {results}")
        #logger.info(f"prev_results: {prev_results}")
        #logger.info(f"next_results: {next_results}")
        #logger.info(f"json_data: {json_data}")


        html_generator.generate_html(modified_image_file, result_file_name, results, prev_results, next_results, json_data)

        cv2.destroyAllWindows()
        logger.info(f"Finished analyzing image: {base_name}")
        return result_file_name
    
    @staticmethod
    def find_prev_next_date(image_output_dir, logger):
        logger.info(f"\n@find_prev_next_date: image_output_dir: {image_output_dir}")
        
        # get the crop number from the image output directory
        crop_number = os.path.dirname(image_output_dir).split('/')[-1]
        # construct the data directory path
        data_dir = os.path.join('data', crop_number)
        logger.info(f"data_dir: {data_dir}")
        
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









    @staticmethod
    def analyze_image(file_name, output_dir, next_matching=None, external_logger=None):
        """
        This function processes an image and saves the results to a new directory named after the base name of the image file in the specified output directory.
        """

        external_logger.info(f"\n@analyze_image: file_name: {file_name}, output_dir: {output_dir}, external_logger: {external_logger}")
        #external_logger.info(f"objects: {objects}")
        external_logger.info(f"next_matching: {next_matching}")

        # Get the base name of the image file
        current_date = os.path.basename(file_name).split('.')[0]
        #crop_number = os.path.basename(os.path.dirname(os.path.dirname(file_name))) # BAD crop_number: data when file_name: data/crop980/20230605.jpg it should be crop980
        crop_number = os.path.basename(os.path.dirname(file_name)) # GOOD crop_number: crop980 when file_name: data/crop980/20230605.jpg

        external_logger.info(f"current_date: {current_date}, crop_number: {crop_number}")

        # Create a directory for the image
        image_output_dir = os.path.join(output_dir, current_date)
        external_logger.info(f"image_output_dir: {image_output_dir}")

        # Create the directory if it doesn't exist
        os.makedirs(image_output_dir, exist_ok=True)


        # Create a logger for this image
        log_name = f"{crop_number}_{current_date}.log"
        external_logger.info(f"log_name: {log_name}")

        # determine the path of the log file and print it to the console
        log_dir = os.path.join(image_output_dir, log_name)

        print(f"Starting log at: {log_dir}")

        # Use crop_number in logger name
        logger = Logger(log_name, image_output_dir, external_logger=external_logger).get_logger()
        logger.propagate = False
 
        logger.info(f"@analyze_image: file_name: {file_name}, output_dir: {output_dir}, external_logger: {external_logger}")

        #load files
        image = ImageAnalyzer.load_image(file_name)
        json_data = ImageAnalyzer.load_json(file_name)

        if json_data is None:
            print(f"Unable to open JSON file: {file_name}")
            sys.exit(1)
        
        logger.info(f"Loaded image & JSON file: {file_name}")

        scalar_position = 0.5
        scalar_size = 0.5
        # scale X,Y coordinates of JSON data
        json_data_scaled = ImageAnalyzer.scale_json(json_data, scalar_position=scalar_size, scalar_size=scalar_size)
        logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")

        if image is None:
            print(f"Unable to open image file: {file_name}")
            sys.exit(1)
        
        prev_date = None
        next_date = None

        #Find the previous & next date 
        prev_date, next_date = ImageAnalyzer.find_prev_next_date(image_output_dir, logger)

        prev_results = []
        next_results = []

        if prev_date is not None:
            # get previous date string
            previous_date_string = os.path.basename(prev_date).split('.')[0]

            prev_results = ImageAnalyzer.load_json(prev_date)
            if prev_results is None:
                logger.info(f"Unable to open JSON file: {prev_date}")
                sys.exit(1)

            logger.info(f"Loaded prev_results from JSON file: {previous_date_string}, length: {len(prev_results)}")
            # scale X,Y coordinates of JSON data
            prev_results = ImageAnalyzer.scale_json(prev_results, scalar_position=scalar_position, scalar_size=scalar_size)
            logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")

        if next_date is not None:
            # get next date string
            next_date_string = os.path.basename(next_date).split('.')[0]

        
            next_results = ImageAnalyzer.load_json(next_date)
            if next_results is None:
                logger.info(f"Unable to open JSON file: {next_date}")
                sys.exit(1)

            logger.info(f"Loaded next_results from JSON file: {next_date_string}, length: {len(next_results)}")
            # scale X,Y coordinates of JSON data
            next_results = ImageAnalyzer.scale_json(next_results, scalar_position=scalar_position, scalar_size=scalar_size)
            logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")


        

        if prev_results:

            logger.info(f"prev_results is not empty, generating matching")

            matching_name = f"{previous_date_string}_{current_date}_matching.json"

            logger.info(f"current_date:{current_date}, generating Matching: {matching_name}")

            # Extract the points and attributes
            points, attributes = ImageAnalyzer.extract_points_and_attributes(json_data)
            prev_points, prev_attributes = ImageAnalyzer.extract_points_and_attributes(prev_results)

            # Normalize the attributes
            attributes = ImageAnalyzer.normalize_attributes(attributes)
            prev_attributes = ImageAnalyzer.normalize_attributes(prev_attributes)

            # Compute the distances
            spatial_distances, attribute_distances = ImageAnalyzer.compute_distances(points, prev_points, attributes, prev_attributes)

            logger.info(f"spatial_distances: {spatial_distances.shape}, attribute_distances: {attribute_distances.shape}")

            # Combine the distances
            combined_distances = ImageAnalyzer.combine_distances(spatial_distances, attribute_distances, spatial_weight=0.7, attribute_weight=0.3)

            logger.info(f"combined_distances: {combined_distances.shape}")

            # Find the matching
            matching, unmatched_current, unmatched_previous, distance_threshold = ImageAnalyzer.find_matching(combined_distances, next_matching, current_date_string=current_date, scalar_distance_threshold=3)
            logger.info(f"Matching length: {len(matching)}")
            logger.info(f"Matching: {matching}")
            logger.info(f"Unmatched current: {len(unmatched_current)}: {unmatched_current}")
            logger.info(f"Unmatched previous {len(unmatched_previous)}: {unmatched_previous}")
            logger.info(f"Distance threshold: {distance_threshold}\n\n")

            # Create plots
            #plot_file_name = os.path.join(image_output_dir, f"{current_date}_plot.png")
            # remove the last /stuff from the image_output_dir
            plot_file_name = os.path.join(image_output_dir.replace(f"/{current_date}", ""), f"{previous_date_string}_{current_date}_plot.png")

            normalized_points = normalize(points)
            normalized_prev_points = normalize(prev_points)

            # Plot the data
            ImageAnalyzer.plot_data(logger,
                                    normalized_points, normalized_prev_points, 
                                    points, prev_points, current_data=json_data, prev_data=prev_results, 
                                    matching=matching, unmatched_current=unmatched_current, unmatched_prev=unmatched_previous, 
                                    combined_distances=combined_distances, distance_threshold=distance_threshold, filename=plot_file_name,
                                    current_date_string=current_date, previous_date_string=previous_date_string)
            
            # Convert matching indices to native int before saving
            #matching = [(int(i), int(j), match_id) for i, j, match_id in matching
            for match_entry in matching:
                match_entry['c'] = int(match_entry['c'])
                match_entry['p'] = int(match_entry['p'])



            # save the matching to a file
            #matching_file_name = os.path.join(image_output_dir, f"{current_date}_matching.json")
            # remove the last /stuff from the image_output_dir
            # matching_file_name = os.path.join(image_output_dir.replace(f"/{current_date}", ""), matching_name)

            # with open(matching_file_name, 'w') as matching_file:
            #     json.dump(matching, matching_file)
            
            # logger.info(f"Matching saved as: {matching_file_name}")
        
        else:
            matching = []

        # Process the image
                    
        image, results_file_name, result_data = ImageProcessor.process_image(image, image_output_dir, current_date, logger, json_data_scaled, matching, date_string=current_date)


        HTML_file_name = ImageAnalyzer.generate_HTML_file(image, result_data, prev_results, next_results, image_output_dir, current_date, logger, json_data_scaled)

        results_entry = {"crop": crop_number, "date": current_date, "results": results_file_name, "html": HTML_file_name}


        return results_entry, matching






```





```python
#html_generator.py
# File: html_generator.py
import base64
import cv2
from jinja2 import Environment, FileSystemLoader
from logger import Logger

class HtmlGenerator:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.env = Environment(loader=FileSystemLoader('templates'))

    def _encode_image(self, image_file: str) -> str:
        """Read the image file and encode it."""
        with open(image_file, "rb") as file:
            image_data = file.read()
            self.logger.info("Image file read successfully.")
        encoded_image = base64.b64encode(image_data).decode()
        self.logger.info("Image file encoded successfully.")
        return encoded_image

    def fetch_image_dims(self, image_file: str) -> tuple:
        """Get the image dimensions."""
        image = cv2.imread(image_file)
        image_height, image_width, _ = image.shape
        self.logger.info("Image dimensions fetched.")
        return image_height, image_width

    def generate_html(self, image_file: str, output_file: str, results: list, prev_data: list, next_data: list,  json_data: list, scalar_position=1, scalar_size=1, transparency=0.25):
        """Generate an HTML file to visualize the image analysis results."""
        self.logger.info("Starting to generate HTML...")
        encoded_image = self._encode_image(image_file)
        image_height, image_width = self.fetch_image_dims(image_file)

        # Get the HTML template
        html_template = self.env.get_template('visualizer.html')

        html_content = html_template.render(
            encoded_image=encoded_image,
            results=results, 
            prev_data=prev_data, next_data=next_data,
            json_data=json_data, 
            image_height=image_height, image_width=image_width,
            scalar_position=scalar_position, scalar_size=scalar_size, 
            transparency=transparency
        )

        # Save the HTML content to the output file
        with open(output_file, "w") as html_file:
            html_file.write(html_content)
        self.logger.info(f"HTML file saved as {output_file}")

        self.logger.info("HTML file generated successfully.")



```





```python
#main.py
# main.py
# Import required libraries

import os
import cv2
import json
import sys
import subprocess
from image_analysis import ImageAnalyzer
from logger import Logger

# Import the get_all_image_files function from nodules.py
from nodules import get_all_image_files, find_crop_folders, load_image, process_crop_folder

from HTML_out import generate_results_page




def main():
    # Change the working directory to the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__)) # get the path of this script, log will be saved here
    os.chdir(script_dir) # change the working directory to the directory of of this script
    
    # Check if the output directory exists, if not make one
    if not os.path.isdir("output"):
        os.makedirs("output")
    else:
        # ask the user if they want to clear the output directory
        print("It is recommended to clear the output directory before running this script.")
        user_input = input("Would you like to clear the output directory? (y/n): ")
        if not user_input.lower() == 'n':
            # delete the output directory
            print("Clearing output directory...")
            os.system("rm -rf output")
            os.makedirs("output")

    # Main Loop: process images until the user enters 'exit'
    while True:
        # ask user for file name or directory
        file_name = input("Enter the file name (or 'exit' to stop): ")
        # if the user enters 'exit', stop the program
        if file_name.lower() == 'exit':
            break
            
        # remove the extension
        log_name, _ = os.path.splitext(file_name)
        # replace / with _ and capitalize the result
        log_name = log_name.replace('/', '_')
        # creates the logger in /output
        logger = Logger(f'{log_name}.log', "output").get_logger()
        # Initialize the results list
        results = []
        # if the user enters a directory, process all the images in the directory
        if os.path.isdir(file_name):
            logger.info(f"Detected directory: {file_name}")
            # get all the files in the directory and its subdirectories
            files = get_all_image_files(file_name)
            # now we have a list of image files
            logger.info(f"Found {len(files)} image files in directory: {file_name}")
            
            logger.info(f"{files}")  # prints all files found in directory
            print(f"Found {len(files)} image files in directory: {file_name}")
            # Tell user where the files will be written
            script_output_dir = os.path.join("output", file_name.replace("data", "").strip("/"))
            print(f"Will write files to directory: {script_output_dir}")
            
            # if the user typed 'data' then there are multiple crop folders 
            # for each crop folder that will be created a separate log file will be created, and an empty list of objects will be created
            crop_folders = find_crop_folders(file_name)    
            print(f"Found {len(crop_folders)} crop folders: {crop_folders}")
            
            # ask the user to continue
            continue_processing = input("Continue processing? (y/n): ")
            if continue_processing.lower() == 'n':
                logger.info("User chose to stop processing images")
                break
            
            logger.info("User chose to continue processing images")
            for crop_folder in crop_folders:
                logger.info(f"Processing crop folder: {crop_folder}")
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
                logger.info("User chose to generate results")

                
                generate_results_page(results, script_output_dir, logger)
        


            # Open the last HTML file generated
            if results and results[-1]:
                subprocess.run(["xdg-open", results[-1][-1]], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null
                
        # if the user enters a file name, process that file
        elif os.path.isfile(file_name):
            # get the directory where the results will be saved
            output_dir = os.path.join("output", os.path.dirname(file_name).replace("data", "").strip("/"))
            # Call analyze_image() to process the image, this is where the magic happens
            result_file_name, new_objects = ImageAnalyzer.analyze_image(file_name, output_dir, external_logger=logger)
            # Open the HTML file generated
            subprocess.run(["xdg-open", result_file_name], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null
        else:
            print("Invalid file name or directory.")
            logger.error(f"Invalid file name or directory: {file_name}")
            continue

        # Print Done! to the console and a line 
        print("--------------------------------------------------")
        print("Done!")
    
    print("Exiting program...")
if __name__ == '__main__':
    main()



```