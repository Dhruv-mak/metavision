from dash.dependencies import Input, Output, State

def register_export_callbacks(app):
    # Update molecules selected count
    @app.callback(
        Output("molecules-selected-count", "children"),
        [Input("molecule-checklist", "value")]
    )
    def update_molecules_count(selected_values):
        return str(len(selected_values)) if selected_values else "0"
    
    # Update numbers selected count
    @app.callback(
        Output("numbers-selected-count", "children"),
        [Input("number-checklist", "value")]
    )
    def update_numbers_count(selected_values):
        return str(len(selected_values)) if selected_values else "0"
    
    # Handle Select All for molecules
    @app.callback(
        [Output("molecule-checklist", "value"),
         Output("select-all-molecules", "value")],
        [Input("select-all-molecules", "value"),
         Input("molecule-checklist", "value")],
        [State("molecule-checklist", "options")]
    )
    def handle_molecule_select_all(select_all, selected_molecules, options):
        # Get all possible values
        all_values = [option["value"] for option in options]
        
        # If select all was just checked
        if select_all and "select-all" in select_all:
            return all_values, ["select-all"]
        # If select all was just unchecked
        elif not select_all:
            return [], []
        # If individual molecules were selected/deselected
        else:
            # If all molecules are selected, ensure select all is checked
            if set(selected_molecules) == set(all_values):
                return all_values, ["select-all"]
            # If some molecules are deselected, ensure select all is unchecked
            else:
                return selected_molecules, []
    
    # Handle Select All for numbers
    @app.callback(
        [Output("number-checklist", "value"),
         Output("select-all-numbers", "value")],
        [Input("select-all-numbers", "value"),
         Input("number-checklist", "value")],
        [State("number-checklist", "options")]
    )
    def handle_number_select_all(select_all, selected_numbers, options):
        # Get all possible values
        all_values = [option["value"] for option in options]
        
        # If select all was just checked
        if select_all and "select-all" in select_all:
            return all_values, ["select-all"]
        # If select all was just unchecked
        elif not select_all:
            return [], []
        # If individual numbers were selected/deselected
        else:
            # If all numbers are selected, ensure select all is checked
            if set(selected_numbers) == set(all_values):
                return all_values, ["select-all"]
            # If some numbers are deselected, ensure select all is unchecked
            else:
                return selected_numbers, []

    # You can add a callback for the export button here
    # @app.callback(...)