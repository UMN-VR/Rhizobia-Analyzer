from scipy.optimize import linear_sum_assignment
import numpy as np

from i_dict import iDict

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
        
        i_dict = iDict()

        tq_accumulator = 0
        tp_pos_accumulator = 0
        tq_pos_i = 0

        if next_matching is not None:
            #next_ids = {match[2] for match in next_matching}  # Extract IDs from next matching
            next_ids = {match_entry['id'] for match_entry in next_matching}
        else:
            next_ids = set()


        if next_matching is None:
            logger.info(f"next_matching is None")

        for idx, (current_index, previous_index) in enumerate(zip(row_ind, col_ind)):

            match_entry = None

            id = f"{current_date_string}_{len(matching)}"
            i = 0
            next_index = -1


            combined_distance = combined_distances[current_index, previous_index]

            if combined_distance <= distance_threshold:

                if next_matching is not None:
                    for match_entry in next_matching:

                        if match_entry['p']['id'] == current_index and match_entry['p']['tq'] > 0:
                    
                            id = match_entry["id"]
                            i = match_entry["i"] + 1
                            next_index = match_entry["c"]['id']

                            # If the nodule was matched below the distance threshold, keep its ID from the next matching
                            logger.info(f"matched entry: {match_entry}, len(matching): {len(matching)}")
                            break
            
            else:
                logger.info(f"combined_distances[{current_index}, {previous_index}] ={combined_distance} > {distance_threshold} = distance_threshold") 

            tracking_quality = (100-((combined_distance/distance_threshold)*100)).round()

            prev = {'id': previous_index, 'tq': tracking_quality}

            current = {'id': current_index}

            next = {'id': next_index}
                
            # give i name 'c' for current, and j name 'p' for previous
            match_result = {'id': id, 'p': prev, 'c': current, 'n':next, 'i':i, 'tq':tracking_quality}

            # add tracking quality to tq_accumulator
            tq_accumulator += tracking_quality

            if tracking_quality > 0:
                tp_pos_accumulator += tracking_quality
                tq_pos_i += 1

            i_dict.add_entry(i)
            

            if match_entry is None:
                logger.info(f"match is None, entry: {match_result} len(matching): {len(matching)}")
            
            matching.append(match_result)
        

        i_dict, i_average = i_dict.get_results()

        logger.info(f"i_dict: {i_dict}")
        print(f"i_dict: {i_dict}")

        # calculate the average tracking quality
        tq_average = tq_accumulator/len(matching)
        logger.info(f"tq_average: {tq_average}")


        # calculate the average tracking quality of the positive matches
        average_tracking_quality = tp_pos_accumulator/tq_pos_i
        #print(f"average_tracking_quality: {average_tracking_quality}")
        logger.info(f"average_tracking_quality: {average_tracking_quality}")

        logger.info(f"@find_matching:\nReturning:\nMatching(lenght={len(matching)}): {matching}")
        logger.info(f"Unmatched current(length={len(unmatched_current)}): {unmatched_current}")
        logger.info(f"Unmatched previous(length={len(unmatched_previous)}): {unmatched_previous}")
        logger.info(f"Distance threshold: {distance_threshold}")
        
        logger.info(f"\n\n")


        stats = {'i_dict': i_dict, 'tq_average': tq_average, 'average_tracking_quality': average_tracking_quality, 'distance_threshold': distance_threshold}

        return matching, unmatched_current, unmatched_previous, stats