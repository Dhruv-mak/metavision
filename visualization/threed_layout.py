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
                labelStyle={ 'margin': '5px'},
                inputStyle={'marginRight': '5px'},
                className="radio-group"
            )
        ], className="control-group"),
        
        # Compact layout with labels and dropdowns side by side
        html.Div([
            # Three controls in a row with minimal spacing
            html.Div([
                # Thickness control
                html.Div([
                    html.Label("Thickness:", 
                            style={'marginRight': '8px', 'display': 'inline-block', 'whiteSpace': 'nowrap'}),
                    dcc.Dropdown(
                        id='thickness-value',
                        options=[{'label': str(i), 'value': i} for i in range(1, 11)],
                        value=1,
                        clearable=False,
                        style={'width': '60px', 'display': 'inline-block'}
                    ),
                ], style={'display': 'inline-flex', 'alignItems': 'center', 'marginRight': '20px'}),
                
                # Gap control
                html.Div([
                    html.Label("Gap:", 
                            style={'marginRight': '8px', 'display': 'inline-block', 'whiteSpace': 'nowrap'}),
                    dcc.Dropdown(
                        id='gap-value',
                        options=[{'label': str(i), 'value': i} for i in range(10)],
                        value=0,
                        clearable=False,
                        style={'width': '60px', 'display': 'inline-block'}
                    ),
                ], style={'display': 'inline-flex', 'alignItems': 'center', 'marginRight': '20px'}),
                
                # Maximum projection control
                html.Div([
                    html.Label("Maximum Projection:", 
                            style={'marginRight': '8px', 'display': 'inline-block', 'whiteSpace': 'nowrap'}),
                    dcc.Dropdown(
                        id='max-projection-value',
                        options=[{'label': str(i), 'value': i} for i in range(100, 0, -1)],
                        value=99,
                        clearable=False,
                        style={'width': '60px', 'display': 'inline-block'}
                    ),
                ], id="max-projection-container", style={'display': 'inline-flex', 'alignItems': 'center'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'}),
        ], style={'marginTop': '15px'}),

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
                className="action-button secondary-button",
                style={"marginLeft": "10px"}
            ),
        ], className="button-container", style={'marginTop': '20px'}),
        
        # Hidden div for folder picker dialog results
        html.Div(id="folder-picker-output", style={"display": "none"}),
        
        # Container for the 3D visualization
        html.Div(id="3d-visualization-container", className="visualization-result", 
                 style={'marginTop': '20px'})
    ], className="visualization-3d-options")