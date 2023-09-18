
# DEPRECATED
import os

import json
import sys
import numpy as np
from Logger import Logger

import image_analysis




class ImageProcessor:

    # DEPRECATED
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

    
# DEPRECATED BAD BAD BAD