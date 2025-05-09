from dash import html, dcc

def get_export_layout():
    """
    Returns the layout for the Export sub-tab.
    """
    return html.Div([
        # Normalization Selection with options inline
        html.Div([
            html.Div([
                html.Label("Select Normalization:", 
                          className="export-label", 
                          style={'display': 'inline-block', 'marginRight': '20px', 'fontWeight': 'bold', 'verticalAlign': 'middle'}),
                          
                html.Div([
                    dcc.RadioItems(
                        id='normalization-select',
                        options=[
                            {'label': 'None', 'value': 'none'},
                            {'label': 'Total Sum Normalization', 'value': 'total_sum_norm'}
                        ],
                        value='none',
                        inline=True, 
                        inputStyle={"marginRight": "5px"},
                        labelStyle={"marginRight": "30px"},
                        className="normalization-radio"
                    )
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ])
        ], className="normalization-section"),
        
        html.Hr(className="section-divider"),
        
        # Two Columns for Selection
        html.Div([
            # First Column (Molecules)
            html.Div([
                html.Div([
                    html.Span("Total: 4 ", className="count-label"),
                    html.Span("Selected: ", className="count-label"),
                    html.Span("0", id="molecules-selected-count", className="count-value"),
                    html.Span(" ", className="spacer"),
                    dcc.Checklist(
                        id='select-all-molecules',
                        options=[{'label': 'Select All', 'value': 'select-all'}],
                        value=[],
                        className="select-all-checkbox"
                    )
                ], className="column-header"),
                
                # Scrollable list of molecules
                html.Div([
                    dcc.Checklist(
                        id='molecule-checklist',
                        options=[
                            {'label': f'molecule {i}', 'value': f'molecule_{i}'} 
                            for i in range(1, 5)
                        ],
                        value=[],
                        className="item-checklist"
                    )
                ], className="column-content", style={'maxHeight': '200px', 'overflowY': 'auto'})
            ], className="selection-column", style={'width': '48%'}),
            
            # Second Column (Numbers)
            html.Div([
                html.Div([
                    html.Span("Total: 10 ", className="count-label"),
                    html.Span("Selected: ", className="count-label"),
                    html.Span("0", id="numbers-selected-count", className="count-value"),
                    html.Span(" ", className="spacer"),
                    dcc.Checklist(
                        id='select-all-numbers',
                        options=[{'label': 'Select All', 'value': 'select-all'}],
                        value=[],
                        className="select-all-checkbox"
                    )
                ], className="column-header"),
                
                # Scrollable list of numbers
                html.Div([
                    dcc.Checklist(
                        id='number-checklist',
                        options=[
                            {'label': f'{i}', 'value': f'number_{i}'} 
                            for i in range(1, 11)
                        ],
                        value=[],
                        className="item-checklist"
                    )
                ], className="column-content", style={'maxHeight': '200px', 'overflowY': 'auto'})
            ], className="selection-column", style={'width': '48%'}),
        ], className="selection-columns-container", style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Hr(className="section-divider"),
        
        # Export Options
        html.Div([
            # CSV Format Selection
            html.Div([
                html.Div([
                    html.Label("Export Format:", className="export-label", 
                              style={'display': 'inline-block', 'marginRight': '15px', 'fontWeight': 'bold', 'verticalAlign': 'middle'}),
                    
                    dcc.RadioItems(
                        id='export-format',
                        options=[
                            {'label': 'Single CSV', 'value': 'single'},
                            {'label': 'Multiple CSVs', 'value': 'multiple'}
                        ],
                        value='single',
                        inline=True,
                        inputStyle={"marginRight": "5px"},  
                        labelStyle={"marginRight": "30px"}, 
                        className="export-format-radio",
                        style={'display': 'inline-block', 'verticalAlign': 'middle'}
                    )
                ])
            ], className="export-format-section", style={'marginBottom': '20px'}), 
            
            # Directory Selection with Browse and Export on the same line
            html.Div([
                html.Div([
                    html.Label("Output Directory:", 
                              className="export-label", 
                              style={
                                  'display': 'inline-block', 
                                  'width': '150px',
                                  'fontWeight': 'bold', 
                                  'verticalAlign': 'middle'
                              }),
                    
                    dcc.Input(
                        id='output-directory',
                        type='text',
                        placeholder="Select output directory...",
                        className="directory-input",
                        style={
                            'display': 'inline-block',
                            'width': 'calc(100% - 420px)',  
                            'verticalAlign': 'middle'
                        }
                    ),
                    
                    # Browse button
                    html.Button(
                        "Browse...",
                        id="browse-button",
                        className="browse-button",
                        style={
                            'display': 'inline-block',
                            'marginLeft': '10px',
                            'width': '100px',
                            'verticalAlign': 'middle'
                        }
                    ),
                    
                    # Export button
                    html.Button(
                        "Export",
                        id="export-button",
                        className="export-button",
                        style={
                            'display': 'inline-block',
                            'marginLeft': '10px',
                            'width': '100px',
                            'verticalAlign': 'middle'
                        }
                    ),
                ], style={'display': 'flex', 'alignItems': 'center', 'width': '100%'})
            ], className="directory-section"),
            
            # Status message area
            html.Div(id="export-status", className="export-status", style={'marginTop': '15px'})
        ], className="export-options")
    ], className="export-layout")
