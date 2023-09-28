import json
import os
import matplotlib.pyplot as plt
import numpy as np
import json
from Logger import Logger


def are_valid_coordinates(x, y, xlim, ylim):
    """
    Check if the coordinates are within the axis limits.
    """
    if x > xlim[1] or x < xlim[0]:
        return False
    if y > ylim[1] or y < ylim[0]:
        return False

    return True

def check_overlap(existing_positions, _x, _y, x_threshold, y_threshold):

    #print(f"@check_overlap: existing_positions:{existing_positions}, _x:{_x}, _y:{_y}")

    for x, y in existing_positions:
        
        abs_x = abs(_x - x)
        abs_y = abs(_y - y)
        
        #if _x == x and _y == y
        if abs_x < x_threshold and abs_y < y_threshold:

            #print(f"x:{x}, y:{y}, _x:{_x}, _y:{_y}")

            return True
    
    return False



def check_overlap_helper(existing_positions, _x, _y, offset_increment, logger, xlim, ylim, i=0):
    """
    0: Check if the current position (x, y) is within the axis limits and not overlapping with any existing positions.
         If it is, return the offset_x and offset_y.
    1: Check if the right position (x + offset_x, y) is within the axis limits and not overlapping with any existing positions.
       If it is, return the offset_x and offset_y.
    2: Check if the upper position (x, y + offset_y) is within the axis limits and not overlapping with any existing positions.
       If it is, return the offset_x and offset_y.
    3: Check if the left position (x - offset_x, y) is within the axis limits and not overlapping with any existing positions.
         If it is, return the offset_x and offset_y.
    4: Check if the lower position (x, y - offset_y) is within the axis limits and not overlapping with any existing positions.
            If it is, return the offset_x and offset_y.
    5: If none of the above are true, call recursion on the top-righ position (x + offset_x, y + offset_y).
    """
    #print(f"\n@check_overlap_helper: existing_positions:{existing_positions}, x:{_x}, y:{_y}, offset_increment:{offset_increment}, xlim:{xlim}, ylim:{ylim}, i:{i}")
    logger.info(f"\n@check_overlap_helper: existing_positions:{existing_positions}, x:{_x}, y:{_y}, offset_increment:{offset_increment}, xlim:{xlim}, ylim:{ylim}, i:{i}")

    #Create list with positions to check
    positions_to_check = [(_x,_y),(_x + offset_increment['x'], _y), (_x, _y + offset_increment['y']), (_x - offset_increment['x'], _y), (_x, _y - offset_increment['y'])]
    modified = False
    for position in positions_to_check:
        x, y = position
        cords_valid = are_valid_coordinates(x, y, xlim, ylim)
        overlap = check_overlap(existing_positions, x, y, offset_increment['x']/2, offset_increment['y']/2)
        #print(f"position:{position}, cords_valid:{cords_valid}, overlap:{overlap}")

        if cords_valid and not overlap:
            return x, y, modified
        

        modified = True

        # wait for user input
        #input("Press Enter to continue...")
        
    #If none of the above are true, call recursion on the top-righ position (x + offset_x, y + offset_y).
    if i < 5:
        #print(f"Calling recursion on the top-righ position (x + offset_x, y + offset_y)")
        logger.info(f"Calling recursion on the top-righ position (x + offset_x, y + offset_y)")
        return check_overlap_helper(existing_positions, x + offset_increment['x'], y + offset_increment['y'], offset_increment, logger, xlim, ylim, i + 1)
    else:
        print(f"ERROR: i >= 5, exiting!")
        logger.info(f"ERROR: i >= 5, exiting!")
        return _x, _y, modified




def correct_overlap(existing_positions, new_position, offset_increment, logger, xlim, ylim):
    """
    Function that corrects potential date text overlaps
    
    """
    x, y, modified = check_overlap_helper(existing_positions, new_position[0], new_position[1], offset_increment, logger, xlim, ylim)

    if modified:
        logger.info(f"returning: {(x, y)}, modified:{modified}, original:{new_position}")
        return (x, y)
    
    else:
        logger.info(f"returning: {new_position}, modified:{modified}")
        return new_position



















# def check_overlap_helper(existing_positions, new_x, new_y, offset_increment, logger, xlim, ylim, offset_x=0.0, offset_y=0.0):
#     modified = False
#     print(f"@check_overlap_helper: existing_positions:{existing_positions}, new_x:{new_x}, new_y:{new_y}, offset_increment:{offset_increment}, xlim:{xlim}, ylim:{ylim}, offset_x:{offset_x}, offset_y:{offset_y}")

#     #print(f"new_x:{new_x}, new_y:{new_y}")
#     for x, y in existing_positions:
#         #print(f"\nx:{x}, y:{y}, offset_x:{offset_x}, offset_y:{offset_y}")

#         if new_x == x and new_y == y:

#             if offset_x != 0:
#                 offset_x = 0
#                 offset_y -= offset_increment['y']
#             else:
#                 if offset_increment['x'] + new_x > xlim[1]:
#                     offset_x -= offset_increment['x']
                    
#                 else:
#                     offset_x += offset_increment['x']
                
