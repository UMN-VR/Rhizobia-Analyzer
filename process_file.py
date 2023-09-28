import os
import subprocess
from image_analysis import ImageAnalyzer

def process_file(file_name, main_logger):
    # get the directory where the results will be saved
    output_dir = os.path.join("output", os.path.dirname(file_name).replace("data", "").strip("/"))
    # Call analyze_image() to process the image, this is where the magic happens
    result_file_name, new_objects = ImageAnalyzer.analyze_image(file_name, output_dir, external_logger=main_logger)
    # Open the HTML file generated
    subprocess.run(["xdg-open", result_file_name], stderr=subprocess.DEVNULL)  # Redirect stderr to /dev/null

