from dash import html, dcc

def get_visualization_layout():
    """
    Returns the layout for the Visualization sub-tab with two dropdowns arranged side by side.
    The column dropdown will be populated dynamically via a callback.
    """
    return html.Div([
        html.Div([
            # Container for side-by-side dropdowns
            html.Div([
                # First dropdown for visualization type
                html.Div([
                    html.Label("Visualization Type:", className="dropdown-label"),
                    dcc.Dropdown(
                        id='visualization-type',
                        options=[
                            {'label': 'Slides', 'value': 'slides'},
                            {'label': 'Norm Plot', 'value': 'normplot'},
                            {'label': 'Animation', 'value': 'animation'},
                            {'label': '3D Image', 'value': '3dimage'},
                        ],
                        placeholder="Select a visualization type",
                        className="dropdown"
                    ),
                ], className="dropdown-container"),
                
                # Second dropdown for column selection
                html.Div([
                    html.Label("Molecule/Tissue:", className="dropdown-label"),
                    dcc.Dropdown(
                        id='column-selector',
                        options=[
                            {'label': 'molecule 1', 'value': 'molecule1'},
                            {'label': 'molecule 2', 'value': 'molecule2'},
                            {'label': 'molecule 3', 'value': 'molecule3'},
                            {'label': 'molecule 4', 'value': 'molecule4'},
                        ],
                        placeholder="Select a molecule/tissue",
                        className="dropdown"
                    ),
                ], className="dropdown-container"),
            ], className="dropdowns-row"),
            
            html.Div(id='visualization-output', className="visualization-container")
        ], className="visualization-controls")
    ], className="visualization-layout")