#             offset_x, offset_y, modified = check_overlap_helper(existing_positions, new_x + offset_x, new_y, offset_increment, logger, xlim, ylim, offset_x, offset_y)
                

#             #print(f"new_x({new_x}) == x({x}), offset_x:{offset_x}")
#             logger.info(f"new_x({new_x}) == x({x}), offset_x:{offset_x}")
#             modified = True
#             return offset_x, offset_y, modified
    
#     return offset_x, offset_y, modified



# def check_overlap(existing_positions, new_position, offset_increment, logger, xlim, ylim):
#     """
#     Check if the new position overlaps with any existing positions.
#     If it does, offset it by offset_increment in the y-direction.

#     ofset increment must be a positive number.
#     """
#     #print(f"@check_overlap: existing_positions:{existing_positions}, new_position:{new_position}, offset_increment:{offset_increment}, xlim:{xlim}, ylim:{ylim}")
#     logger.info(f"@check_overlap: existing_positions:{existing_positions}, new_position:{new_position}, offset_increment:{offset_increment}, xlim:{xlim}, ylim:{ylim}")

#     new_x, new_y = new_position

#     offset_x, offset_y, modified = check_overlap_helper(existing_positions, new_x, new_y, offset_increment, logger, xlim, ylim)

    
        
#         # if new_y == y:
#         # #if abs(new_y - y) > offset_increment['y']:
#         #     if offset_increment['y'] + new_y > ylim[1]:
#         #         offset_y -= offset_increment['y']
#         #     else:
#         #         offset_y += offset_increment['y']
#         #     print(f"new_y({new_y}) == y({y}), offset_y:{offset_y}")
#         #     modified = True




#         # abs_x = abs(new_x - x)
#         # abs_y = abs(new_y - y)
#         # print(f"abs_x:{abs_x}, abs_y:{abs_y}")
#         # if abs_x < offset_increment and abs_y < offset_increment:
#         #     print(f"abs_x < offset_increment and abs_y < offset_increment")
#         #     offset_y -= offset_increment  # Change this line to adjust the direction of the offset
#         #     break
    
#     # final_x = new_x + offset_x
#     # final_y = new_y + offset_y
#     # # Check if the new position is outside the axis limits
#     # if final_x > xlim[1]:
#     #     final_x = new_x - offset_x

#     # elif final_x < xlim[0]:
#     #     final_x = new_x - offset_x
        
#     # if final_y > ylim[1]:
#     #     final_y = new_y - offset_y

#     # elif final_y < ylim[0]:
#     #     final_y = new_y - offset_y
    
   
#     if modified:
#         #print(f"returning: {(new_x + offset_x, new_y + offset_y)}, modified:{modified}, original:{new_position}")
#         logger.info(f"returning: {(new_x + offset_x, new_y + offset_y)}, modified:{modified}, original:{new_position}")
#         return (new_x + offset_x, new_y + offset_y)
   
#     else:
#         #print(f"returning: {new_position}, modified:{modified}")
#         logger.info(f"returning: {new_position}, modified:{modified}")
#         return new_position


