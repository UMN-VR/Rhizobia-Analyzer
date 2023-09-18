import os
import imageio

def generate_gifs(crop_folder, logger):
    dates_dir = os.path.join("output", crop_folder.replace("data", "").strip("/")) + "/nodules-last-detected-on"
    print(f"@generate_gifs: dates_dir:{dates_dir}")
    
    subdirs = [os.path.join(dates_dir, o) for o in os.listdir(dates_dir) if os.path.isdir(os.path.join(dates_dir,o))]
    
    for subdir in subdirs:
        subdir_folder = subdir.split("/")[-1]
        print(f"subdir: {subdir}")
        year, month, day = os.path.basename(subdir).split("-")
        
        nodules_subdirs = [os.path.join(subdir, o) for o in os.listdir(subdir) if os.path.isdir(os.path.join(subdir,o))]


        for nodule_dir in nodules_subdirs:
            print(f"nodule_dir: {nodule_dir}")
            nodule_num = os.path.basename(nodule_dir)
            o_jpg_files = sorted([f for f in os.listdir(nodule_dir) if f.endswith('.jpg')])
            o_jpg_files = [os.path.join(nodule_dir, f) for f in o_jpg_files]
            
            o_images = [imageio.imread(f) for f in o_jpg_files]
            o_gif_path = os.path.join(nodule_dir, 'o.gif')            
            imageio.mimsave(o_gif_path, o_images, duration=1)
            
            d_jpg_folder = os.path.join(nodule_dir, 'detection')
            d_jpg_files = sorted([f for f in os.listdir(d_jpg_folder) if f.endswith('.jpg')])
            d_jpg_files = [os.path.join(d_jpg_folder, f) for f in d_jpg_files]
            
            d_images = [imageio.imread(f) for f in d_jpg_files]
            d_gif_path = os.path.join(nodule_dir, 'd.gif')
            imageio.mimsave(d_gif_path, d_images, duration=1)
