from dash import Output, Input, State, callback, dcc, html, ALL
import dash
from flask import session
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import logging
from plotly import express as px
import time

logger = logging.getLogger("metavision")

def register_slides_callback(app, cache):
    @app.callback(
        Output("thumbnails-grid", "children"),
        Input("colormap-selection", "value"),
        prevent_initial_call=True,
    )
    def update_colormap(colormap):
        compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
        if compound_matrix is None:
            raise ValueError("No compound matrix found in cache.")
        
        # Use a more robust cache-busting approach
        timestamp = int(time.time() * 1000)  # Millisecond precision
        
        slices, rows, cols = compound_matrix.shape
        vmax = np.percentile(compound_matrix[compound_matrix != 0], 99)
        thumbnails = []
        for i in range(slices):
            # Generate static image using matplotlib with the selected colormap
            fig, ax = plt.subplots(figsize=(2, 2), dpi=80)
            ax.imshow(compound_matrix[i], cmap=colormap, vmin=0, vmax=vmax)
            ax.axis('off')
            
            # Remove all padding and whitespace
            fig.subplots_adjust(0, 0, 1, 1)
            fig.tight_layout(pad=0)
            
            # Convert matplotlib figure to base64 encoded PNG
            buf = io.BytesIO()
            fig.savefig(buf, format='png', transparent=True, 
                        bbox_inches='tight', pad_inches=0, 
                        facecolor='none', edgecolor='none')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('ascii')
            
            # Add container class that indicates the active colormap
            container_class = f'thumbnail-container colormap-{colormap}'
            
            # Add unique timestamp per request to each image URL
            thumbnails.append(
                html.Div(
                    html.Img(
                        src=f"data:image/png;base64,{img_str}#{timestamp}-{i}",  # Use # instead of ?
                        id={'type': 'thumbnail-img', 'index': i},
                        className='slide-thumbnail-image',
                        key=f"{i}-{colormap}"
                    ),
                    className=container_class,
                    id=f'thumbnail-container-{i}'
                )
            )
        
        # Log to verify callback is running
        logger.info(f"Updated thumbnails with colormap: {colormap}")
        
        return thumbnails
    
    
    @app.callback(
        Output("selected-slide-display", "children"),
        Input({"type": "thumbnail-img", "index": ALL}, "n_clicks"),
        State({"type": "thumbnail-img", "index": ALL}, "id"),
        State("colormap-selection", "value"),
        prevent_initial_call=True,
    )
    def display_plotly_fig(clicks, ids, colormap):
        # Find which thumbnail was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            return html.Div("Click on a thumbnail to view details", className="select-instruction")
            
        # Get the ID of the clicked element
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        clicked_id = eval(triggered_id)
        clicked_index = clicked_id['index']
        
        compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
        if compound_matrix is None:
            return html.Div("Error: Data not available", className="error-message")
            
        # Get the corresponding slice from the compound matrix
        selected_slice = compound_matrix[clicked_index]
        
        # Create a Plotly figure with proper styling
        fig = px.imshow(
            selected_slice, 
            color_continuous_scale=colormap,
            zmin=0,
            zmax=np.percentile(compound_matrix[compound_matrix != 0], 99)
        )
        
        # Update layout with dark theme styling
        fig.update_layout(
        title={
            'text': f"Slice {clicked_index + 1}",
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
        }
    )
        
        # Add light grid to better show the image structure
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
        
        # Mark the selected thumbnail with a different border
        return dcc.Graph(
            id="selected-slide-graph",
            figure=fig,
            config={"displayModeBar": True},
            className="selected-slide-graph"
        )