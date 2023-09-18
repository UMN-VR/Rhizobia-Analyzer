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

from memory_logger import log_memory_usage

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
    def find_matching(logger, combined_distances, next_matching=None, current_date_string=None, scalar_distance_threshold=3):
        """Find the matching between the current and previous points.
        Returns: matching, unmatched_current, unmatched_previous, distance_threshold

            format of matching: [(i, j, ID), ...] where i is the index of the current point, j is the index of the previous point, and ID is the ID of the nodule
        
        """

        logger.info(f"\n@find_matching: combined_distances: {combined_distances.shape}, next_matching: {next_matching}, current_date_string: {current_date_string}, scalar_distance_threshold: {scalar_distance_threshold}")

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

        for idx, (ix, jx) in enumerate(zip(row_ind, col_ind)):

            match = None

            id = f"{current_date_string}_{len(matching)}"
            i = 0

            if combined_distances[ix, jx] <= distance_threshold:

                if next_matching is not None:
                    for match_entry in next_matching:
                        if match_entry['p'] == ix:
                            match = match_entry
                            id = match["id"]
                            i = match["i"] + 1

                            # If the nodule was matched below the distance threshold, keep its ID from the next matching
                            logger.info(f"matched: {match}, current_date_string: {current_date_string}, len(matching): {len(matching)}")
                            break


                

            # give i name 'c' for current, and j name 'p' for previous
            match_entry = {'id': id, 'c': ix, 'p': jx, 'i':i}
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
    def generate_HTML_file(image, prev_data, json_data, next_data, image_output_dir, base_name, logger):
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
        logger.info(f"prev_data: {prev_data}")
        logger.info(f"json_data: {json_data}")
        logger.info(f"next_data: {next_data}")


        html_generator.generate_html(modified_image_file, result_file_name, prev_data, json_data, next_data)

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
 
        log_memory_usage(logger)
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

        prev_date_string = None
        next_date_string = None

        if prev_date is not None:
            # get previous date string
            prev_date_string = os.path.basename(prev_date).split('.')[0]

            prev_results = ImageAnalyzer.load_json(prev_date)
            if prev_results is None:
                logger.info(f"Unable to open JSON file: {prev_date}")
                sys.exit(1)

            logger.info(f"Loaded prev_results from JSON file: {prev_date_string}, length: {len(prev_results)}")
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
            log_memory_usage(logger)

            matching_name = f"{prev_date_string}_{current_date}_matching.json"

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

            log_memory_usage(logger)

            # Find the matching
            matching, unmatched_current, unmatched_previous, distance_threshold = ImageAnalyzer.find_matching(logger, combined_distances, next_matching, current_date_string=current_date, scalar_distance_threshold=3)
            logger.info(f"Matching length: {len(matching)}")
            logger.info(f"Matching: {matching}")
            logger.info(f"Unmatched current: {len(unmatched_current)}: {unmatched_current}")
            logger.info(f"Unmatched previous {len(unmatched_previous)}: {unmatched_previous}")
            logger.info(f"Distance threshold: {distance_threshold}\n\n")

            # Create plots
            #plot_file_name = os.path.join(image_output_dir, f"{current_date}_plot.png")
            # remove the last /stuff from the image_output_dir
            plot_file_name = os.path.join(image_output_dir.replace(f"/{current_date}", ""), f"{prev_date_string}_{current_date}_plot.png")

            normalized_points = normalize(points)
            normalized_prev_points = normalize(prev_points)

            # Plot the data
            ImageAnalyzer.plot_data(logger,
                                    normalized_points, normalized_prev_points, 
                                    points, prev_points, current_data=json_data, prev_data=prev_results, 
                                    matching=matching, unmatched_current=unmatched_current, unmatched_prev=unmatched_previous, 
                                    combined_distances=combined_distances, distance_threshold=distance_threshold, filename=plot_file_name,
                                    current_date_string=current_date, previous_date_string=prev_date_string)
            
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


        HTML_file_name = ImageAnalyzer.generate_HTML_file(image, prev_date_string, results_file_name, next_date_string, image_output_dir, current_date, logger)

        results_entry = {"crop": crop_number, "date": current_date, "results": results_file_name, "html": HTML_file_name}


        return results_entry, matching



