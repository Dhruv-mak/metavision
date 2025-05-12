from dash import Output, Input, State, dcc, html
import plotly.graph_objects as go
import numpy as np
from flask import session
import base64
import io
import logging
import nibabel as nib
from scipy.ndimage import zoom
import plotly.express as px
from dash.exceptions import PreventUpdate
import os
import tempfile

logger = logging.getLogger("metavision")

class MetaAtlas3D:
    def __init__(self, matrix, resolution, thickness, gap, insert):
        self.matrix = matrix
        self.resolution = resolution
        self.thickness = thickness
        self.gap = gap
        self.insert = insert
        
    def create_nii(self):
        # reshape matrix from (z,y,x) to (x,y,z)
        output_matrix = np.transpose(self.matrix,(2,1,0))
        Ir = np.squeeze(output_matrix)
        img = nib.Nifti1Image(Ir, affine=np.eye(4))
        # adjust thickness
        header = img.header.copy()
        header['pixdim'][3] = (self.thickness+self.gap)/((1+self.insert)*self.resolution)
    
        nii_img = nib.Nifti1Image(Ir, affine=np.eye(4), header=header)
        return nii_img

def create_nii(matrix, resolution, thickness, gap, insert=0):
    # resolution: MALDI resolution (x-y axis); section thickness; gap between adjacent sections; number of inserted sections
    # reshape matrix from (z,y,x) to (x,y,z)
    output_matrix = np.transpose(matrix,(2,1,0))
    Ir = np.squeeze(output_matrix)
    img = nib.Nifti1Image(Ir, affine=np.eye(4))
    # adjust thickness
    header = img.header.copy()
    header['pixdim'][3] = (thickness+gap)/((1+insert)*resolution)

    nii_img = nib.Nifti1Image(Ir, affine=np.eye(4), header=header)
    return nii_img

def create_3d_figure(compound_matrix, projection_type, thickness, gap, max_projection):
    """
    Creates a 3D visualization figure using Plotly with inverted grayscale and no grid
    """
    slices, rows, cols = compound_matrix.shape
    
    # Apply maximum intensity projection if selected
    if projection_type == 'maximum':
        # Apply maximum projection with the selected percentile
        threshold = np.percentile(compound_matrix, max_projection)
        volume_data = np.where(compound_matrix > threshold, compound_matrix, 0)
    else:
        volume_data = compound_matrix
    
    # Create x, y, z coordinates for the volume
    x = np.linspace(0, cols-1, cols)
    y = np.linspace(0, rows-1, rows)
    z = np.linspace(0, slices-1, slices)
    
    # Account for thickness and gap
    z = z * (thickness + gap)
    
    # Create a figure for 3D volume
    fig = go.Figure()
    
    # Normalize data for better visualization
    max_val = np.max(volume_data)
    if max_val > 0:
        normalized_data = volume_data / max_val
    else:
        normalized_data = volume_data
    
    # Create inverted grayscale colormap (high intensity = dark)
    # White (0) to black (1)
    custom_colorscale = [
        [0, 'rgb(255, 255, 255)'],  # White for low values
        [1, 'rgb(0, 0, 0)']          # Black for high values
    ]
    
    # Iterate through slices to create surfaces
    for i in range(slices):
        # Create 3D surface with inverted grayscale coloring and no grid
        fig.add_trace(go.Surface(
            z=np.ones((rows, cols)) * z[i],
            x=x,
            y=y,
            surfacecolor=normalized_data[i],
            colorscale=custom_colorscale,  # Inverted grayscale
            opacity=0.9,  # Slightly higher opacity for better visibility
            showscale=(i == 0),  # Only show colorbar for the first surface
            colorbar=dict(
                title=dict(
                    text='Intensity',
                    font=dict(color='white')
                ),
                tickfont=dict(color='white')
            ),
            # Remove all contours/grid lines
            contours=dict(
                x=dict(show=False),
                y=dict(show=False),
                z=dict(show=False)
            ),
            lighting=dict(
                ambient=0.7,    # Increased ambient light for better visibility
                diffuse=0.9,    # Increased diffuse light
                fresnel=0.1,    # Reduced fresnel effect further
                specular=0.3,   # Reduced specular highlights
                roughness=0.7   # Increased roughness for less shiny appearance
            )
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '3D Brain Visualization',
            'font': {'color': 'white', 'size': 18},
            'y': 0.95,
        },
        scene=dict(
            xaxis=dict(
                title='X',
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='grey',
                showbackground=True,
                zerolinecolor='white',
                showspikes=False,
                showgrid=False,  # Hide grid
                zeroline=False,  # Hide zero line
            ),
            yaxis=dict(
                title='Y',
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='grey',
                showbackground=True,
                zerolinecolor='white',
                showspikes=False,
                showgrid=False,  # Hide grid
                zeroline=False,  # Hide zero line
            ),
            zaxis=dict(
                title='Z',
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='grey',
                showbackground=True,
                zerolinecolor='white',
                showspikes=False,
                showgrid=False,  # Hide grid
                zeroline=False,  # Hide zero line
            ),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)  # Adjusted camera angle for better view
            ),
        ),
        height=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, b=0, t=50),
        updatemenus=[{
            'buttons': [
                {
                    'args': ['scene.camera.eye', {'x': 1.5, 'y': 1.5, 'z': 1.2}],
                    'label': 'Default View',
                    'method': 'relayout'
                },
                {
                    'args': ['scene.camera.eye', {'x': 0, 'y': 0, 'z': 2.5}],
                    'label': 'Top View',
                    'method': 'relayout'
                },
                {
                    'args': ['scene.camera.eye', {'x': 2.5, 'y': 0, 'z': 0}],
                    'label': 'Side View',
                    'method': 'relayout'
                }
            ],
            'direction': 'down',
            'pad': {'r': 10, 't': 10},
            'showactive': True,
            'type': 'buttons',
            'x': 0.9,
            'y': 1.1,
            'xanchor': 'right',
            'yanchor': 'top',
            'bgcolor': 'rgba(45, 45, 45, 0.8)',
            'font': {'color': 'white'}
        }]
    )
    
    return fig
