from dash import html, dcc
from flask import session
import logging
logger = logging.getLogger("metavision")

def get_export_layout(cache):
    """
    Returns the layout for the Export sub-tab.
    """
    logger.debug("Creating Export Layout")
    molecule_list = cache.get(f"{session['session_id']}:molecules_list")
    if not molecule_list:
        logger.error("No molecules found in cache.")
        raise ValueError("No molecules found in cache.")
    logger.debug(f"molecule_list: {molecule_list}")
    tissue_list = cache.get(f"{session['session_id']}:tissue_ids")
    if not tissue_list:
        logger.error("No tissues found in cache.")
        raise ValueError("No tissues found in cache.")
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
                    html.Span(f"Total: {len(molecule_list)}", className="count-label"),
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
                            {'label': i, 'value': i} 
                            for i in molecule_list
                        ],
                        value=[],
                        className="item-checklist"
                    )
                ], className="column-content checklist-container")
            ], className="selection-column"),
            
            # Second Column Tissues
            html.Div([
                html.Div([
                    html.Span(f"Total: {len(tissue_list)}", className="count-label"),
                    html.Span("Selected: ", className="count-label"),
                    html.Span("0", id="tissues-selected-count", className="count-value"),
                    html.Span(" ", className="spacer"),
                    dcc.Checklist(
                        id='select-all-tissues',
                        options=[{'label': 'Select All', 'value': 'select-all'}],
                        value=[],
                        className="select-all-checkbox"
                    )
                ], className="column-header"),
                
                # Scrollable list of tissues
                html.Div([
                    dcc.Checklist(
                        id='tissues-checklist',
                        options=[
                            {'label': i, 'value': i} 
                            for i in tissue_list
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