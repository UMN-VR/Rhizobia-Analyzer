import os
import imageio
from logger import Logger
from PIL import Image, ImageDraw, ImageFont


from dir_utils import get_all_image_files


from PIL import ImageFont

def get_font(font_size=10):
    try:
        # Try to load Arial font if available
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback to default font if Arial is not found
        font = ImageFont.load_default()
    return font

def generate_gifs(nodule_dir, logger):
    
    # #print(f"nodule_dir: {nodule_dir}")
    # nodule_num = 
    # o_jpg_files = sorted([f for f in os.listdir(nodule_dir) if f.endswith('.jpg')])
    # o_jpg_files = [os.path.join(nodule_dir, f) for f in o_jpg_files]
    
    # o_images = [imageio.imread(f) for f in o_jpg_files]
    # o_gif_path = os.path.join(nodule_dir, 'o.gif')            
    # imageio.mimsave(o_gif_path, o_images, duration=1)


    
    # d_jpg_folder = os.path.join(nodule_dir, 'detection')
    # d_jpg_files = sorted([f for f in os.listdir(d_jpg_folder) if f.endswith('.jpg')])
    # d_jpg_files = [os.path.join(d_jpg_folder, f) for f in d_jpg_files]
    
    # d_images = [imageio.imread(f) for f in d_jpg_files]
    # d_gif_path = os.path.join(nodule_dir, 'd.gif')
    # imageio.mimsave(d_gif_path, d_images, duration=1)

    generate_gif(nodule_dir, 'o.gif', logger)
    generate_gif(os.path.join(nodule_dir, 'detection'), 'd.gif', logger)


import numpy as np

def generate_gif(path, output_name, logger, duration=500):
    logger.info(f"@generate_gif: path:{path}, output_name:{output_name}")
    jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.jpg')])
    len_jpg_files = len(jpg_files)
    logger.info(f"len_jpg_files: {len_jpg_files}")
    
    if len_jpg_files == 0:
        # try .png
        jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
    
    if len(jpg_files) == 0:
        logger.error("No valid image files found.")
        return
    
    jpg_files = [os.path.join(path, f) for f in jpg_files]
    
    images = []
    for f in jpg_files:
        pil_img = Image.open(f)
        draw = ImageDraw.Draw(pil_img)
        
        # Add text to bottom-right corner
        text = os.path.basename(f)
        font = get_font()  # Using your get_font function

        # Manually set text position (bottom right corner)
        x, y = 35, 40  # Adjust these values as needed for the text position


        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        images.append(np.array(pil_img))
        # Optional: Print the file name for debugging
        #print(f"Processed image: {f}")

    gif_path = os.path.join(path, output_name)
    imageio.mimsave(gif_path, images, duration=duration, loop=0)
    # Optional: Print completion message
    print(f"GIF saved at: {gif_path}")


# def generate_gif(path, output_name, logger, duration=500):
#     logger.info(f"@generate_gif: path:{path}, output_name:{output_name}")
#     jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.jpg')])
#     len_jpg_files = len(jpg_files)
#     logger.info(f"len_jpg_files: {len_jpg_files}")
    
#     if len_jpg_files == 0:
#         # try .png
#         jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
    
#     if len(jpg_files) == 0:
#         logger.error("No valid image files found.")
#         return
    
#     jpg_files = [os.path.join(path, f) for f in jpg_files]
    
#     images = []
#     for f in jpg_files:
#         pil_img = Image.open(f)
#         draw = ImageDraw.Draw(pil_img)
        
#         # Add text to bottom-right corner
#         text = os.path.basename(f)
#         font = get_font()  # Using your get_font function

#         # Measure text size with the font object
#         textwidth, textheight = font.getsize(text)  
        
#         width, height = pil_img.size
#         x = width - textwidth - 10  # Adjust as needed
#         y = height - textheight - 10  # Adjust as needed

#         draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
#         images.append(np.array(pil_img))
#         # Optional: Print the file name for debugging
#         print(f"Processed image: {f}")

#     gif_path = os.path.join(path, output_name)
#     imageio.mimsave(gif_path, images, duration=duration, loop=0)
#     # Optional: Print completion message
#     print(f"GIF saved at: {gif_path}")


# def generate_gif(path, output_name, logger, duration=500):
#     logger.info(f"@generate_gif: path:{path}, output_name:{output_name}")
#     jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.jpg')])
#     len_jpg_files = len(jpg_files)
#     logger.info(f"len_jpg_files: {len_jpg_files}")
    
#     if len_jpg_files == 0:
#         # try .png
#         jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
    
#     if len(jpg_files) == 0:
#         logger.error("No valid image files found.")
#         return
    
#     jpg_files = [os.path.join(path, f) for f in jpg_files]
    
#     images = []
#     for f in jpg_files:
#         pil_img = Image.open(f)
#         draw = ImageDraw.Draw(pil_img)
        
#         # Add text to bottom-right corner
#         text = os.path.basename(f)
#         font = ImageFont.load_default()
#         textwidth, textheight = draw.textsize(text, font)
        
#         width, height = pil_img.size
#         x = width - textwidth + 23
#         y = height - textheight 
        
#         draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
#         images.append(np.array(pil_img))

#     gif_path = os.path.join(path, output_name)
#     imageio.mimsave(gif_path, images, duration=duration, loop=0)




def generate_gif_from_list(list, output_filename, logger, duration=500, draw_text=False, filename_is_date=False):

    #print(f"@generate_gif_from_list: list:{list}, output_filename:{output_filename}")
    logger.info(f"@generate_gif_from_list: list:{list}, output_filename:{output_filename}")
    images = []
    for f in list:
        pil_img = Image.open(f)
        draw = ImageDraw.Draw(pil_img)
        
        # Add text to bottom-right corner
        text = os.path.basename(f)

        #remove extension
        text = os.path.splitext(text)[0]
        
        if filename_is_date:
            # text is formated like: 20230607 and will be converted to 2023-06-07
            text = f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    

        #font = ImageFont.load_default()
        #font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
        font = get_font()


        width, height = pil_img.size

        # x = width -100
        y = height-50 
        x = 0
        # y = 0

        bbox = draw.textbbox((x, y), text, font=font)
        textwidth, textheight = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if draw_text:
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        images.append(np.array(pil_img))

    #print(f"output_filename: {output_filename})
    logger.info(f"output_filename: {output_filename}")
    imageio.mimsave(output_filename, images, duration=duration, loop = 0)


# files = get_all_image_files("data/crop1000")

# logger = Logger("generate_gifs").get_logger()

# generate_gif_from_list(files, "crop1000.gif", logger, draw_text=True, filename_is_date=True)

# generate_gifs("output/crop1000/nodules-last-detected-on/2023-06-07/34", logger)