from dash import html, dcc
from flask import session
import logging
logger = logging.getLogger("metavision")

def get_visualization_layout(cache):
    """
    Returns the layout for the Visualization sub-tab with two dropdowns arranged side by side.
    The column dropdown will be populated dynamically via a callback.
    """
    molecule_list = cache.get(f"{session['session_id']}:molecules_list")
    ref_compound = cache.get(f"{session['session_id']}:ref_compound")
    logger.info(f"ref_compound: {ref_compound}")
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
                            {'label': molecule, 'value': molecule} for molecule in molecule_list
                        ],
                        value=ref_compound,
                        placeholder="Select a molecule/tissue",
                        className="dropdown"
                    ),
                ], className="dropdown-container"),
            ], className="dropdowns-row"),
            
            dcc.Loading(
                id="loading-visualization",
                type="circle",
                color="#00BCD4",  # Match your primary color
                children=html.Div(id='visualization-output', className="visualization-container"),
                overlay_style={"visibility": "visible", "filter": "blur(2px)", "background": "rgba(0,0,0,0.3)"}
            )
        ], className="visualization-controls")
    ], className="visualization-layout")