from dash import Dash, html, dcc
from form.form_layout import get_layout
import logging
import dash
from form.form_callback import register_form_callback

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
        return html.Div([
            html.H3("Results", className="section-title"),
            html.P("Results will be displayed here.", className="results-text")
        ])
    else:
        return html.Div([
            html.H3("Error", className="error-text"),
            html.P("Invalid tab selected.", className="error-message")
        ])
        
# Registering the callback for the tabs
register_form_callback(app)


if __name__ == "__main__":
    app.run(debug=True)