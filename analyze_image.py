import os 
import sys
from Logger import Logger
from memory_logger import log_memory_usage
from cv_utils import load_image
from image_analysis import ImageAnalyzer, normalize
from image_processing import ImageProcessor
from json_utils import load_json, scale_json
from plot_p_transition import plot_p_transition
from find_prev_next_date_paths import find_prev_next_date_paths
from find_matching import find_matching
from generate_HTML_file import generate_HTML_file
from process_image import process_image


def analyze_image(image_file_name, output_dir, next_matching=None, external_logger=None):
    """
    This function processes an image and saves the results to a new directory named after the base name of the image file in the specified output directory.
    """

    external_logger.info(f"\n@analyze_image: file_name: {image_file_name}, output_dir: {output_dir}, external_logger: {external_logger}")
    #external_logger.info(f"objects: {objects}")
    #external_logger.info(f"next_matching: {next_matching}")

    # Get the base name of the image file 
    current_date = os.path.basename(image_file_name).split('.')[0]
    #crop_number = os.path.basename(os.path.dirname(os.path.dirname(file_name))) # BAD crop_number: data when file_name: data/crop980/20230605.jpg it should be crop980
    crop_number = os.path.basename(os.path.dirname(image_file_name)) # GOOD crop_number: crop980 when file_name: data/crop980/20230605.jpg

    external_logger.info(f"current_date: {current_date}, crop_number: {crop_number}")

    # Create a directory for the image
    image_output_dir = os.path.join(output_dir, current_date)
    external_logger.info(f"image_output_dir: {image_output_dir}")

    # Create the directory if it doesn't exist
    os.makedirs(image_output_dir, exist_ok=True)


    # Create a logger for this image
    log_name = f"{crop_number}_{current_date}.log"
    

    # determine the path of the log file and print it to the console
    log_dir = os.path.join(image_output_dir, log_name)

    

    # Use crop_number in logger name

    print(f"Starting log at: {log_dir} with log_name: {log_name}")

    external_logger.info(f"Starting log at: {log_dir}")

    logger = Logger(log_name, image_output_dir, external_logger=external_logger).get_logger()

    log_dir = image_output_dir+"/"+log_name

    logger.propagate = False

    log_memory_usage(logger)
    logger.info(f"@analyze_image: file_name: {image_file_name}, output_dir: {output_dir}, external_logger: {external_logger}")

    #load files
    image = load_image(image_file_name)
    json_data = load_json(image_file_name)

    if json_data is None:
        print(f"Unable to open JSON file: {image_file_name}")
        sys.exit(1)
    
    logger.info(f"Loaded image & JSON file: {image_file_name}")

    scalar_position = 0.5
    scalar_size = 0.5
    # scale X,Y coordinates of JSON data
    json_data_scaled = scale_json(json_data, scalar_position=scalar_size, scalar_size=scalar_size)
    logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")

    if image is None:
        print(f"Unable to open image file: {image_file_name}")
        sys.exit(1)
    
    prev_date = None
    next_date = None

    #Find the previous & next date 
    prev_date, next_date = find_prev_next_date_paths(image_output_dir, logger)

    json_prev = []
    next_results = []

    prev_date_string = None
    next_date_string = None

    match_stats = {}

    plot_file_name = None

    if prev_date is not None:
        # get previous date string
        prev_date_string = os.path.basename(prev_date).split('.')[0]

        json_prev = load_json(prev_date)
        if json_prev is None:
            logger.info(f"Unable to open JSON file: {prev_date}")
            sys.exit(1)

        logger.info(f"Loaded prev_results from JSON file: {prev_date_string}, length: {len(json_prev)}")
        # scale X,Y coordinates of JSON data
        json_prev = scale_json(json_prev, scalar_position=scalar_position, scalar_size=scalar_size)
        logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")

    if next_date is not None:
        # get next date string
        next_date_string = os.path.basename(next_date).split('.')[0]

    
        next_results = load_json(next_date)
        if next_results is None:
            logger.info(f"Unable to open JSON file: {next_date}")
            sys.exit(1)

        logger.info(f"Loaded next_results from JSON file: {next_date_string}, length: {len(next_results)}")
        # scale X,Y coordinates of JSON data
        next_results = scale_json(next_results, scalar_position=scalar_position, scalar_size=scalar_size)
        logger.info(f"Scaled JSON data: scalar_position: {scalar_position}, scalar_size: {scalar_size}")


    

    if json_prev:

        logger.info(f"prev_results is not empty, generating matching")
        log_memory_usage(logger)

        matching_name = f"{prev_date_string}_{current_date}_matching.json"

        logger.info(f"current_date:{current_date}, generating Matching: {matching_name}")

        # Extract the points and attributes
        points, attributes = ImageAnalyzer.extract_points_and_attributes(json_data)
        prev_points, prev_attributes = ImageAnalyzer.extract_points_and_attributes(json_prev)

        # Compute the distances
        spatial_distances, attribute_distances = ImageAnalyzer.compute_distances(points, prev_points, attributes, prev_attributes)

        logger.info(f"spatial_distances: {spatial_distances.shape}, attribute_distances: {attribute_distances.shape}")

        # Combine the distances
        combined_distances = ImageAnalyzer.combine_distances(spatial_distances, attribute_distances, spatial_weight=0.7, attribute_weight=0.3)

        logger.info(f"combined_distances: {combined_distances.shape}")

        log_memory_usage(logger)

        # Find the matching
        matching, unmatched_current, unmatched_previous, match_stats = find_matching(logger, combined_distances, crop_folder=crop_number, next_matching=next_matching, current_date_string=current_date, current_json=json_data, prev_json=json_prev, next_json=next_results)

        plot_file_name = os.path.join(image_output_dir.replace(f"/{current_date}", ""), "plots")

        # Create the directory if it doesn't exist
        os.makedirs(plot_file_name, exist_ok=True)

        plot_file_name = os.path.join(plot_file_name, f"{prev_date_string}_{current_date}.png")

        normalized_points = normalize(points)
        normalized_prev_points = normalize(prev_points)

        # Plot the data
        plot_p_transition(logger,
            normalized_points, normalized_prev_points, 
            points, prev_points, current_data=json_data, prev_data=json_prev, 
            matching=matching, unmatched_current=unmatched_current, unmatched_prev=unmatched_previous, 
            combined_distances=combined_distances, distance_threshold=match_stats['distance_threshold'], filename=plot_file_name,
            current_date_string=current_date, previous_date_string=prev_date_string)

        # Convert matching indices to native int before saving
        #matching = [(int(i), int(j), match_id) for i, j, match_id in matching
        for match_entry in matching:
            match_entry['c']['id'] = int(match_entry['c']['id'])
            match_entry['p']['id'] = int(match_entry['p']['id'])



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
                
    current_json = process_image(image, image_output_dir, current_date, logger, json_data_scaled, matching, date_string=current_date)


    #HTML_file_name = generate_HTML_file(image, prev_date_string, current_json, next_date_string, image_output_dir, current_date, logger)


    results_entry = {"date": current_date,
                        "json": current_json, "log": log_dir, "image": image_file_name, "plot": plot_file_name,
                        "match_stats": match_stats
                    }

    logger.info(f"results_entry: {results_entry}")


    return results_entry, matching



