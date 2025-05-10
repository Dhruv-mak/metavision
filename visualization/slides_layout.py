from dash import dcc, html
from flask import session
import math
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import base64
from PIL import Image

def get_slides_layout(cache):
    """
    Returns the layout for the Slides visualization with a grid of thumbnails on the left 
    and a larger selected image on the right.
    """
    compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
    if compound_matrix is None:
        raise ValueError("No compound matrix found in cache.")
    
    slices, rows, cols = compound_matrix.shape
    N = round(math.sqrt(slices))
    vmax = np.percentile(compound_matrix[compound_matrix != 0], 99)
    
    # Create thumbnail figures
    thumbnails = []
    for i in range(slices):
        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=compound_matrix[i],
                colorscale='Viridis',
                showscale=False,
                zmin=0,
                zmax=vmax
            )
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=120,
            width=120,
        )
        
        thumbnails.append(
            html.Div([
                dcc.Graph(
                    figure=fig,
                    config={'displayModeBar': False},
                    id=f'thumbnail-{i}',
                    className='slide-thumbnail'
                ),
                html.Div(f"Slice {i+1}", className='thumbnail-label')
            ], className='thumbnail-container', id=f'thumbnail-container-{i}')
        )

    return html.Div([
        # Controls for colormap selection
        html.Div([
            html.Label("Colormap:", className="control-label"),
            dcc.RadioItems(
                id='colormap-selection',
                options=[
                    {'label': 'Viridis', 'value': 'viridis'},
                    {'label': 'Magma', 'value': 'magma'},
                    {'label': 'Grayscale', 'value': 'gray'}
                ],
                value='viridis',
                className="colormap-radio"
            )
        ], className="slides-controls"),
        
        # Main content area with thumbnails and selected image
        html.Div([
            # Left column - Thumbnails grid with loading spinner
            html.Div([
                dcc.Loading(
                    id="loading-thumbnails",
                    type="circle",
                    children=html.Div(thumbnails, className='thumbnails-grid')
                )
            ], className='thumbnails-column'),
            
            # Right column - Selected image with loading spinner
            html.Div([
                dcc.Loading(
                    id="loading-selected-image",
                    type="circle",
                    children=html.Div([
                        html.Div("Click on a thumbnail to view details", className="select-instruction"),
                        html.Div(id="selected-slide-display")
                    ], className='selected-slide-container')
                )
            ], className='selected-column')
        ], className='slides-content'),
        
        # Hidden div to store currently selected slice index
        dcc.Store(id='selected-slice', data=0),
        
        # Hidden div to store compound matrix shape info
        dcc.Store(id='matrix-info', data={
            'slices': slices,
            'rows': rows,
            'cols': cols,
            'vmax': vmax
        })
    ], className='slides-layout')