def plot_nodule_json_data_combined(nodule_dir, logger):
        
    #read _.json file
    json_file = os.path.join(nodule_dir, '_.json')
    with open(json_file) as f:
        data = json.load(f)
    
    #print(data)

    number_of_entries = len(data)
    #print(f"nodules_dir: {nodule_dir} has {number_of_entries} entries")
    logger.info(f"nodules_dir: {nodule_dir} has {number_of_entries} entries")

    if number_of_entries < 2:
        logger.info(f"nodules_dir: {nodule_dir} has less than 2 entries, skipping")
        #print(f"nodules_dir: {nodule_dir} has less than 2 entries, skipping")
        return

    # Initialize the lists
    dates = []
    areas = []
    perimeters = []
    diameters = []
    eccentricities = []

    i_s = []
    xs = []
    ys = []
    tqs = []
    dxs = []
    dys = []
    dds = []
    das = []
    dps = []
    des = []
    
    # Loop through the data
    for entry in data:
        e = entry.get('entry', {}).get('e')
        m = entry.get('entry', {}).get('m')
        
        if e is not None and m is not None:
            i_s.append(m.get('i'))
            dates.append(entry.get('date'))
            xs.append(e.get('x'))
            ys.append(e.get('y'))
            areas.append(e.get('a'))
            perimeters.append(e.get('p'))
            diameters.append(e.get('d'))
            eccentricities.append(e.get('e'))
            tqs.append(m.get('p').get('tq'))
            dxs.append(m.get('p').get('dx'))
            dys.append(m.get('p').get('dy'))
            dds.append(m.get('p').get('dd'))
            das.append(m.get('p').get('da'))
            dps.append(m.get('p').get('dp'))
            des.append(m.get('p').get('de'))

    # Make the plots
    fig, axs = plt.subplots(figsize=(12, 12))
    
    # create sizes with areas * 4
    sizes = [a * 4 for a in areas]

    # Plot 1: Tracking Quality
    scatter = axs.scatter(x=xs, y=ys, s=sizes, c=tqs, cmap='RdYlGn')

    # Set alpha level of scatter points
    scatter.set_alpha(0.5)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('% Tracking Quality (TQ) =>  -inf(bad) to 100(good)')


    cm = plt.get_cmap('RdYlGn')
    
    for i in range(len(xs) - 1):
        x_values = np.linspace(xs[i], xs[i + 1], 30)
        y_values = np.linspace(ys[i], ys[i + 1], 30)
        if tqs[i] is not None and tqs[i + 1] is not None:
            tq_values = np.linspace(tqs[i], tqs[i + 1], 30)

            for j in range(len(x_values) - 1):
                color = cm((tq_values[j] - min(tqs)) / (max(tqs) - min(tqs)))
                
                #print(f"j:{j}")

                # every 3rd draw an arrow
                if j == 5 or j == 25:
                    axs.annotate('', xy=(x_values[j+1], y_values[j+1]), xytext=(x_values[j], y_values[j]),
                                arrowprops=dict(arrowstyle='->', lw=1.5, color=color, alpha=0.5, mutation_scale=60))
                else:
                    axs.plot(x_values[j:j+2], y_values[j:j+2], color=color, alpha=0.5)
        else:
            print(f"WARNING: tqs[i] is None or tqs[i + 1] is None!")
            
            # wait for user input
            #input("Press Enter to continue...")


    # Initialize an empty list to hold existing annotation positions
    existing_positions = []

    for i, (m_i, date, x, y, tq, area, perimeter, diameter, eccentricity, dx, dy, dd, da, dp, de) in enumerate(zip(i_s, dates, xs, ys, tqs, areas, perimeters, diameters, eccentricities, dxs, dys, dds, das, dps, des)):
            
        #print which date is being plotted
        #print(f"\n\nPlotting date: {date}")

        logger.info(f"\n\nPlotting date: {date}")

        xlim = axs.get_xlim()
        ylim = axs.get_ylim()

       
        offset_increment_x = (xlim[1] - xlim[0]) / 8
        offset_increment_y = (ylim[1] - ylim[0]) / 18


        offset_increments = {'x':offset_increment_x, 'y':offset_increment_y}

        new_position = correct_overlap(existing_positions, (x, y), offset_increments, logger, xlim, ylim)
        existing_positions.append(new_position)
        
        axs.annotate(date, new_position, textcoords="offset points", xytext=(0, 0), ha='center', fontsize=8)
        stats_str = f"TQ:{tq} I:{m_i} A: {area}\nX:{x} Y:{y} D:{diameter}\nP:{perimeter} E:{eccentricity}\nΔx:{dx} Δy:{dy} Δd:{dd}\nΔa:{da} Δp:{dp} Δe:{de}"
        axs.annotate(stats_str, new_position, textcoords="offset points", xytext=(0, -35), ha='center', fontsize=6)

        axs.set_title('Tracking Quality')
        
    #axs.set_aspect('equal', adjustable='box')
    # Save the first plot
    plt.tight_layout()
    plt.savefig(os.path.join(nodule_dir, 'tq_plot.png'))
    #plt.show(block=True)
    plt.close()

    # Plot 2: Differences
    fig, axs = plt.subplots(figsize=(12, 8))
    axs.plot(dates, dxs, label='dx (Δx) (dif x)')
    axs.plot(dates, dys, label='dy (Δy) (dif y)')
    axs.plot(dates, dds, label='dd (Δd) (diameter)')
    axs.plot(dates, das, label='da (Δa) (area)')
    axs.plot(dates, dps, label='dp (Δp) (perimeter)')
    axs.plot(dates, des, label='de (Δe) (eccentricity)')
    axs.legend()
    axs.set_title("Δ's")
    
    # Save the second plot
    plt.tight_layout()
    plt.savefig(os.path.join(nodule_dir, 'dif_plot.png'))
    #plt.show(block=True)
    plt.close()


def plot_nodule_json_data(nodule_dir, logger):
        
    #read _.json file
    json_file = os.path.join(nodule_dir, '_.json')
    with open(json_file) as f:
        data = json.load(f)
    
    #print(data)

    number_of_entries = len(data)
    #print(f"nodules_dir: {nodule_dir} has {number_of_entries} entries")
    logger.info(f"nodules_dir: {nodule_dir} has {number_of_entries} entries")

    if number_of_entries < 2:
        logger.info(f"nodules_dir: {nodule_dir} has less than 2 entries, skipping")
        #print(f"nodules_dir: {nodule_dir} has less than 2 entries, skipping")
        return

    # Delete old plot if exists
    if os.path.exists(os.path.join(nodule_dir, 'Tracking_Quality_plot.png')):
        os.remove(os.path.join(nodule_dir, 'Tracking_Quality_plot.png'))
    
    if os.path.exists(os.path.join(nodule_dir, 'Differences_plot.png')):
        os.remove(os.path.join(nodule_dir, 'Differences_plot.png'))

    # Make new plot
    plot_nodule_json_data_combined(nodule_dir, logger)


#Example usage:

# logger = Logger('plot_nodule_json_datay').get_logger()

# plot_nodule_json_data("output/crop1000/nodules-last-detected-on/2023-06-07/35", logger)