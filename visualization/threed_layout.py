from dash import html, dcc

def get_3d_image_layout():
    """
    Returns the layout for the 3D image visualization options with side-by-side parameters.
    """
    return html.Div([
        # Projection type radio buttons
        html.Div([
            html.Label("Projection Type:", className="control-label"),
            dcc.RadioItems(
                id='projection-type',
                options=[
                    {'label': 'Original', 'value': 'original'},
                    {'label': 'Maximum', 'value': 'maximum'}
                ],
                value='original',
                inline=True,
                className="radio-group"
            )
        ], className="control-group"),
        
        # Compact layout with labels and dropdowns side by side
        html.Div([
            # Three controls in a row with minimal spacing
            html.Div([
                # Thickness control
                html.Div([
                    html.Label("Thickness:", className="compact-label"),
                    dcc.Dropdown(
                        id='thickness-value',
                        options=[{'label': str(i), 'value': i} for i in range(1, 11)],
                        value=1,
                        clearable=False,
                        className="compact-dropdown"
                    ),
                ], className="compact-control"),
                
                # Gap control
                html.Div([
                    html.Label("Gap:", className="compact-label"),
                    dcc.Dropdown(
                        id='gap-value',
                        options=[{'label': str(i), 'value': i} for i in range(10)],
                        value=0,
                        clearable=False,
                        className="compact-dropdown"
                    ),
                ], className="compact-control"),
                
                # Maximum projection control
                html.Div([
                    html.Label("Maximum Projection:", className="compact-label"),
                    dcc.Dropdown(
                        id='max-projection-value',
                        options=[{'label': str(i), 'value': i} for i in range(100, 0, -1)],
                        value=99,
                        clearable=False,
                        className="compact-dropdown"
                    ),
                ], id="max-projection-container", className="compact-control"),
            ], className="compact-controls-row"),
        ], className="compact-controls-container"),

        # Buttons for viewing in 3D and saving
        html.Div([
            html.Button(
                "View in 3D",
                id="view-3d-button",
                className="action-button primary-button"
            ),
            html.Button(
                "Save 3D Image",
                id="save-3d-button",
                className="action-button secondary-button"
            ),
        ], className="button-container"),
        
        # Hidden div for folder picker dialog results
        html.Div(id="folder-picker-output", className="hidden-element"),
        
        # Container for the 3D visualization
        html.Div(id="3d-visualization-container", className="visualization-result")
    ], className="visualization-3d-options")