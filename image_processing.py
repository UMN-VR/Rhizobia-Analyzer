import os
import cv2
import json
import sys
import numpy as np
from logger import Logger

import image_analysis




class ImageProcessor:

    @staticmethod
    def get_max_id(tracked_objects):
        """ Find the maximum ID in the list of tracked objects. """
        if tracked_objects is not None and len(tracked_objects) > 0:
            # Extract date and id components from id string
            id_components = [(obj['id'].split('_')[0], int(obj['id'].split('_')[1])) for obj in tracked_objects if obj['id'] is not None]
            # Find the maximum id component
            max_id = max(id_components, key=lambda x: x[1])
            # Reconstruct the id string
            max_id_str = f"{max_id[0]}_{max_id[1]}"
            return max_id_str
        else:
            return None



        

    @staticmethod
    def find_dayJSON_match_for_contour(x, y, w, h, area, json_data, logger):
        """
        Match contour with JSON data and return matched object.

        JSON_data example:
        {'x': 186, 'y': 92, 'd': 13, 'a': 541.0, 'p': 87.3553, 'e': 0.681415}, {'x': 241, 'y': 95, 'd': 7, 'a': 186.0, 'p': 48.0416, 'e': 0.57267}, {'x': 164, 'y': 98, 'd': 4, 'a': 63.0, 'p': 26.7279, 'e': 0.383255},


        
        Checks if any of the rectangle generated from the contour encloses the centroid of any of the JSON objects.

        If a match is found, return the matched object, otherwise return None and print closest match to logger. 
        """

        logger.info(f"@find_dayJSON_match_for_contour: x: {x}, y: {y}, w: {w}, h: {h}, area: {area}")
        #logger.info(f"JSON data: {json_data}")

        #logger.info(f"JSON data: {json_data}")

        # Initialize the closest match
        closest_match = None

        distances = []

        i = 0
        # Process each JSON object
        for json_obj in json_data:
            
            # parse the JSON object
            json_x, json_y, json_d, json_a, json_p, json_e = json_obj["x"], json_obj["y"], json_obj["d"], json_obj["a"], json_obj["p"], json_obj["e"]

            # calculate if the centroid of the JSON object is inside the rectangle
            if x <= json_x <= x + w and y <= json_y <= y + h:

                # Print the results to the console
                logger.info(f"Matched with JSON#{i}: ({json_x}, {json_y}, {json_d}, {json_a}, {json_p}, {json_e})")

                # add ID as i to JSON object
                json_obj["id"] = i

                # add tq (Tracking Confidence) to JSON object
                json_obj["tq"] = 100

                # return the matched object

                return json_obj

            # if not inside of rectangle calculate distance from centroid to rectangle
            else:
                # calculate the distance between the centroid of the contour and the centroid of the JSON object
                distance = np.sqrt((json_x - (x + w / 2)) ** 2 + (json_y - (y + h / 2)) ** 2)
                distances.append(distance)

                # if the closest match is None or the distance is smaller than the closest match, update the 
                if closest_match is None or distance < closest_match["distance"]:
                    closest_match = {"id": i, "distance": distance}
            
            i += 1
        
        # if here, no match was found, fetch details of closest match
        closest_match = json_data[closest_match["id"] - 1]

        # Print the closest match to the logger
        logger.info(f"Closest match: {closest_match}")
        return None


    @staticmethod
    def extract_segment(right_image, left_image, cX, cY):
        """
        Extract the image segment corresponding to the contour from both right and left images.
        """
        right_nodule_img = right_image[max(0, cY - 25):min(right_image.shape[0], cY + 25),
                          max(0, cX - 25):min(right_image.shape[1], cX + 25)]
        left_nodule_img = left_image[max(0, cY - 25):min(left_image.shape[0], cY + 25),
                         max(0, cX - 25):min(left_image.shape[1], cX + 25)]
        return right_nodule_img, left_nodule_img
    


    @staticmethod
    def process_image(image, output_dir, image_name, logger, json_data, matching, date_string):
        """
        Function to process an image, detect objects in the image, and segment the objects.
        """

        logger.info(f"\n@process_image: output_dir: {output_dir}, image_name: {image_name}, date_string: {date_string}")
        #logger.info(f"tracked_objects: {tracked_objects}")
        logger.info(f"{len(json_data)} json_data entries")
        logger.info(f"{len(matching)} matching entries")

        #logger.info(f"json_data: {json_data}")
        #logger.info(f"matching: {matching}")

        # Create folder to store 50x50 chopped images of nodules
        #nodules_dir = os.path.join(output_dir, 'nodules') 
        # when output_dir = 'output/crop1001/20230424', nodules_dir = 'output/crop1001/20230424/nodules' instead we want to use 'output/crop1001/nodules/20230424' 

        # get the 'output/crop1001' part of the output_dir
        crop_dir = os.path.dirname(output_dir) # 'output/crop1001'
        logger.info(f"crop_dir: {crop_dir}")
        # for the '20230424' part use date_string

        # create the nodules_dir
        nodules_dir = os.path.join(crop_dir, 'nodules-last-detected-on') # 'output/crop1001/nodules'
        logger.info(f"nodules_dir: {nodules_dir}")

        # Split the image into left and right images
        mid_x = image.shape[1] // 2
        left_image = image[:, :mid_x]
        right_image = image[:, mid_x:]
        logger.info(f"Split image into left and right images: {left_image.shape}, {right_image.shape}")

        # Convert the right image to HSV and apply a mask to detect nodules
        hsv = cv2.cvtColor(right_image, cv2.COLOR_BGR2HSV)
        logger.info(f"Converted right image to HSV: {hsv.shape}")

        # Create a mask to detect nodules
        mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        logger.info(f"Created mask to detect nodules: {mask.shape}")

        # Optional: show mask to user
        # cv2.imshow("Mask", mask)
        # cv2.waitKey(0)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize the empty list of results
        results = []

        max_id = f"{date_string}_0"
        



        logger.info(f"\nFound {len(contours)} contours in mask, processing each contour...\n")
        # Process each contour
        for i, contour in enumerate(contours):

            date_component, id_component = max_id.split('_')

            # Extract date and id components from max_id string
            logger.info(f"max_id: {max_id}, i: {i}")
            # logger.info("Contour:")
            # logger.info(f"{contour}\n"

            
            # Find the moments of the contour
            # Moments are used to find the centroid of the contour, a moment is a weighted average of the image pixels
            M = cv2.moments(contour)
            logger.info(f"Moments: {M}")

            # If the area of the contour is 0, skip it
            if M["m00"] == 0:
                logger.info(f"Skipping contour#{i + 1} because area is 0.\n\n")
                continue
            
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

            matched_contour = ImageProcessor.find_dayJSON_match_for_contour(x, y, w, h, area, json_data, logger)

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
            #look through the matching and find the corresponding entry, the set the entry_id to the 'name' in the matching entry in one line
            if matching is not None:
                for match_entry in matching:
                    current_id = match_entry['c']
                    previous_id = match_entry['p']
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

                match = {'c': JSON_entry, 'p': -1, 'id': max_id}


            #look through the matching and find the corresponding entry, the set the entry_id to the 'name' in the matching entry
            # for first_id, second_id, name in matching:
            #     logger.info(f"first_id: {first_id} second_id: {second_id} name: {name}")

            #     if JSON_entry == first_id:
            #         logger.info(f"Matched with {name}")
            #         entry_id = name
            #         break


            # Create a new entry for the results list 'm' is the matching entry in the matching list
            entry = {'m':match, 'c': cords, 'a': area, 'r': rect, 'e': matched_contour}

            if JSON_entry == "ERROR":
                logger.info(f"ERROR: No input JSON(nodules) match, ID:{max_id} area: {area} position: {cords}")
            else:
                # Add the entry to the results list
                results.append(entry)


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

            # Extract the image segment corresponding to the contour from both right and left images
            right_nodule_img, left_nodule_img = ImageProcessor.extract_segment(right_image, left_image, cX, cY)

            image_file_name = f"{formated_date_string}.jpg" 

            right_nodule_image_file_path = os.path.join(nodule_images_detection_path, image_file_name)

            cv2.imwrite(right_nodule_image_file_path, right_nodule_img)

            logger.info(f"Segmented nodule image saved as {right_nodule_image_file_path}")

            
            left_nodule_image_file_path = os.path.join(nodule_images_path, image_file_name)

            cv2.imwrite(left_nodule_image_file_path, left_nodule_img)

            logger.info(f"Original nodule image saved as {left_nodule_image_file_path}")
            


            # Increment the id component
            id_component = int(id_component) + 1
            # Reconstruct the max_id string
            max_id = f"{date_component}_{id_component}"

            logger.info(f"\n")




        logger.info(f"Done analyzing contours, found {len(results)} nodules.\n\n")

        # Save the results to a JSON file
        json_file_name = os.path.join(output_dir, f'{image_name}.json')
        with open(json_file_name, 'w') as json_file:
            json.dump(results, json_file, indent=2)
        
        return image, json_file_name, results
