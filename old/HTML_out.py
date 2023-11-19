import os
import shutil

#i made this to create a link to view the images in the browser, 
def generate_HTML_results_page(results, script_output_dir, logger):
    html_dir = os.path.join(script_output_dir, 'HTML')
    os.makedirs(html_dir, exist_ok=True)
    
    results_page_path = os.path.join(html_dir, 'results_page.html')
    
    with open(results_page_path, 'w') as results_page:
        results_page.write('<html>\n<body>\n<ul>\n')

        for files in results:
            for file in files:
                crop_number = file.split('/')[1].replace('crop', '')  # Extract crop number
                new_file_name = f"{crop_number}_{os.path.basename(file)}"
                destination = os.path.join(html_dir, new_file_name)
                
                # Copy file
                shutil.copy2(file, destination)
                
                # Generate link
                link = f"https://htmlpreview.github.io/?https://github.com/UMN-VR/FramingV2-DetectionV5-PreProcessor-Output/blob/main/HTML/{new_file_name}"
                
                # Write link to HTML file
                results_page.write(f'<li><a href="{link}">{new_file_name}</a></li>\n')

        results_page.write('</ul>\n</body>\n</html>')

    logger.info(f"Results page generated at {results_page_path}")

def generate_offline_HTML_results_page(results, script_output_dir, logger):
    html_dir = os.path.join(script_output_dir, 'HTML')
    os.makedirs(html_dir, exist_ok=True)
    
    results_page_path = os.path.join(html_dir, 'offline_results_page.html')
    
    with open(results_page_path, 'w') as results_page:
        results_page.write('<html>\n<body>\n<ul>\n')

        for files in results:
            for file in files:
                crop_number = file.split('/')[1].replace('crop', '')  # Extract crop number
                new_file_name = f"{crop_number}_{os.path.basename(file)}"
                destination = os.path.join(html_dir, new_file_name)
                
                # Copy file
                shutil.copy2(file, destination)
                
                # Generate link
                link = destination  # local path to the file
                
                # Write link to HTML file
                results_page.write(f'<li><a href="file://{link}">{new_file_name}</a></li>\n')

        results_page.write('</ul>\n</body>\n</html>')

    logger.info(f"Offline results page generated at {results_page_path}")


def generate_results_page(results, script_output_dir, logger):

    user_input = input("Generate Offline HTML Results Page? (y/n): ")
    if user_input.lower() != 'n':
        generate_offline_HTML_results_page(results, script_output_dir, logger)


    user_input = input("Generate Online HTML Results Page? (y/n): ")
    if user_input.lower() != 'n':
        generate_HTML_results_page(results, script_output_dir, logger)
   




