from dash import Output, Input, State, callback, dcc, html
import dash
from flask import session
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

def register_slides_callback(app, cache):
    @app.callback(
        Output("loading-thumbnails", "children"),
        Input("colormap-selection", "value"),
        prevent_initial_call=True,
    )
    def update_colormap(colormap):
        compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
        if compound_matrix is None:
            raise ValueError("No compound matrix found in cache.")
        
        slices, rows, cols = compound_matrix.shape
        vmax = np.percentile(compound_matrix[compound_matrix != 0], 99)
        thumbnails = []
        for i in range(slices):
            # Generate static image using matplotlib - adjust figure settings
            fig, ax = plt.subplots(figsize=(2, 2), dpi=80)
            ax.imshow(compound_matrix[i], cmap=colormap, vmin=0, vmax=vmax)
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
                        id=f'thumbnail-img-{i}',
                        className='slide-thumbnail-image'
                    ),
                    className='thumbnail-container', 
                    id=f'thumbnail-container-{i}'
                )
            )
            
        return html.Div(thumbnails, className='thumbnails-grid')