from dash import Output, Input, State, callback, dcc, html
import dash
from flask import session
from plotly import graph_objects as go

def register_slides_callback(app, cache):
    @callback(
        [Output("selected-slide-display", "children"), Output("selected-slice", "data")],
        [
            Input("thumbnail-container-0", "n_clicks"),
            Input("thumbnail-container-1", "n_clicks"),
            Input("thumbnail-container-2", "n_clicks"),
            # Add more inputs as needed for all your thumbnails
            Input("colormap-selection", "value"),
        ],
        [State("selected-slice", "data"), State("matrix-info", "data")],
        prevent_initial_call=True,
    )
    def update_selected_slide(
        click0, click1, click2, colormap, selected_slice, matrix_info
    ):
        # Find which thumbnail was clicked by checking the callback context
        ctx = dash.callback_context
        if not ctx.triggered:
            return (
                html.Div(
                    "Click on a thumbnail to view details", className="select-instruction"
                ),
                selected_slice,
            )

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if "thumbnail-container" in trigger_id:
            # Extract the slice index from the clicked thumbnail ID
            selected_slice = int(trigger_id.split("-")[-1])

            # Get compound matrix from cache
            compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
            if compound_matrix is None:
                return (
                    html.Div("Error: No data available", className="error-message"),
                    selected_slice,
                )

            vmax = matrix_info["vmax"]

            # Create a detailed view of the selected slice with the chosen colormap
            fig = go.Figure()
            fig.add_trace(
                go.Heatmap(
                    z=compound_matrix[selected_slice],
                    colorscale=colormap,
                    showscale=True,
                    zmin=0,
                    zmax=vmax,
                    colorbar=dict(
                        title="Intensity",
                        titleside="right",
                        titlefont=dict(color="white"),
                        tickfont=dict(color="white"),
                        ticks="outside",
                    ),
                )
            )

            fig.update_layout(
                title=dict(
                    text=f"Slice {selected_slice + 1}",
                    font=dict(color="white", size=16),
                    x=0.5,
                ),
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                font=dict(color="white"),
                height=500,
            )

            return (
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": True},
                    className="selected-slide-graph",
                ),
                selected_slice,
            )

        # If it was just a colormap change, update the current view
        compound_matrix = cache.get(f"{session['session_id']}:compound_matrix")
        if compound_matrix is None or selected_slice is None:
            return (
                html.Div("Error: No data available", className="error-message"),
                selected_slice,
            )

        vmax = matrix_info["vmax"]

        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=compound_matrix[selected_slice],
                colorscale=colormap,
                showscale=True,
                zmin=0,
                zmax=vmax,
                colorbar=dict(
                    title="Intensity",
                    titleside="right",
                    titlefont=dict(color="white"),
                    tickfont=dict(color="white"),
                    ticks="outside",
                ),
            )
        )

        fig.update_layout(
            title=dict(
                text=f"Slice {selected_slice + 1}", font=dict(color="white", size=16), x=0.5
            ),
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            font=dict(color="white"),
            height=500,
        )

        return (
            dcc.Graph(
                figure=fig,
                config={"displayModeBar": True},
                className="selected-slide-graph",
            ),
            selected_slice,
        )
