import json
import os
import matplotlib.pyplot as plt
import numpy as np
import json


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
            input("Press Enter to continue...")

    for i, (m_i, date, x, y, tq, area, perimeter, diameter, eccentricity, dx, dy, dd, da, dp, de) in enumerate(zip(i_s, dates, xs, ys, tqs, areas, perimeters, diameters, eccentricities, dxs, dys, dds, das, dps, des)):
        axs.annotate(date, (x, y), textcoords="offset points", xytext=(0, 0), ha='center', fontsize=8)
        stats_str = f"TQ:{tq} I:{m_i} A: {area}\nX:{x} Y:{y} D:{diameter}\nP:{perimeter} E:{eccentricity}\nΔx:{dx} Δy:{dy} Δd:{dd}\nΔa:{da} Δp:{dp} Δe:{de}"
        axs.annotate(stats_str, (x, y), textcoords="offset points", xytext=(0, -35), ha='center', fontsize=6)
    
    axs.set_title('Tracking Quality')
    
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