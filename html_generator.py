# File: html_generator.py
import base64
import cv2
from jinja2 import Environment, FileSystemLoader
from Logger import Logger
import os

class HtmlGenerator:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.env = Environment(loader=FileSystemLoader('templates'))

    def _encode_image(self, image_file: str) -> str:
        """Read the image file and encode it."""
        with open(image_file, "rb") as file:
            image_data = file.read()
            self.logger.info("Image file read successfully.")
        encoded_image = base64.b64encode(image_data).decode()
        self.logger.info("Image file encoded successfully.")
        return encoded_image

    def fetch_image_dims(self, image_file: str) -> tuple:
        """Get the image dimensions."""
        image = cv2.imread(image_file)
        image_height, image_width, _ = image.shape
        self.logger.info("Image dimensions fetched.")
        return image_height, image_width

    def generate_html(self, image_file: str, output_file: str, prev_data: str, json_data: str,  next_data: str, scalar_position=1, scalar_size=1, transparency=0.25):
        """Generate an HTML file to visualize the image analysis results."""
        self.logger.info("Starting to generate HTML...")
        image_height, image_width = self.fetch_image_dims(image_file)

        # Remore everything after the last slash to get only the file name
        image_file = os.path.basename(image_file)

        json_data = os.path.basename(json_data) 

        # add ../{data}/{data}.json to the prev_data and next_data
        if prev_data != None:
            prev_data = os.path.join("..", prev_data, prev_data)
            prev_data += ".json"

        if next_data != None:
            next_data = os.path.join("..", next_data, next_data)
            next_data += ".json"
        

        # Get the HTML template
        html_template = self.env.get_template('visualizer.html')

        html_content = html_template.render(
            image_file=image_file,
            prev_data=prev_data, json_data=json_data, next_data=next_data,
            image_height=image_height, image_width=image_width,
            scalar_position=scalar_position, scalar_size=scalar_size, 
            transparency=transparency
        )

        # Save the HTML content to the output file
        with open(output_file, "w") as html_file:
            html_file.write(html_content)
        self.logger.info(f"HTML file saved as {output_file}")

        self.logger.info("HTML file generated successfully.")
