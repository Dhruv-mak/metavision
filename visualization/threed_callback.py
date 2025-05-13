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
    Creates a 3D point cloud visualization with proper slice thickness and gaps
    """
    slices, rows, cols = compound_matrix.shape
    
    # Apply maximum intensity projection if selected
    if projection_type == 'maximum':
        threshold = np.percentile(compound_matrix, max_projection) / 100
    else:
        threshold = 0.15
    
    # Normalize data
    max_val = np.max(compound_matrix)
    if max_val > 0:
        normalized_data = compound_matrix / max_val
    else:
        normalized_data = compound_matrix
    
    # For point cloud with true thickness, we need to create multiple z-positions for each slice
    points_x = []
    points_y = []
    points_z = []
    point_values = []
    
    # Identify points above threshold
    for z_idx in range(slices):
        slice_data = normalized_data[z_idx]
        mask = slice_data > threshold
        y_coords, x_coords = np.nonzero(mask)
        values = slice_data[mask]
        
        if len(x_coords) > 0:
            # Calculate base z position for this slice
            base_z = z_idx * (1 + gap)  # Base position with gap
            
            # For each point in this slice, create multiple points through the thickness
            if thickness <= 1:
                # For thickness <= 1, just use a single layer of points
                points_x.extend(x_coords)
                points_y.extend(y_coords)
                points_z.extend([base_z] * len(x_coords))
                point_values.extend(values)
            else:
                # For thickness > 1, create multiple z-layers to represent thickness
                # Number of layers based on thickness (at least 2 for thickness > 1)
                num_layers = max(2, int(thickness))
                
                # Create points at different z-positions within the slice thickness
                for layer in range(num_layers):
                    z_pos = base_z + (layer * (thickness / num_layers))
                    points_x.extend(x_coords)
                    points_y.extend(y_coords)
                    points_z.extend([z_pos] * len(x_coords))
                    point_values.extend(values)
    
    # Convert to numpy arrays
    points_x = np.array(points_x)
    points_y = np.array(points_y)
    points_z = np.array(points_z)
    point_values = np.array(point_values)
    
    # Limit points if necessary to avoid browser performance issues
    max_points = 100000
    if len(points_x) > max_points:
        indices = np.random.choice(len(points_x), max_points, replace=False)
        points_x = points_x[indices]
        points_y = points_y[indices]
        points_z = points_z[indices]
        point_values = point_values[indices]
    
    # Create the figure with point cloud
    fig = go.Figure(data=go.Scatter3d(
        x=points_x, y=points_y, z=points_z,
        mode='markers',
        marker=dict(
            size=2,
            color=point_values,
            colorscale='Greys_r',
            opacity=0.8
        ),
        hoverinfo='none'
    ))
    
    # Clean layout with no axes or borders
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
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