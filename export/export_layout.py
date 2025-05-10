from dash import html, dcc

def get_export_layout():
    """
    Returns the layout for the Export sub-tab.
    """
    return html.Div([
        # Normalization Selection with options inline
        html.Div([
            html.Div([
                html.Label("Select Normalization:", className="export-label"),
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
                ], className="radio-container")
            ], className="normalization-controls")
        ], className="form-section normalization-section"),
        
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
                ], className="column-content checklist-container")
            ], className="selection-column"),
            
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
                ], className="column-content checklist-container")
            ], className="selection-column"),
        ], className="selection-columns-container"),
        
        html.Hr(className="section-divider"),
        
        # Export Options
        html.Div([
            # CSV Format Selection
            html.Div([
                html.Div([
                    html.Label("Export Format:", className="export-label"),
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
                        className="export-format-radio"
                    )
                ], className="format-controls")
            ], className="export-format-section"),
            
            # Directory Selection with Browse and Export buttons
            html.Div([
                html.Div([
                    html.Label("Output Directory:", className="export-label"),
                    dcc.Input(
                        id='output-directory',
                        type='text',
                        placeholder="Select output directory...",
                        className="directory-input"
                    ),
                    html.Button(
                        "Browse...",
                        id="browse-button",
                        className="browse-button"
                    ),
                    html.Button(
                        "Export",
                        id="export-button",
                        className="export-button"
                    ),
                ], className="directory-controls")
            ], className="directory-section"),
            
            # Status message area
            html.Div(id="export-status", className="export-status")
        ], className="form-section export-options")
    ], className="export-layout")