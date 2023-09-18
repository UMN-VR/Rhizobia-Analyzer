import cv2
import sys

# loads 
def load_image(file_name):
    """
    Function to load an image using OpenCV.
    Arguments:
    file_name -- str, path to the image file.
    Returns:
    image -- numpy array, loaded image.
    """
    # Read the image
    image = cv2.imread(file_name)
    # If image reading fails, print an error message
    if image is None:
        print(f"Unable to open image file: {file_name}")
    return image