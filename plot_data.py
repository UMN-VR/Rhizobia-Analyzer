
import matplotlib.pyplot as plt

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
            i = match_entry['c']['id']
            j = match_entry['p']['id']
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
            i = match_entry['c']['id']
            j = match_entry['p']['id']
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