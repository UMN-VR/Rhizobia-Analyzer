from scipy.optimize import linear_sum_assignment
import numpy as np

from i_dict import iDict

#from json_utils import initialize_json_file, append_to_json_list

def find_matching(logger, combined_distances, crop_folder, distance_threshold=20, next_matching=None, current_date_string=None, current_json=None, prev_json=None, next_json=None):
        """Find the matching between the current and previous points.
        Returns: matching, unmatched_current, unmatched_previous, distance_threshold

            format of matching: [(i, j, ID), ...] where i is the index of the current point, j is the index of the previous point, and ID is the ID of the nodule
        
        """

        logger.info(f"\n@find_matching: combined_distances: {combined_distances.shape}, next_matching: {next_matching}, current_date_string: {current_date_string}, distance_threshold: {distance_threshold}")

        row_ind, col_ind = linear_sum_assignment(combined_distances)
        unmatched_current = set(range(combined_distances.shape[0])) - set(row_ind)
        unmatched_previous = set(range(combined_distances.shape[1])) - set(col_ind)

        #distance_threshold = np.median(combined_distances[row_ind, col_ind]) * 3
        matching = []
        
        i_dict = iDict()

        tq_accumulator = 0

        dx_accumulator = 0
        dy_accumulator = 0
        dd_accumulator = 0
        da_accumulator = 0
        dp_accumulator = 0
        de_accumulator = 0
        

        tp_pos_accumulator = 0
        tq_pos_i = 0

        # if next_matching is not None:
        #     #next_ids = {match[2] for match in next_matching}  # Extract IDs from next matching
        #     next_ids = {match_entry['id'] for match_entry in next_matching}
        # else:
        #     next_ids = set()


        if next_matching is None:
            logger.info(f"next_matching is None")

        for idx, (current_index, previous_index) in enumerate(zip(row_ind, col_ind)):

            match_entry = None

            id = f"{current_date_string}_{len(matching)}"
            i = 0
            dx = 0
            dy = 0


            combined_distance = combined_distances[current_index, previous_index]

            prev_x = prev_json[previous_index]['x']
            prev_y = prev_json[previous_index]['y']


            current_x = current_json[current_index]['x']
            current_y = current_json[current_index]['y']

            # calculate the distance between the current and previous points
            p_dx = current_x - prev_x
            p_dy = current_y - prev_y

            prev_diameter = prev_json[previous_index]['d']
            current_diameter = current_json[current_index]['d']

            prev_area = prev_json[previous_index]['a']
            current_area = current_json[current_index]['a']

            prev_perimeter = prev_json[previous_index]['p']
            current_perimeter = current_json[current_index]['p']

            prev_eccentricity = prev_json[previous_index]['e']
            current_eccentricity = current_json[current_index]['e']

            # prev_tracking_quality = prev_json[previous_index]['tq']
            # current_tracking_quality = current_json[current_index]['tq']

            p_dd = round((current_diameter - prev_diameter), 2)

            p_da = round((current_area - prev_area), 2)

            p_dp = round((current_perimeter - prev_perimeter), 2)

            p_de = round((current_eccentricity - prev_eccentricity), 2)

            # dtq = current_tracking_quality - prev_tracking_quality

            # add to accumulators
            dx_accumulator += p_dx
            dy_accumulator += p_dy
            dd_accumulator += p_dd
            da_accumulator += p_da
            dp_accumulator += p_dp
            de_accumulator += p_de




            matched_next = False

            # if combined_distance <= distance_threshold:

            if next_matching is not None:

                for match_entry in next_matching: 

                    if match_entry['p']['id'] == current_index:

                        
                        if match_entry['p']['tq'] > 0:

                            matched_next = True
                
                            id = match_entry["id"]
                            i = match_entry["i"] + 1

                            next_index = match_entry["c"]['id']

                            next_x = next_json[next_index]['x']
                            next_y = next_json[next_index]['y']

                            next_diameter = next_json[next_index]['d']
                            next_area = next_json[next_index]['a']
                            next_perimeter = next_json[next_index]['p']
                            next_eccentricity = next_json[next_index]['e']

                            n_dx = next_x - current_x
                            n_dy = next_y - current_y

                            n_dd = round((next_diameter - current_diameter), 2)
                            n_da = round((next_area - current_area), 2)
                            n_dp = round((next_perimeter - current_perimeter), 2)
                            n_de = round((next_eccentricity - current_eccentricity), 2)



                            # If the nodule was matched below the distance threshold, keep its ID from the next matching
                            logger.info(f"matched entry: {match_entry}, len(matching): {len(matching)}")
                        else:
                            logger.info(f"tq < 0")
                            
                        break

                            

                            



                            
            
            # else:
            #     logger.info(f"combined_distances[{current_index}, {previous_index}] ={combined_distance} > {distance_threshold} = distance_threshold") 


                

            tracking_quality = (100-((combined_distance/distance_threshold)*100)).round()

            prev = {'id': previous_index, 'tq': tracking_quality, 'dx': p_dx, 'dy': p_dy, 'dd': p_dd, 'da': p_da, 'dp': p_dp, 'de': p_de}

            current = {'id': current_index}

            if matched_next:
                next = {'id': next_index, 'dx': n_dx, 'dy': n_dy, 'dd': n_dd, 'da': n_da, 'dp': n_dp, 'de': n_de}

            else:
                next = {}
                # filename format is 'output/{crop_folder}/nodules-last-detected-on/{date_string}/{id}/_.json'
                # filename must be something like 'output/crop1001/nodules-last-detected-on/2023-04-24/0/_.json'

                # formated_date_string = current_date_string[0:4] + '-' + current_date_string[4:6] + '-' + current_date_string[6:8]

                # id_number_component = id.split('_')[1]
                # filename = f"output/{crop_folder}/nodules-last-detected-on/{formated_date_string}/{id_number_component}/_.json"
                # initialize_json_file(filename)
                
            # give i name 'c' for current, and j name 'p' for previous
            match_result = {'id': id, 'p': prev, 'c': current, 'n':next, 'i':i}

            # add tracking quality to tq_accumulator
            tq_accumulator += tracking_quality

            if tracking_quality > 0:
                tp_pos_accumulator += tracking_quality
                tq_pos_i += 1

            i_dict.add_entry(i)
            

            if match_entry is None:
                logger.info(f"match is None, entry: {match_result} len(matching): {len(matching)}")
            
            matching.append(match_result)
        
        len_matching = len(matching)

        i_dict, i_average = i_dict.get_results()

        logger.info(f"i_dict: {i_dict}")
        print(f"i_dict: {i_dict}")

        # calculate the average tracking quality
        tq_average = tq_accumulator/len_matching

        dx_average = dx_accumulator/len_matching
        dy_average = dy_accumulator/len_matching
        dd_average = dd_accumulator/len_matching
        da_average = da_accumulator/len_matching
        dp_average = dp_accumulator/len_matching
        de_average = de_accumulator/len_matching

        logger.info(f"tq_average: {tq_average}, dx_average: {dx_average}, dy_average: {dy_average}, dd_average: {dd_average}, da_average: {da_average}, dp_average: {dp_average}, de_average: {de_average}")


        # calculate the average tracking quality of the positive matches
        average_tracking_quality = tp_pos_accumulator/tq_pos_i
        #print(f"average_tracking_quality: {average_tracking_quality}")
        logger.info(f"average_tracking_quality: {average_tracking_quality}")

        logger.info(f"@find_matching:\nReturning:\nMatching(lenght={len(matching)}): {matching}")
        logger.info(f"Unmatched current(length={len(unmatched_current)}): {unmatched_current}")
        logger.info(f"Unmatched previous(length={len(unmatched_previous)}): {unmatched_previous}")
        logger.info(f"Distance threshold: {distance_threshold}")
        
        logger.info(f"\n\n")


        stats = {'i_dict': i_dict,'average_tracking_quality': average_tracking_quality, 'distance_threshold': distance_threshold, 
                  'length' : {'matching': len_matching, 'unmatched_current': len(unmatched_current), 'unmatched_previous': len(unmatched_previous)},
                    'average': {'tq': tq_average, i_average: i_average, 'dx': dx_average, 'dy': dy_average, 'dd': dd_average, 'da': da_average, 'dp': dp_average, 'de': de_average}
                }

        return matching, unmatched_current, unmatched_previous, stats