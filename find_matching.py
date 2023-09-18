from scipy.optimize import linear_sum_assignment
import numpy as np

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