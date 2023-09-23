import os
import cv2
from find_dayJSON_match_for_contour import find_dayJSON_match_for_contour


from cv_utils import extract_segment

from json_utils import append_to_json_list


def process_contour(i, contour, logger, json_data, matching, date_string, nodules_dir, right_image, left_image, max_id):
    

    # Extract date and id components from max_id string
    logger.info(f"@process_contour: max_id: {max_id}")
    # logger.info("Contour:")
    # logger.info(f"{contour}\n"

    
    # Find the moments of the contour
    # Moments are used to find the centroid of the contour, a moment is a weighted average of the image pixels
    M = cv2.moments(contour)
    logger.info(f"Moments: {M}")

    # If the area of the contour is 0, skip it
    if M["m00"] == 0:
        logger.info(f"Skipping contour#{i + 1} because area is 0.\n\n")
        return None
    
    # Find the centroid of the contour
    cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
    logger.info(f"Centroid: {cX}, {cY}")

    # Calculate the bounding rectangle of the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Calculate the area of the contour
    area = cv2.contourArea(contour)

    cords = {'x' : x, 'y': y}
    rect = {'x' : x, 'y': y, 'w': w, 'h': h}

    # Print the results to the console
    logger.info(f"Processing contour#{i + 1}: area: {area} centroid: {cX}, {cY} rectangle: ({x}, {y}, {w}, {h})")
    
    # Find the matching contour in the JSON data 
    # NEEDS WORK

    matched_contour = find_dayJSON_match_for_contour(x, y, w, h, area, json_data, logger)

    # If a matching contour was found, use its ID, otherwise create a new ID
    if matched_contour is not None:
        logger.info(f"Match with input JSON(nodules) ID: {matched_contour['id']}")

    # If no matching contour was found, create a new ID
    else:
        
        logger.info(f"No input JSON(nodules) match, ID:{max_id} area: {area} position: {cords}")

    # Get the JSON entry corresponding to the matched contour
    logger.info(f"Matched contour: {matched_contour}")
    JSON_entry = matched_contour['id'] if matched_contour is not None else "ERROR"
    logger.info(f"JSON_entry: {JSON_entry}")

    entry_id = max_id
    match = {}
    
    if matching is not None:
        for match_entry in matching:
            current_id = match_entry['c']['id']
            previous_id = match_entry['p']['id']
            name = match_entry['id']
            
            #logger.info(f"first_id: {first_id} second_id: {second_id} name: {name}")

            if JSON_entry == current_id:
                logger.info(f"Matched with first_id: {current_id} second_id: {previous_id} name: {name}")

                # Save the name of the matching entry [first_id, second_id, name]
                #match = [first_id, second_id, name]
                match = match_entry 
                entry_id = name
                break
    else:
        print("WARNING: matching is None")
        logger.info("WARNING: matching is None")

    if match == {}:
        logger.info("WARNING: match is empty")
        current = {'id': JSON_entry}

        match = {'id': max_id, 'p': {}, 'c': current,'n': {},}


    #look through the matching and find the corresponding entry, the set the entry_id to the 'name' in the matching entry
    # for first_id, second_id, name in matching:
    #     logger.info(f"first_id: {first_id} second_id: {second_id} name: {name}")

    #     if JSON_entry == first_id:
    #         logger.info(f"Matched with {name}")
    #         entry_id = name
    #         break


    # Create a new entry for the results list 'm' is the matching entry in the matching list
    entry = {'m':match, 'c': cords, 'a': area, 'r': rect, 'e': matched_contour}

    # if JSON_entry == "ERROR":
    #     logger.info(f"ERROR: No input JSON(nodules) match, ID:{max_id} area: {area} position: {cords}")
    # else:
    #     # Add the entry to the results list
    #     results.append(entry)


    logger.info(f"entry_id:{entry_id}, entry saved to results list")

    # Nodule images will be saved to 'output/crop1001/nodules/{last_detected_string}/{entry_id_number_component}/current_date.jpg'

    # separate the date and number from the entry_id, entry_id = '20210401_0' -> date_component = '20210401', id_component = '0'

    # get the date_component
    entry_id_date_component = entry_id.split('_')[0]
    # get the id_component
    entry_id_number_component = entry_id.split('_')[1]

    
    #nodule_images_path = os.path.join(nodules_dir, entry_id) 
    #os.makedirs(nodule_images_path, exist_ok=True)
    # # instead of output/crop975/nodules/20230607_202 use output/crop975/nodules/20230607/202

    # Extract the image segment corresponding to the contour from both right and left images
    right_nodule_img, left_nodule_img = extract_segment(right_image, left_image, cX, cY)

    # chech that the size of the images is 50x50 (50, 50, 3)
    if right_nodule_img.shape != (50, 50, 3):
        logger.info(f"WARNING: right_nodule_img.shape != (50, 50, 3) != {right_nodule_img.shape}")
        return entry
    
    if left_nodule_img.shape != (50, 50, 3):
        logger.info(f"WARNING: left_nodule_img.shape != (50, 50, 3) != {left_nodule_img.shape}")
        return entry
    

    #make sure the 'ouput/crop1001/nodules/{last_detected_string}/{entry_id_number_component}' directory exists, otherwise create it
    formatted_entry_id_date_component = entry_id_date_component[0:4] + '-' + entry_id_date_component[4:6] + '-' + entry_id_date_component[6:8]
    #last_detected_string = f"Last-Detected-{formatted_entry_id_date_component}"
    last_detected_string = f"{formatted_entry_id_date_component}"

    nodule_images_path = os.path.join(nodules_dir, last_detected_string, entry_id_number_component)
    os.makedirs(nodule_images_path, exist_ok=True)

    nodule_images_detection_path = os.path.join(nodule_images_path, "detection")
    os.makedirs(nodule_images_detection_path, exist_ok=True)

    os.makedirs(nodule_images_path, exist_ok=True)

    logger.info(f"created dirs at nodule_detection_path: {nodule_images_detection_path} and nodule_images_original_path: {nodule_images_path}")            

    # convert date_string to format '20210401' to '2021-04-01'
    formated_date_string = date_string[0:4] + '-' + date_string[4:6] + '-' + date_string[6:8]

    

    image_file_name = f"{formated_date_string}.jpg" 

    right_nodule_image_file_path = os.path.join(nodule_images_detection_path, image_file_name)

    cv2.imwrite(right_nodule_image_file_path, right_nodule_img)

    logger.info(f"Segmented nodule image saved as {right_nodule_image_file_path}")

    
    left_nodule_image_file_path = os.path.join(nodule_images_path, image_file_name)

    cv2.imwrite(left_nodule_image_file_path, left_nodule_img)

    logger.info(f"Original nodule image saved as {left_nodule_image_file_path}")
    

    logger.info(f"\n")

    append_to_json_list(nodule_images_path+"/_.json", entry)

    return entry