from dash import Input, Output, State, callback, html
from visualization.threed_layout import get_3d_image_layout
from visualization.slides_layout import get_slides_layout

def register_visualization_callback(app, cache):
    @app.callback(
        Output("visualization-output", "children"),
        Input("visualization-type", "value"),
        Input("column-selector", "value")
    )
    def get_viz_tab_content(viz_type, column):
        if not viz_type:
            return html.Div("Please select a visualization type.", className="instruction-text")
        
        if not column:
            return html.Div("Please select a molecule/tissue to visualize.", className="instruction-text")
        
        if viz_type == "3dimage":
            return get_3d_image_layout()
        elif viz_type == "slides":
            # Return slides visualization layout
            return get_slides_layout(cache)
        elif viz_type == "normplot":
            # Return normplot visualization layout
            return html.Div("Norm Plot visualization will appear here")
        elif viz_type == "animation":
            # Return animation visualization layout
            return html.Div("Animation visualization will appear here")
        else:
            return html.Div("Unknown visualization type selected.", className="error-message")