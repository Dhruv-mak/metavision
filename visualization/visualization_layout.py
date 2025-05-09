from dash import html, dcc

def get_visualization_layout():
    """
    Returns the layout for the Visualization sub-tab with two dropdowns arranged side by side.
    The column dropdown will be populated dynamically via a callback.
    """
    return html.Div([
        html.Div([
            # Container for side-by-side dropdowns using flexbox
            html.Div([
                # First dropdown for visualization type
                html.Div([
                    html.Label("Visualization Type:", className="dropdown-label"),
                    dcc.Dropdown(
                        id='visualization-type',
                        options=[
                            {'label': html.Span(['Slides'], style={'color': 'Black', 'font-size': 16}), 'value': 'slides'},
                            {'label': html.Span(['Norm Plot'], style={'color': 'Black', 'font-size': 16}), 'value': 'normplot'},
                            {'label': html.Span(['Animation'], style={'color': 'Black', 'font-size': 16}), 'value': 'animation'},
                            {'label': html.Span(['3D Image'], style={'color': 'Black', 'font-size': 16}), 'value': '3dimage'},
                        ],
                        placeholder="Select a visualization type",
                        className="dropdown"
                    ),
                ], style={'flex': '1', 'marginRight': '10px'}),
                
                # Second dropdown for column selection
                html.Div([
                    html.Label("Molecule/Tissue:", className="dropdown-label"),
                    dcc.Dropdown(
                        id='column-selector',
                        options=[
                            {'label': html.Span(['molecule 1'], style={'color': 'Black', 'font-size': 16}), 'value': 'molecule1'},
                            {'label': html.Span(['molecule 2'], style={'color': 'Black', 'font-size': 16}), 'value': 'molecule2'},
                            {'label': html.Span(['molecule 3'], style={'color': 'Black', 'font-size': 16}), 'value': 'molecule3'},
                            {'label': html.Span(['molecule 4'], style={'color': 'Black', 'font-size': 16}), 'value': 'molecule4'},
                        ],
                        placeholder="Select a molecule/tissue",
                        className="dropdown"
                    ),
                ], style={'flex': '1', 'marginLeft': '10px'}),
            ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-end'}),
            
            html.Div(id='visualization-output', className="visualization-container",
                    style={'marginTop': '20px'})
        ], className="visualization-controls")
    ])