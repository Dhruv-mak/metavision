from dash import Dash, html, dcc
from form.form_layout import get_layout
import logging
import dash
import uuid
import os
import secrets
from flask import session, g
from flask_caching import Cache
from utils import janitor
import threading
from form.form_callback import register_form_callback
from visualization.visualization_layout import get_visualization_layout
from export.export_layout import get_export_layout
from config import setup_logger

# Initialize the root logger once
setup_logger(log_level=logging.INFO, log_dir="logs", name="metavision")
# Get a reference to that logger
logger = logging.getLogger("metavision")

app = Dash()
server = app.server
server.secret_key = secrets.token_hex(16)

app.config.suppress_callback_exceptions = True
app.title = "MetaVision Data Processing"
threading.Thread(target=janitor, daemon=True).start()

CACHE_CONFIG = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 60 * 60,
}

cache = Cache(app.server, config=CACHE_CONFIG)


@server.before_request
def ensure_user_workspace():
    """Ensure that the user workspace exists."""
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    os.mkdir("workspaces") if not os.path.exists("workspaces") else None    
    user_id = session["session_id"]
    work_dir = os.path.join("workspaces", user_id)
    if not os.path.exists(work_dir):
        # Create the directory if it doesn't exist
        logger.info(f"Creating workspace directory: {work_dir}")
        os.makedirs(work_dir, exist_ok=True)
    
    g.work_dir = work_dir

app.layout = html.Div([
    html.H1("MetaVision Data Processing", className="app-title"),
    
    # Tabs
    dcc.Tabs(id="tabs", value="parameters", children=[
        dcc.Tab(label="Parameters", value="parameters", className="tab"),
        dcc.Tab(label="Visualization", value="visualization", className="tab"),
        dcc.Tab(label="Export", value="export", className="tab"),
    ], className="tabs"),
    html.Div(id="tabs-content", className="tab-content"),
    dcc.Store(id="processed", data=False),
    dcc.Store(id="molecule")
    ])

@app.callback(
    dash.dependencies.Output("tabs-content", "children"),
    [dash.dependencies.Input("tabs", "value")]
)
def render_tab(tab):
    if tab == "parameters":
        return get_layout()
    elif tab == "visualization":
        return get_visualization_layout()
    elif tab == "export":
        return get_export_layout()
    else:
        return html.Div([
            html.H3("Error", className="error-text"),
            html.P("Invalid tab selected.", className="error-message")
        ])
            
# Registering the callback for the tabs
register_form_callback(app, cache)

if __name__ == "__main__":
    app.run(debug=True)