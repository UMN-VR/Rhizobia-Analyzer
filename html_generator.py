# File: html_generator.py
import base64
import cv2
from jinja2 import Environment, FileSystemLoader
from logger import Logger

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

    def generate_html(self, image_file: str, output_file: str, results: list, prev_data: list, next_data: list,  json_data: list, scalar_position=1, scalar_size=1, transparency=0.25):
        """Generate an HTML file to visualize the image analysis results."""
        self.logger.info("Starting to generate HTML...")
        encoded_image = self._encode_image(image_file)
        image_height, image_width = self.fetch_image_dims(image_file)

        # Get the HTML template
        html_template = self.env.get_template('visualizer.html')

        html_content = html_template.render(
            encoded_image=encoded_image,
            results=results, 
            prev_data=prev_data, next_data=next_data,
            json_data=json_data, 
            image_height=image_height, image_width=image_width,
            scalar_position=scalar_position, scalar_size=scalar_size, 
            transparency=transparency
        )

        # Save the HTML content to the output file
        with open(output_file, "w") as html_file:
            html_file.write(html_content)
        self.logger.info(f"HTML file saved as {output_file}")

        self.logger.info("HTML file generated successfully.")
