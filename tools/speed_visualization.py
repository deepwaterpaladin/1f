import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

import fastf1

gp_arr = [
    "Australia",
    "China",
    "Japan",
    "Bahrain",
    "Saudi Arabia",
    "Miami",
    "Emilia Romagna",
    "Monaco",
    "Spain",
    "Canada",
    "Austria",
    "Great Britain",
    "Belgium",
    "Hungary",
    "Netherlands",
    "Italy",
    "Azerbaijan",
    "Singapore",
    "United States",
    "Mexico",
    "Brazil",
    "Las Vegas",
    "Qatar",
    "Abu Dhabi"
]

session_dict = {
    "FP1":"Free Practice 1",
    "FP2":"Free Practice 2",
    "FP3":"Free Practice 3",
    "SQ":"Sprint Qualifying",
    "SR":"Sprint Race",
    "Q":"Qualifying",
    "R":"Grand Prix"
}

def plot_fastest_lap(year: int, gp: str | int,  ses:str, driver:str):
    colormap = mpl.cm.plasma_r
    session = fastf1.get_session(year, gp, ses)
    weekend = session.event
    sess = session_dict[ses]
    if type(gp) == str:
        name = gp
    else:
        name = gp_arr[gp-1]
    session.load()
    lap = session.laps.pick_drivers(driver).pick_fastest()

    x = lap.telemetry['X']             
    y = lap.telemetry['Y']              
    color = lap.telemetry['Speed']

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'{year} {name} {sess} - {driver} - Speed', size=24, y=0.97)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
            color='black', linestyle='-', linewidth=16, zorder=0)

    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm,
                        linestyle='-', linewidth=5)

    lc.set_array(color)

    line = ax.add_collection(lc)

    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap,
                                    orientation="horizontal")

    plt.show()