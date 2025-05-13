from dash import Output, Input, State, callback, dcc, html, ALL
from flask import session
import numpy as np
import plotly.graph_objects as go
import logging

logger = logging.getLogger("metavision")

def get_animation_layout(cache):
    compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
    if compound_matrix is None:
        return html.Div("No data available for animation.", className="error-message")
    
    # Get the dimensions of the compound matrix
    slices, rows, cols = compound_matrix.shape
    logger.info(f"Creating heatmap viewer with {slices} slices of {rows}x{cols} data")
    
    # Calculate a good vmax value for color scaling (99th percentile of non-zero values)
    vmax = np.percentile(compound_matrix[compound_matrix != 0], 99)
    
    # Create a figure for the visualization
    fig = go.Figure()
    
    # Calculate aspect ratio based on data dimensions to prevent stretching
    aspect_ratio = cols / rows
    
    # Add all slices as frames
    frames = []
    for i in range(slices):
        frames.append(
            go.Frame(
                data=[go.Heatmap(
                    z=compound_matrix[i], 
                    colorscale='magma',
                    zmin=0,
                    zmax=vmax
                )],
                name=f"slice_{i+1}"
            )
        )
    
    # Add the first slice as the initial display
    fig.add_trace(
        go.Heatmap(
            z=compound_matrix[0], 
            colorscale='magma',
            zmin=0,
            zmax=vmax
        )
    )
    
    # Configure frame settings
    fig.frames = frames
    
    # Add slider for slice navigation
    fig.update_layout(
        title={
            'text': "Slice Viewer",
            'font': {'color': 'white', 'size': 18},
            'y': 0.95
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_colorbar={
            'title': {
                'text': "Intensity",
                'font': {'color': 'white'}
            },
            'tickfont': {'color': 'white'}
        },
        # Set the aspect ratio to maintain proper proportions
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,  # 1:1 aspect ratio
        ),
        # Adjust height based on width and aspect ratio
        autosize=True,
        height=700,  # Increase base height
        sliders=[
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 16, "color": "white"},
                    "prefix": "Slice: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 100, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [
                            [f"slice_{i+1}"],
                            {
                                "frame": {"duration": 100, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 100}
                            }
                        ],
                        "label": str(i+1),
                        "method": "animate"
                    }
                    for i in range(slices)
                ],
                "tickcolor": "white",
                "font": {"color": "white"}
            }
        ]
    )
    
    # Disable grids and axes labels
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    
    # Create the visualization container
    animation_layout = html.Div([
        html.H3("Data Slices", className="section-title"),
        html.P("Navigate through slices of data using the slider below. Each slice is shown as a heatmap with magma colormap.", 
               className="section-description"),
        
        dcc.RadioItems(
            id="colormap-selection-animation",
            options=[
                {'label': 'Viridis', 'value': 'viridis'},
                {'label': 'Magma', 'value': 'magma'},
                {'label': 'Plasma', 'value': 'plasma'},
                {'label': 'Cividis', 'value': 'cividis'}
            ],
            value='magma',
            className="colormap-selection",
            inputClassName="radio-input",
            labelClassName="radio-label",
            inputStyle={"margin-right": "5px"},
            labelStyle={"display": "inline-flex", "align-items": "center", "margin-right": "20px"},
        ),
        
        # Main graph
        dcc.Graph(
            id="animation-graph",
            figure=fig,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'responsive': True
            },
            className="animation-graph"
        )
        
    ], id="animation-container", className="animation-container")
    
    return animation_layout