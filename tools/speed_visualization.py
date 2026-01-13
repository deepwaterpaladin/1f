from typing import Dict, List
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import plotly.graph_objects as go
import fastf1


gp_arr: List[str] = [
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

session_dict: Dict[str, str] = {
    "FP1": "Free Practice 1",
    "FP2": "Free Practice 2",
    "FP3": "Free Practice 3",
    "SQ": "Sprint Qualifying",
    "SR": "Sprint Race",
    "Q": "Qualifying",
    "R": "Grand Prix"
}


def plot_fastest_lap(year: int, gp: str | int, ses: str, driver: str) -> None:
    """
    Creates a matplotlib visualization of a driver's fastest lap with speed data.
    
    This function generates a track map colored by speed, where the color gradient
    represents the speed at each point on the track. Uses matplotlib with a plasma
    colormap (reversed) where yellow indicates slower speeds and purple indicates
    faster speeds.
    
    Args:
        year: The Formula 1 season year (e.g., 2023, 2024).
        gp: Grand Prix identifier, either:
            - str: Event name (e.g., "Monaco", "Singapore")
            - int: Round number (1-indexed, e.g., 1 for first race)
        ses: Session code from session_dict keys:
            - "FP1", "FP2", "FP3": Free Practice sessions
            - "SQ": Sprint Qualifying
            - "SR": Sprint Race
            - "Q": Qualifying
            - "R": Grand Prix (main race)
        driver: Three-letter driver code (e.g., "VER", "HAM", "LEC").
    
    Returns:
        None. Displays the plot using plt.show().
    
    Notes:
        - The plot shows the track layout with a thick black outline
        - Speed is visualized using the plasma_r colormap
        - A horizontal colorbar shows the speed scale
        - The function loads full telemetry data, which may take time
    
    Example:
        >>> plot_fastest_lap(2024, "Monaco", "Q", "VER")
        >>> plot_fastest_lap(2024, 6, "R", "HAM")  # 6th race of the season
    """
    colormap: mpl.colors.Colormap = mpl.cm.plasma_r
    session: fastf1.core.Session = fastf1.get_session(year, gp, ses)
    weekend: fastf1.events.Event = session.event
    sess: str = session_dict[ses]
    
    if type(gp) == str:
        name: str = gp
    else:
        name: str = gp_arr[gp - 1]
    
    session.load()
    lap: fastf1.core.Lap = session.laps.pick_drivers(driver).pick_fastest()

    x: np.ndarray = lap.telemetry['X'].to_numpy()
    y: np.ndarray = lap.telemetry['Y'].to_numpy()
    color: np.ndarray = lap.telemetry['Speed'].to_numpy()

    points: np.ndarray = np.array([x, y]).T.reshape(-1, 1, 2)
    segments: np.ndarray = np.concatenate([points[:-1], points[1:]], axis=1)
    
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'{year} {name} {sess} - {driver} - Speed', size=24, y=0.97)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
            color='black', linestyle='-', linewidth=16, zorder=0)

    norm: mpl.colors.Normalize = plt.Normalize(color.min(), color.max())
    lc: LineCollection = LineCollection(segments, cmap=colormap, norm=norm,
                                        linestyle='-', linewidth=5)

    lc.set_array(color)

    line: LineCollection = ax.add_collection(lc)

    cbaxes: Axes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend: mpl.colors.Normalize = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend: mpl.colorbar.ColorbarBase = mpl.colorbar.ColorbarBase(
        cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal"
    )

    plt.show()


def plot_fastest_lap_plotly(year: int, gp: str | int, ses: str, driver: str) -> None:
    """
    Creates an interactive Plotly visualization of a driver's fastest lap with speed data.
    
    This function generates an interactive track map where markers are colored by speed.
    Uses the reversed Plasma colorscale where yellow indicates slower speeds and purple
    indicates faster speeds. The plot is interactive, allowing zooming, panning, and
    hover to see exact speed values.
    
    Args:
        year: The Formula 1 season year (e.g., 2023, 2024).
        gp: Grand Prix identifier, either:
            - str: Event name (e.g., "Monaco", "Singapore")
            - int: Round number (1-indexed, e.g., 1 for first race)
        ses: Session code from session_dict keys:
            - "FP1", "FP2", "FP3": Free Practice sessions
            - "SQ": Sprint Qualifying
            - "SR": Sprint Race
            - "Q": Qualifying
            - "R": Grand Prix (main race)
        driver: Three-letter driver code (e.g., "VER", "HAM", "LEC").
    
    Returns:
        None. Displays the interactive plot using fig.show().
    
    Notes:
        - Uses Plotly for interactive visualization
        - Hover over any point to see exact speed
        - Colorscale: Plasma_r (yellow=slow, purple=fast)
        - Maintains aspect ratio for accurate track representation
        - The function loads full telemetry data, which may take time
    
    Example:
        >>> plot_fastest_lap_plotly(2024, "Monaco", "Q", "VER")
        >>> plot_fastest_lap_plotly(2024, 6, "R", "HAM")  # 6th race
    """
    session: fastf1.core.Session = fastf1.get_session(year, gp, ses)
    sess: str = session_dict[ses]
    
    if type(gp) == str:
        name: str = gp
    else:
        name: str = gp_arr[gp - 1]
    
    session.load()
    lap: fastf1.core.Lap = session.laps.pick_drivers(driver).pick_fastest()

    x: np.ndarray = lap.telemetry['X'].to_numpy()
    y: np.ndarray = lap.telemetry['Y'].to_numpy()
    speed: np.ndarray = lap.telemetry['Speed'].to_numpy()

    fig: go.Figure = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+lines',
        line=dict(
            color='rgba(0,0,0,0.3)',
            width=2
        ),
        marker=dict(
            color=speed,
            colorscale='Plasma_r',  # Reversed: yellow=slow, purple=fast
            size=8,
            colorbar=dict(
                title="Speed (km/h)",
                thickness=20,
                len=0.7
            ),
            line=dict(width=0)
        ),
        hovertemplate='Speed: %{marker.color:.1f} km/h<extra></extra>',
        showlegend=False
    ))

    fig.update_layout(
        title=dict(
            text=f'{year} {name} {sess} - {driver} - Speed',
            x=0.5,
            xanchor='center',
            font=dict(size=24)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            visible=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        plot_bgcolor='white',
        width=1200,
        height=675,
        hovermode='closest'
    )

    fig.show()