def register_3d_callback(app, cache):
    # Callback to show/hide the max projection dropdown based on projection type selection
    @app.callback(
        Output("max-projection-container", "style"),
        Input("projection-type", "value")
    )
    def toggle_max_projection(projection_type):
        if projection_type == 'maximum':
            return {'display': 'block'}
        return {'display': 'none'}
    
    # Callback to view the 3D visualization
    @app.callback(
        Output("3d-visualization-container", "children"),
        Input("view-3d-button", "n_clicks"),
        State("thickness-value", "value"),
        State("gap-value", "value"),
        State("max-projection-value", "value"),
        State("projection-type", "value"),
        prevent_initial_call=True
    )
    def view_3d(n_clicks, thickness, gap, max_projection, projection_type):
        if not n_clicks:
            raise PreventUpdate
        
        # Get compound matrix data from cache
        try:
            compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
            if compound_matrix is None:
                return html.Div("No data available for 3D visualization.", className="error-message")
            
            # Create 3D figure
            fig = create_3d_figure(compound_matrix, projection_type, thickness, gap, max_projection)
            
            # Return the 3D visualization
            return dcc.Graph(
                id='3d-brain-graph',
                figure=fig,
                style={'height': '700px'},
                config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'responsive': True
                }
            )
        
        except Exception as e:
            logger.error(f"Error creating 3D visualization: {str(e)}")
            return html.Div([
                html.H4("Error Creating 3D Visualization", style={'color': '#f44336'}),
                html.P(f"Details: {str(e)}")
            ], className="visualization-error")
    
    # Callback to download the 3D NIfTI image
    @app.callback(
        Output("download-3d-image", "data"),
        Input("save-3d-button", "n_clicks"),
        State("thickness-value", "value"),
        State("gap-value", "value"),
        prevent_initial_call=True
    )
    def download_3d_image(n_clicks, thickness, gap):
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get compound matrix from cache
            compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
            if compound_matrix is None:
                raise PreventUpdate
            
            # Create NIfTI file
            resolution = 1  # Default resolution
            slices = 0      # Default insert value
            
            # Create NIfTI object
            atlas_data = MetaAtlas3D(compound_matrix, resolution, thickness, gap, slices)
            nii_data = atlas_data.create_nii()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.nii', delete=False) as tmp:
                temp_path = tmp.name
            
            try:
                # Save NIfTI data to the temporary file
                nib.save(nii_data, temp_path)
                
                # Read the file back into memory
                with open(temp_path, 'rb') as f:
                    file_data = f.read()
                
                # Generate a base64 string from the data
                nii_data_b64 = base64.b64encode(file_data).decode('utf-8')
                
                # Return as download
                filename = f"brain_3d_t{thickness}_g{gap}.nii"
                return dict(
                    content=nii_data_b64,
                    filename=filename,
                    type="application/octet-stream"
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Error generating NIfTI file: {str(e)}")
            raise PreventUpdate