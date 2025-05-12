from dash import dcc, html
from flask import session
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import matplotlib

# Set matplotlib to use a backend that doesn't require a display
matplotlib.use('Agg')

def get_slides_layout(cache):
    """
    Returns the layout for the Slides visualization with a grid of thumbnails on the left 
    and a larger selected image on the right.
    """
    compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
    if compound_matrix is None:
        raise ValueError("No compound matrix found in cache.")
    
    slices, rows, cols = compound_matrix.shape
    vmax = np.percentile(compound_matrix[compound_matrix != 0], 99)
    
    # Create thumbnail static images
    thumbnails = []
    for i in range(slices):
        # Generate static image using matplotlib - adjust figure settings
        fig, ax = plt.subplots(figsize=(2, 2), dpi=80)
        ax.imshow(compound_matrix[i], cmap='viridis', vmin=0, vmax=vmax)
        ax.axis('off')
        
        # Remove all padding and whitespace
        fig.subplots_adjust(0, 0, 1, 1)  # left, bottom, right, top
        fig.tight_layout(pad=0)
        
        # Convert matplotlib figure to base64 encoded PNG
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, 
                    bbox_inches='tight', pad_inches=0, 
                    facecolor='none', edgecolor='none')
        plt.close(fig)  # Close figure to free memory
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('ascii')
        
        thumbnails.append(
            html.Div(
                html.Img(
                    src=f"data:image/png;base64,{img_str}",
                    # id=f'thumbnail-img-{i}',
                    id={'type': 'thumbnail-img', 'index': i},
                    className='slide-thumbnail-image',
                    key=f"{i}-viridis"
                ),
                className='thumbnail-container', 
                id=f'thumbnail-container-{i}'
            )
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
                className="colormap-radio",
                inline=True
            )
        ], className="slides-controls"),
        
        # Main content area with thumbnails and selected image
        html.Div([
            # Left column - Thumbnails grid with loading spinner
            html.Div([
                dcc.Loading(
                    id="loading-thumbnails",
                    type="circle",
                    children=html.Div(thumbnails, className='thumbnails-grid', id='thumbnails-grid'),
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"}
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