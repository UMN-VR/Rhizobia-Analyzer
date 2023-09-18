# nodule_analysis.py
import json
import os
from Logger import Logger
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
