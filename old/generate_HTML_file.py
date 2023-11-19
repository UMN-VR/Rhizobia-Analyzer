
import os
import cv2
from html_generator import HtmlGenerator

def generate_HTML_file(image, prev_data, json_data, next_data, image_output_dir, base_name, logger):
    """
    Store processed results to HTML and modified image file.
    """

    # Directory to store the modified image file
    modified_image_file = os.path.join(image_output_dir, f"{base_name}_rectangles.jpg")

    # for result in results:
    #     x, y, w, h = result['rect_coords']
    #     #logger.info(f"ID: {result['id']}, Location: {result['position']}, Size: {result['size']}")

    #save the image with the rectangles drawn on it
    cv2.imwrite(modified_image_file, image)
    logger.info(f"Modified image saved as: {modified_image_file}")

    result_file_name = os.path.join(image_output_dir, f"{base_name}_result.html")

    # Create an instance of HtmlGenerator
    html_generator = HtmlGenerator(logger)

    logger.info(f"Generating HTML with:")

    logger.info(f"modified_image_file: {modified_image_file}")
    logger.info(f"result_file_name: {result_file_name}")
    logger.info(f"prev_data: {prev_data}")
    logger.info(f"json_data: {json_data}")
    logger.info(f"next_data: {next_data}")


    html_generator.generate_html(modified_image_file, result_file_name, prev_data, json_data, next_data)

    cv2.destroyAllWindows()

    return result_file_name
