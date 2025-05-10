from dash import dcc, html, Input, Output, State
from flask import session
import logging

logger = logging.getLogger("metavision")


def register_export_callback(app, cache):
    @app.callback(
        Output("tissues-selected-count", "children"),
        [Input("tissue-checklist", "value")],
    )
    def update_tissues_count(selected_tissues):
        logger.info(f"Selected tissues: {selected_tissues}")
        count = len(selected_tissues)
        logger.info(f"Number of selected tissues: {count}")
        return str(count)
    
    @app.callback(
        Output("molecules-selected-count", "children"),
        Input("molecule-checklist", "value"),
    )
    def update_molecules_count(selected_molecules):
        logger.info(f"Selected molecules: {selected_molecules}")
        count = len(selected_molecules)
        logger.info(f"Number of selected molecules: {count}")
        return str(count)
    
    @app.callback(
        [],
        [Input("select-all-molecules", "value"), Input("molecule-checklist", "value"), Input("")],
    )
    def export_file(select_all_check, checked_molecules):
        logger.info("Exporting file...")

        molecules_list = cache.get(f"{session['id']}:molecules_list")
        if select_all_check == [] and checked_molecules == []:
            logger.error("No molecules selected for export.")
            raise ValueError("No molecules selected for export.")

        selected_molecules = []
        if "select-all-molecules" in select_all_check:
            selected_molecules = molecules_list
        else:
            selected_molecules = checked_molecules

        selected_tissues = cache.get(f"{session['id']}:tissue_ids")
        if selected_tissues is None:
            logger.error("No tissues selected for export.")
            raise ValueError("No tissues selected for export.")
        logger.info(f"Selected molecules: {selected_molecules}")
        logger.info(f"Selected tissues: {selected_tissues}")
        
        
        
        
