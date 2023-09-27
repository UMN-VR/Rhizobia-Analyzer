import os
import imageio
from Logger import Logger


from dir_utils import get_all_image_files




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


def generate_gif(path, output_name, logger, duration=500):

    #print(f"@generate_gif: path:{path}, output_name:{output_name}")
    logger.info(f"@generate_gif: path:{path}, output_name:{output_name}")

    jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.jpg')])

    len_jpg_files = len(jpg_files)
    #print(f"len_jpg_files: {len_jpg_files}")
    logger.info(f"len_jpg_files: {len_jpg_files}")
    if len_jpg_files == 0:
        #try .png
        jpg_files = sorted([f for f in os.listdir(path) if f.endswith('.png')])


    jpg_files = [os.path.join(path, f) for f in jpg_files]
    
    images = [imageio.imread(f) for f in jpg_files]
    gif_path = os.path.join(path, output_name)
    imageio.mimsave(gif_path, images, duration=duration, loop = 0)


def generate_gif_from_list(list, output_filename, logger, duration=500):

    #print(f"@generate_gif_from_list: list:{list}, output_filename:{output_filename}")
    logger.info(f"@generate_gif_from_list: list:{list}, output_filename:{output_filename}")
    images = [imageio.imread(f) for f in list]

    #print(f"output_filename: {output_filename})
    logger.info(f"output_filename: {output_filename}")
    imageio.mimsave(output_filename, images, duration=duration, loop = 0)


files = get_all_image_files("data/crop980")

logger = Logger("generate_gifs").get_logger()

generate_gif_from_list(files, "crop1000.gif", logger)