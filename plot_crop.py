
# Full re-write of the `plot_crop.py` file, incorporating all discussed functionalities.
import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from Logger import Logger
def plot_crop(crop_json_file, plot_file_name_prefix, logger=None):

    logger.info(f"@plot_crop: crop_json_file:{crop_json_file}, plot_file_name_prefix:{plot_file_name_prefix}, logger:{logger}")
        # Read JSON file
    with open(crop_json_file, 'r') as f:
        data = json.load(f)
    crop_number = list(data.keys())[0]
    crop_data = data[crop_number]
    
    # Initialize lists for metrics and dates
    dates, dx, dy, dd, da, dp, de, tq, i = [], [], [], [], [], [], [], [], []
    matching, unmatched_current, unmatched_previous = [], [], []
    i_dict, average_tracking_quality = [], []
    
    # Loop through each entry to populate metric and date lists
    for entry in crop_data:
        # Extract metrics and dates
        dates.append(entry.get('date', None))
        stats = entry.get('match_stats', {})
        averages = stats.get('averages', {})
        lengths = stats.get('lengths', {})
        
        dx.append(averages.get('dx', None))
        dy.append(averages.get('dy', None))
        dd.append(averages.get('dd', None))
        da.append(averages.get('da', None))
        dp.append(averages.get('dp', None))
        de.append(averages.get('de', None))
        tq.append(averages.get('tq', None))
        i.append(averages.get('i', None))
        
        matching.append(lengths.get('matching', None))
        unmatched_current.append(lengths.get('unmatched_current', None))
        unmatched_previous.append(lengths.get('unmatched_previous', None))
        
        i_dict.append(stats.get('i_dict', {}))
        average_tracking_quality.append(stats.get('average_tracking_quality', None))
        
    # Generate unique keys from all i_dict entries
    unique_keys = set()
    for idict in i_dict:
        unique_keys.update(idict.keys())
        
    # Generate a color map for unique keys
    n_unique_keys = len(unique_keys)
    colors = cm.RdYlGn_r(np.linspace(0, 1, n_unique_keys))
    color_map = {key: colors[idx] for idx, key in enumerate(sorted(unique_keys, key=int))}
    # Prepare custom date labels
    prev_month, prev_year = None, None
    custom_date_labels = []
    for date in dates:
        day, month, year = date[6:], date[4:6], date[:4]
        if month != prev_month or year != prev_year:
            custom_date_label = f"{day}\n{month}/{year}"
        else:
            custom_date_label = day
        custom_date_labels.append(custom_date_label)
        prev_month, prev_year = month, year
    
    # Group metrics for plotting
    metric_groups = [
        [('Δx (change in x)', dx, 'b'), ('Δy (change in y)', dy, 'g'), ('Δa (area)', da, 'c'), ('Δp (perimeter)', dp, 'm')],
        [('i average (should increase by 1 every day if perfect tracking)', i, 'orange'), ('tq_avg (Average(+ and -)Tracking Quality)', tq, 'k'), ('Δd (diameter)', dd, 'r'), ('Δe (eccentricity)', de, 'y')],
        [('Matching', matching, 'purple'), ('Unmatched Current', unmatched_current, 'pink'),
         ('Unmatched Previous', unmatched_previous, 'brown'),
         ('tq (Average Positive Tracking Quality)', average_tracking_quality, 'lime')]
    ]

    #diameter, eccentricity, perimeter, area, i, tq, matching, unmatched_current, unmatched_previous, i_dict, average_tracking_quality
    
   # Special colormap for centered metrics
    
    
    for group_idx, metric_group in enumerate(metric_groups):
        fig, axs = plt.subplots(4, 1, figsize=(16, 10))
        plt.subplots_adjust(hspace=0.4)  
        
        for ax, (metric_name, metric_data, color) in zip(axs, metric_group):
            
            # Filter out None values for normalization BAD CODE, ADD ELSE STATEMENT, MIGHT CAUSE MISALIGNMENT AND SHOW WRONG DATA
            filtered_dates = [date for date, val in zip(dates, metric_data) if val is not None]
            filtered_data = [val for val in metric_data if val is not None ]

            # print sizes of filtered data and dates 
            logger.info(f"filtered_dates: {len(filtered_dates)}")
            logger.info(f"filtered_data: {len(filtered_data)}")
            
            if metric_name in ['Δx (change in x)', 'Δy (change in y)', 'Δa (area)', 'Δp (perimeter)', 'Δe (eccentricity)', 'Δd(diameter)', 'tq_avg (Average(+ and -)Tracking Quality)', 'Unmatched Current', 'Unmatched Previous']:
                max_val = max(abs(np.min(filtered_data)), np.max(filtered_data))
                filtered_data_abs = np.abs(filtered_data)
                norm_data = np.array(filtered_data_abs) / max_val  # This will make it go from -1 to 1
                #print(norm_data)
                centered_metric_cmap = cm.RdYlGn_r
                colors_b = [centered_metric_cmap(val) for val in norm_data]  # Map to 0 to 1
                ax.bar(filtered_dates, filtered_data, color=colors_b)
            
            elif metric_name in ['tq (Average Positive Tracking Quality)', 'Matching']:
                max_val = max(abs(np.min(filtered_data)), np.max(filtered_data))
                norm_data = np.array(filtered_data) / max_val  # This will make it go from -1 to 1
                centered_metric_cmap = cm.RdYlGn
                colors_b = [centered_metric_cmap(val) for val in norm_data]  # Map to 0 to 1
                ax.bar(filtered_dates, filtered_data, color=colors_b)

            
            else:
                ax.bar(filtered_dates, filtered_data, color=color)
                
            ax.set_title(metric_name)
            ax.set_xticks(dates)
            ax.set_xticklabels(custom_date_labels, rotation=0)
            
            # Annotate y-values
            for i, txt in enumerate(metric_data):
                if txt is not None:
                    ax.annotate(str(txt), (dates[i], metric_data[i]), textcoords="offset points", xytext=(0, 5), ha='center')
        
        names = ["dx_dy_da_dp", "i_tq_dd_de", "matching_tq"]
        
        plt.savefig(f"{plot_file_name_prefix}_{names[group_idx]}.png")
        
        
    # Special plot for i_dict as a stacked bar chart
    # Special plot for i_dict as a stacked bar chart
    fig, ax = plt.subplots(figsize=(20, 10))
    counters = {}  # Initialize counters for each unique key
    for idx, date in enumerate(dates):
        if i_dict[idx]:
            keys, values = zip(*i_dict[idx].items())
            bottom_value = 0  # Initialize the bottom for the stacked bar
            
            for k, v in zip(keys, values):
                # Increment the counter for the current key, initialize it if it doesn't exist
                counters[k] = counters.get(k, 0) + 1
                
                # Calculate the color index, making sure it's within the colormap bounds
                color_idx = min(counters[k], n_unique_keys - 1)
                
                # Fetch the color from the colormap
                color = colors[color_idx]
                
                ax.bar(date, v, bottom=bottom_value, color=color, label=f"{date}_{k}")
                
                # Annotate the bar component with its number
                ax.text(date, bottom_value + v / 2, f"{k}:{v}", ha='center', va='center')
                
                # Update the bottom for the next segment
                bottom_value += v
    ax.set_title("i_dict plot: if tracking well 'i' should increase by 1 each day(green)")
    ax.set_xticks(dates)
    ax.set_xticklabels(custom_date_labels, rotation=0)
    plt.savefig(f"{plot_file_name_prefix}_i_dict.png")
    #plt.show()

# Example usage
# logger = Logger('plot_crop').get_logger()
# plot_crop('output/crop1000/crop1000.json', "output/crop1000/plots/dif_plot")
