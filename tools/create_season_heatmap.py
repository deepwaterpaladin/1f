from typing import List, Dict, Any
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import fastf1

def create_season_heatmap(year: int) -> go.Figure:
    """
    Creates a heatmap visualization of F1 driver points for a given season.
    Handles mid-season cases by skipping races that haven't occurred yet (not ideal but workable for now).
    
    Args:
        year: The season year to visualize
        
    Returns:
        A Plotly figure object containing the heatmap
    """
    
    schedule: pd.DataFrame = fastf1.get_event_schedule(year, include_testing=False)
    standings: List[Dict[str, Any]] = []
    short_event_names: List[str] = []

    for _, event in schedule.iterrows():
        event_name: str = event["EventName"]
        round_number: int = event["RoundNumber"]
        
        try:
            race = fastf1.get_session(year, event_name, "R")
            race.load(laps=False, telemetry=False, weather=False, messages=False)
            
            if race.results is None or race.results.empty:
                continue
                
        except Exception as e:
            continue  # Skipping races that haven't happened yet (we can handle another way)
        
        short_event_names.append(event_name.replace("Grand Prix", "").strip())

        sprint = None
        sprint_points_dict: Dict[str, float] = {}
        
        if event["EventFormat"] == "sprint_qualifying":
            try:
                sprint = fastf1.get_session(year, event_name, "S")
                sprint.load(laps=False, telemetry=False, weather=False, messages=False)
                
                if sprint.results is not None and not sprint.results.empty:
                    for _, sprint_row in sprint.results.iterrows():
                        sprint_points_dict[sprint_row["Abbreviation"]] = sprint_row["Points"]
            except Exception:
                pass

        for _, driver_row in race.results.iterrows():
            abbreviation: str = driver_row["Abbreviation"]
            race_points: float = driver_row["Points"]
            race_position: int = driver_row["Position"]

            sprint_points: float = sprint_points_dict.get(abbreviation, 0)

            standings.append(
                {
                    "EventName": event_name,
                    "RoundNumber": round_number,
                    "Driver": abbreviation,
                    "Points": race_points + sprint_points,
                    "Position": race_position,
                }
            )

    if not standings:
        raise ValueError(f"No race data available for {year} season yet")

    df: pd.DataFrame = pd.DataFrame(standings)
    heatmap_data: pd.DataFrame = df.pivot(
        index="Driver", columns="RoundNumber", values="Points"
    ).fillna(0)

    heatmap_data["total_points"] = heatmap_data.sum(axis=1)
    heatmap_data = heatmap_data.sort_values(by="total_points", ascending=True)
    total_points = heatmap_data["total_points"].values
    heatmap_data = heatmap_data.drop(columns=["total_points"])
    
    position_data: pd.DataFrame = df.pivot(
        index="Driver", columns="RoundNumber", values="Position"
    ).fillna("N/A")

    hover_info: List[List[Dict[str, Any]]] = [
        [
            {
                "position": position_data.at[driver, race],
            }
            for race in heatmap_data.columns
        ]
        for driver in heatmap_data.index
    ]
    
    fig: go.Figure = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.85, 0.15],
        subplot_titles=(f"F1 {year} Season Summary", "Total Points"),
    )
    fig.update_layout(width=900, height=800)

    fig.add_trace(
        go.Heatmap(
            x=short_event_names,
            y=heatmap_data.index,
            z=heatmap_data.values,
            text=heatmap_data.values,
            texttemplate="%{text}",
            textfont={"size": 12},
            customdata=hover_info,
            hovertemplate=(
                "Driver: %{y}<br>"
                "Race Name: %{x}<br>"
                "Points: %{z}<br>"
                "Position: %{customdata.position}<extra></extra>"
            ),
            colorscale="YlGnBu",
            showscale=False,
            zmin=0,
            zmax=heatmap_data.values.max() if heatmap_data.values.max() > 0 else 1,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Heatmap(
            x=["Total Points"] * len(total_points),
            y=heatmap_data.index,
            z=total_points,
            text=total_points,
            texttemplate="%{text}",
            textfont={"size": 12},
            colorscale="YlGnBu",
            showscale=False,
            zmin=0,
            zmax=total_points.max() if total_points.max() > 0 else 1,
        ),
        row=1,
        col=2,
    )

    return fig