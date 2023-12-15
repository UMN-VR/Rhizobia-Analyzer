import json
import os
import logging

def prep_nodules(nodules_data, logger):
    """
    Aggregate nodules by ID and organize data by date, and count the number of unique dates for each nodule.
    Args:
        nodules_data (list): List of nodules data, each with date and nodules info.
        logger (logging.Logger): Logger for logging information and errors.
    Returns:
        list: List of aggregated nodules data.
    """
    # Dictionary to hold aggregated nodules
    aggregated_nodules = {}

    for entry in nodules_data:
        # Extract the date and format it to YYYY-MM-DD
        date = entry['date']
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        # Process each nodule in the entry
        for nodule in entry['nodules']:
            # Each nodule is a dictionary with a single key-value pair
            for nodule_id, nodule_data in nodule.items():
                # If the nodule ID is not in the aggregated list, add it
                if nodule_id not in aggregated_nodules:
                    aggregated_nodules[nodule_id] = {}

                # Add/update the nodule data under the formatted date
                aggregated_nodules[nodule_id][formatted_date] = nodule_data

    # Calculate the number of unique dates for each nodule and prepare the final list
    formatted_nodules = []
    for nodule_id, dates in aggregated_nodules.items():
        nodule_entry = {"id": nodule_id, "num_detections": len(dates), **dates}
        formatted_nodules.append(nodule_entry)

    return formatted_nodules



# Testing the function with a sample file
def test_prep_nodules(logger, file_path):
    """
    Test the prep_nodules function with a given file path.

    Args:
        logger (logging.Logger): Logger for logging information and errors.
        file_path (str): Path to the nodules JSON file.
    """

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    # Load the nodules data from the file
    try:
        with open(file_path, 'r') as file:
            nodules_data = json.load(file)
        logger.info("Nodules data loaded successfully.")

    except json.JSONDecodeError as e:
        logger.error(f"Error in JSON decoding: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return

    # Process the data
    aggregated_nodules = prep_nodules(nodules_data, logger)
    logger.info("Nodules data processed successfully.")

    # Logging the results for review
    #logger.info(f"Aggregated Nodules: {aggregated_nodules}")

    # Save the results to a file
    try:
        aggregated_nodules_path = file_path.replace('.json', '_aggregated.json')
        with open(aggregated_nodules_path, 'w') as file:
            json.dump(aggregated_nodules, file, indent=1)
        logger.info("Aggregated nodules saved successfully.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return

if __name__ == "__main__":
    # Setting up logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    # Test file path (Windows path format)
    test_file_path = r'output\\crop1000\\crop1000_nodules.json'

    # Run the test
    test_prep_nodules(logger, test_file_path)
