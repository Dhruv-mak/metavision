from dash import Input, Output, State, html
from visualization.threed_layout import get_3d_image_layout
from visualization.slides_layout import get_slides_layout
from visualization.norm_layout import get_norm_layout
from visualization.animation_layout import get_animation_layout
from form.form_callback import normalize, align, impute_mat, interpolate_mat
from flask import session
import dash
import logging
import os
import numpy as np

logger = logging.getLogger('metavision')

def register_visualization_callback(app, cache):
    @app.callback(
        Output("visualization-output", "children"),
        Input("visualization-type", "value"),
        Input("column-selector", "value"),
        prevent_initial_call=True,
    )
    def get_viz_tab_content(viz_type, molecule):
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id
        logger.info(f"The triggered id is:{triggered_id}")
        
        if triggered_id == "column-selector":
            filename = cache.get(f"{session["session_id"]}:filename")
            if not filename:
                return html.Div("Error: Filename not available", className="error-message")
            if not os.path.exists(os.path.join("workspaces", filename.replace(".csv", ".npy"))):
                return html.Div("Error: Warp Matrix File not found", className="error-message")
            warp_matrix = np.load(os.path.join("workspaces", filename.replace(".csv", ".npy")))
            df = cache.get(f"{session['session_id']}:df")
            if df is None:
                return html.Div("Error: Data not available", className="error-message")
            molecules_list = cache.get(f"{session['session_id']}:molecules_list")
            if molecules_list is None:
                return html.Div("Error: Molecule list not available", className="error-message")
            df, compound_matrix = normalize(
                molecule, df, molecules_list, filename, cache
            )
            compound_matrix = align(molecule, df, molecules_list, filename, warp_matrix, cache)
            interpolate = cache.get(f"{session["session_id"]}:interpolate")
            impute = cache.get(f"{session["session_id"]}:impute")
            radius = cache.get(f"{session["session_id"]}:radius")
            slices = cache.get(f"{session["session_id"]}:slices")
            if interpolate == [] and impute == []:
                logger.info("No interpolation or imputation selected.")
                cache.set(f"{session['session_id']}:compound_matrix", compound_matrix)
            else:
                if impute != []:
                    logger.info("Imputation selected.")
                    compound_matrix = impute_mat(radius, compound_matrix)
                if interpolate != []:
                    logger.info("Interpolation selected.")
                    compound_matrix = interpolate_mat(slices, compound_matrix)
                cache.set(f"{session['session_id']}:compound_matrix", compound_matrix)
            
        if not viz_type:
            return html.Div(
                "Please select a visualization type.", className="instruction-text"
            )

        if viz_type == "3dimage":
            return get_3d_image_layout()
        elif viz_type == "slides":
            # Return slides visualization layout
            return get_slides_layout(cache)
        elif viz_type == "normplot":
            # Return normplot visualization layout
            return get_norm_layout(cache)
        elif viz_type == "animation":
            # Return animation visualization layout
            return get_animation_layout(cache)
        else:
            return html.Div(
                "Unknown visualization type selected.", className="error-message"
            )