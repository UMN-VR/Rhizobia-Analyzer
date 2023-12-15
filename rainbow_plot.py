import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from datetime import datetime
import numpy as np
import logging
import os
import subprocess

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def hex_to_rgb(hex_color):
    """ Convert hex color to normalized RGB tuple. """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def make_rainbow_plot(data, ax, ignore_single_entry=True):
    """
    Create a rainbow plot on the given Axes object.

    Args:
        data (list): List of nodules data.
        ax (matplotlib.axes.Axes): Axes object to plot on.
        ignore_single_entry (bool): Flag to ignore nodules with only one entry.
    """
    all_dates = set()  # Collect all unique dates
    nodule_data_grouped = {}  # Group data by nodule ID

    for nodule in data:
        nodule_id = nodule['id']
        for date_str, details in nodule.items():
            if '-' in date_str:
                all_dates.add(date_str)
                if nodule_id not in nodule_data_grouped:
                    nodule_data_grouped[nodule_id] = {}
                nodule_data_grouped[nodule_id][date_str] = details

    sorted_dates = sorted(list(all_dates))

    for nodule_id, dates_details in nodule_data_grouped.items():
        if ignore_single_entry and len(dates_details) <= 1:
            continue  # Skip nodules with only one entry

        valid_dates = [date for date in sorted_dates if date in dates_details]
        valid_areas = [dates_details[date]['a'] for date in valid_dates]
        color = hex_to_rgb(next(iter(dates_details.values()))['rgb_r']) if dates_details else (0, 0, 0)
        linewidth = max(0.25, len(valid_dates) / 8)  # Thinner lines

        # Plotting the nodule line
        ax.plot([datetime.strptime(date, '%Y-%m-%d') for date in valid_dates], valid_areas, linestyle='solid', marker=None, color=color, linewidth=linewidth)

        # Adding circles at start and end points of valid data
        if valid_dates:
            start_date = datetime.strptime(valid_dates[0], '%Y-%m-%d')
            end_date = datetime.strptime(valid_dates[-1], '%Y-%m-%d')
            ax.plot(start_date, valid_areas[0], 'o', color=color, markeredgecolor='black')
            ax.plot(end_date, valid_areas[-1], 'o', color=color, markeredgecolor='black')

            # Adding text labels at start and end points
            ax.text(start_date, valid_areas[0], nodule_id, fontsize='xx-small', color=color)
            ax.text(end_date, valid_areas[-1], nodule_id, fontsize='xx-small', color=color)

def test_make_rainbow_plot(file_path, save_filename):
    """ Test function to create and save a rainbow plot from a JSON file. """
    logger.info("Loading data from file.")
    with open(file_path, 'r') as file:
        data = json.load(file)

    fig, ax = plt.subplots(figsize=(15, 8))  # Larger figure
    make_rainbow_plot(data, ax)

    # Formatting the plot
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    fig.autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Area')
    ax.set_title('Rainbow Plot of Nodules')

    # Save the plot to a file
    plt.savefig(save_filename)
    logger.info(f"Saved plot to {save_filename}")

    # Open the saved image file
    if os.path.exists(save_filename):
        subprocess.run(['open', save_filename], check=True)
    else:
        logger.error(f"Failed to find the saved file: {save_filename}")

# Test file path
test_file_path = 'output\\crop1000\\crop1000_nodules.json'

save_file_name = 'output\\crop1000\\crop1000_nodules.png'

test_make_rainbow_plot(test_file_path, save_file_name)




