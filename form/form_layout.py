from dash import Dash, html, dcc

def get_layout():
    """
    Function to create the layout of the Dash app.
    """
    return html.Div([
        html.H1("MetaVision Data Processing", className="app-title"),
        
        # File Upload Section
        html.Div([
            html.H3("Step 1: Upload Data", className="section-title"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.Div(className='upload-icon'),
                    html.Div('Drag and Drop or', className='upload-text'),
                    html.Button('Select CSV File', className='upload-button')
                ], className='upload-content'),
                multiple=False,
                className='file-upload'
            ),
            html.Div(id='upload-output', className='upload-output'),
        ], className='form-section'),
        
        html.Hr(className="section-divider"),
        
        # Interpolate Section
        html.Div([
            html.H3("Step 2: Interpolate", className="section-title"),
            dcc.Checklist(
                id='interpolate-checkbox',
                options=[{'label': 'Run Interpolation', 'value': 'interpolate'}],
                value=[]
            ),
            html.Div([
                html.Label("Slices:", className="input-label"),
                dcc.Input(
                    id='slices-input',
                    type='number',
                    min=1,
                    step=1,
                    value=1,
                    className="number-input"
                )
            ], id='interpolate-options', className='option-container'),
        ], className='form-section'),
        
        html.Hr(className="section-divider"),
        
        # Impute Section
        html.Div([
            html.H3("Step 3: Impute", className="section-title"),
            dcc.Checklist(
                id='impute-checkbox',
                options=[{'label': 'Run Imputation', 'value': 'impute'}],
                value=[]
            ),
            html.Div([
                html.Label("Radius:", className="input-label"),
                dcc.Input(
                    id='radius-input',
                    type='number',
                    min=1,
                    step=1,
                    value=1,
                    className="number-input"
                )
            ], id='impute-options', className='option-container'),
        ], className='form-section'),
        
        html.Hr(className="section-divider"),
        
        # Run Button
        html.Div([
            html.Button('Run', id='run-button', n_clicks=0, className="run-button")
        ], className="button-container"),
        
    ], className="app-container")