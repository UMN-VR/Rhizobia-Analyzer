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

def extract_segment(right_image, left_image, cX, cY):
        """
        Extract the image segment corresponding to the contour from both right and left images.
        """
        right_nodule_img = right_image[max(0, cY - 25):min(right_image.shape[0], cY + 25),
                          max(0, cX - 25):min(right_image.shape[1], cX + 25)]
        left_nodule_img = left_image[max(0, cY - 25):min(left_image.shape[0], cY + 25),
                         max(0, cX - 25):min(left_image.shape[1], cX + 25)]
        return right_nodule_img, left_nodule_img
    