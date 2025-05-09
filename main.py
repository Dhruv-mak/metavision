from dash import Dash, html, dcc
from form.form_layout import get_layout
import logging
import dash
from form.form_callback import register_form_callback
from results_layout import get_results_layout, get_visualization_layout, get_export_layout

logger = logging.getLogger(__name__)
app = Dash()
server = app.server
app.config.suppress_callback_exceptions = True
app.title = "MetaVision Data Processing"

app.layout = html.Div([
    html.H1("MetaVision Data Processing", className="app-title"),
    
    # Tabs
    dcc.Tabs(id="tabs", value="parameters", children=[
        dcc.Tab(label="Parameters", value="parameters", className="tab"),
        dcc.Tab(label="Results", value="results", className="tab"),
    ], className="tabs"),
    html.Div(id="tabs-content", className="tab-content"),
    ])

@app.callback(
    dash.dependencies.Output("tabs-content", "children"),
    [dash.dependencies.Input("tabs", "value")]
)
def render_tab(tab):
    if tab == "parameters":
        return get_layout()
    elif tab == "results":
        return get_results_layout()
    else:
        return html.Div([
            html.H3("Error", className="error-text"),
            html.P("Invalid tab selected.", className="error-message")
        ])

# Add a callback for the results sub-tabs
@app.callback(
    dash.dependencies.Output("results-subtab-content", "children"),
    [dash.dependencies.Input("results-subtabs", "value")]
)
def render_results_subtab(subtab):
    if subtab == "visualization":
        return get_visualization_layout()
    elif subtab == "export":
        return get_export_layout()
    else:
        return html.Div([
            html.P("Invalid sub-tab selected.", className="error-message")
        ])
            
# Registering the callback for the tabs
register_form_callback(app)


if __name__ == "__main__":
    app.run(debug=True)