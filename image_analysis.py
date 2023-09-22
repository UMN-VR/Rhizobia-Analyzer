import os
import cv2
import json
import sys
import numpy as np

from Logger import Logger
from html_generator import HtmlGenerator

from scipy.spatial.distance import cdist

import matplotlib.pyplot as plt
from skimage import io, filters, measure
from skimage.segmentation import clear_border
from skimage.color import label2rgb
from skimage.morphology import closing, square

from memory_logger import log_memory_usage



import uuid

def normalize(arr):
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

class ImageAnalyzer:

    @staticmethod
    def extract_points_and_attributes(data):
        """Extract the points and their attributes from the data."""
        points = np.array([[point['x'], point['y']] for point in data])
        attributes = np.array([[point['d'], point['a'], point['p'], point['e']] for point in data])
        return points, attributes

    @staticmethod
    def normalize(attributes):
        """Normalize the attributes to have zero mean and unit variance."""
        attributes = (attributes - np.mean(attributes, axis=0)) / np.std(attributes, axis=0)
        return attributes

    @staticmethod
    def compute_distances(normalized_points, normalized_prev_points, attributes, attributes_prev):
        """Compute the spatial and attribute distances between all pairs of points."""
        spatial_distances = cdist(normalized_points, normalized_prev_points)
        attribute_distances = cdist(attributes, attributes_prev)
        return spatial_distances, attribute_distances

    @staticmethod
    def combine_distances(spatial_distances, attribute_distances, spatial_weight, attribute_weight):
        """Compute the combined distances."""
        combined_distances = spatial_weight * spatial_distances + attribute_weight * attribute_distances
        return combined_distances

    


        
    




