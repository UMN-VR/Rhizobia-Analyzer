
import os
import cv2
import json
import numpy as np

from process_contour import process_contour



def process_image(image, output_dir, image_name, logger, json_data, matching, date_string):
        """
        Function to process an image, detect objects in the image, and segment the objects.
        """

        logger.info(f"\n@process_image: output_dir: {output_dir}, image_name: {image_name}, date_string: {date_string}")
        #logger.info(f"tracked_objects: {tracked_objects}")
        logger.info(f"len(json_data) = {len(json_data)} json_data entries")
        max_id_i = len(matching)
        logger.info(f"len(matching) = {max_id_i} matching entries, setting max_id_i to {max_id_i}")

        

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

        # get the max_id from the matching



        #max_id_i = 0
        # das problem ist dass die id_component nicht eindeutig ist, weil es mehrere einträge mit dem gleichen datum gibt
        # fix: start max_id with len(matching)
        

        results = []

        logger.info(f"\nFound {len(contours)} contours in mask, processing each contour...\n")
        # Process each contour
        for i, contour in enumerate(contours):

            max_id = f"{date_string}_{max_id_i}"

            result = process_contour(i, contour, logger, json_data, matching, date_string, nodules_dir, right_image, left_image, max_id)

            if result is not None:
                results.append(result)                 

            max_id_i += 1
            
            

        logger.info(f"Done analyzing contours, found {len(results)} nodules.\n\n")

        # Save the results to a JSON file
        json_file_name = os.path.join(output_dir, f'{image_name}.json')
        with open(json_file_name, 'w') as json_file:
            json.dump(results, json_file, indent=2)
        
        return json_file_name