
import numpy as np
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