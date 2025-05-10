from dash import dcc, html, Input, Output, State
from flask import session
import logging
import pandas as pd
import io
import zipfile

logger = logging.getLogger("metavision")


def register_export_callback(app, cache):
    @app.callback(
        Output("tissues-selected-count", "children"),
        Input("tissues-checklist", "value"),
        Input("select-all-tissues", "value"),
    )
    def update_tissues_count(selected_tissues, select_all_check):
        if select_all_check != []:
            tissues_list = cache.get(f"{session['session_id']}:tissue_ids")
            return str(len(tissues_list))
        logger.debug(f"Selected tissues: {selected_tissues}")
        count = len(selected_tissues)
        logger.debug(f"Number of selected tissues: {count}")
        return str(count)

    @app.callback(
        Output("molecules-selected-count", "children"),
        Input("molecule-checklist", "value"),
        Input("select-all-molecules", "value"),
    )
    def update_molecules_count(selected_molecules, select_all_check):
        if select_all_check != []:
            molecules_list = cache.get(f"{session['session_id']}:molecules_list")
            return str(len(molecules_list))
        logger.debug(f"Selected molecules: {selected_molecules}")
        count = len(selected_molecules)
        logger.debug(f"Number of selected molecules: {count}")
        return str(count)

    @app.callback(
        [Output("download-data", "data")],
        [
            Input("select-all-molecules", "value"),
            Input("molecule-checklist", "value"),
            Input("normalization-select", "value"),
            Input("export-format", "value")
        ],
    )
    def export_file(select_all_check, checked_molecules, normalization, export):
        logger.info("Exporting file...")

        molecules_list = cache.get(f"{session['session_id']}:molecules_list")
        if select_all_check == [] and checked_molecules == []:
            logger.error("No molecules selected for export.")
            raise ValueError("No molecules selected for export.")

        selected_molecules = []
        if "select-all-molecules" in select_all_check:
            selected_molecules = molecules_list
        else:
            selected_molecules = checked_molecules

        selected_tissues = cache.get(f"{session['session_id']}:tissue_ids")
        if selected_tissues is None:
            logger.error("No tissues selected for export.")
            raise ValueError("No tissues selected for export.")
        logger.info(f"Selected molecules: {selected_molecules}")
        logger.info(f"Selected tissues: {selected_tissues}")

        if normalization == "none":
            df = cache.get(f"{session["session_id"]}:df")
            filtered_df = df[df['tissue_id'].isin(selected_tissues)]
        else:
            df = cache.get(f"{session["session_id"]}:norm_df")
            filtered_df = df[df['tissue_id'].isin(selected_tissues)]
        
        if export == "multiple":
            df_list = []
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for tissue in selected_tissues:
                    tissue_df = filtered_df[filtered_df['tissue_id'] == tissue]
                    
                    # Filter the dataframe for each tissue
                    tissue_df = filtered_df[filtered_df['tissue_id'] == tissue] 

                    # Select only the columns for selected molecules and the tissue_ids
                    export_df = tissue_df[['tissue_id'] + selected_molecules]
                    df_list.append(export_df)
                # Create a byte buffer to store the zip file
                    # Add each dataframe as a separate CSV file in the zip
                    for i, export_df in enumerate(df_list):
                        tissue_id = export_df['tissue_id'].iloc[0]
                        csv_buffer = io.StringIO()
                        export_df.to_csv(csv_buffer, index=False)
                        zip_file.writestr(f"tissue_{tissue_id}.csv", csv_buffer.getvalue())

            # Reset buffer position to the beginning
            buffer.seek(0)

            # Return the zip file for download
            return [dcc.send_bytes(buffer.getvalue(), f"tissues_export.zip")]
        else:
            export_df = filtered_df[['tissue_id'] + selected_molecules]
            buffer = io.StringIO()
            export_df.to_csv(buffer, index=False)
            buffer.seek(0)
            return [dcc.send_data_frame(buffer.getvalue(), "export.csv")]
                
                
