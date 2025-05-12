from dash import Output, Input, State
import logging
import os
import pandas as pd
import io
import base64
from flask import session
from metavision.MetaAlign3D import create_compound_matrix, calculate_warp_matrix
from metavision.MetaAlign3D import MetaAlign3D
from metavision.MetaInterp3D import MetaInterp3D
import os
import numpy as np
from metavision.utils import get_ref_compound
from metavision.MetaNorm3D import MetaNorm3D
from flask import session
from metavision.MetaImpute3D import MetaImpute3D

logger = logging.getLogger("metavision")


def normalize(molecule, df, molecule_list, filename, cache):
    logger.info("Normalizing molecule data...")
    meta_norm = MetaNorm3D(df, molecule_list[0])
    logger.info("MetaNorm3D is completed")
    norm_df = meta_norm.totalsum_norm()
    cache.set(f"{session['session_id']}:norm_df", norm_df)
    logger.info(f"totalsum norm df head: {norm_df.head}")
    data = meta_norm.section_norm()
    cache.set(f"{session['session_id']}:df", data)
    logger.info(f"Calling MetaAlign3D in start_normalization process")
    session_id = session["session_id"]
    warp_matrix = cache.get(f"{session_id}:warp_matrix")
    meta_normalize = MetaAlign3D(
        filename, df, molecule, molecule_list[0], warp_matrix, reverse=True
    )
    logger.info("MetaAlign3D is completed in start_normalization process")
    compound_matrix = meta_normalize.create_compound_matrix()
    # cache.set(f"{session_id}:compound_matrix", compound_matrix)
    logger.info(f"Sum of compound_matrix: {compound_matrix.sum()}")
    return data, compound_matrix


def align(molecule, df, molecule_list, filename, warp_matrix, cache):
    logger.info("Aligning molecule data...")
    meta_align = MetaAlign3D(
        filename,
        df,
        molecule,
        molecule_list[0],
        warp_matrix,
        reverse=True,
    )
    logger.info("MetaAlign3D is completed in start_alignment process")
    compound_matrix = meta_align.create_compound_matrix()
    compound_matrix = meta_align.seq_align()
    logger.info(f"Sum of compound_matrix: {compound_matrix.sum()}")
    return compound_matrix

def impute_mat(radius, compound_matrix):
    logger.info("Imputing molecule data...")
    meta_impute = MetaImpute3D(create_compound_matrix, radius)
    logger.info("MetaImpute3D is completed")
    compound_matrix = meta_impute.seq_impute()
    logger.info(f"Sum of compound_matrix: {compound_matrix.sum()}")
    return compound_matrix

def interpolate_mat(slices, compound_matrix):
    logger.info("Interpolating molecule data...")
    meta_interp = MetaInterp3D(compound_matrix, slices)
    logger.info("MetaInterp3D is completed")
    compound_matrix = meta_interp.interp()
    logger.info(f"Sum of compound_matrix: {compound_matrix.sum()}")
    return compound_matrix

def register_form_callback(app, cache):
    """
    Register the callback for the form submission.
    """

    @app.callback(
        [Output("processed", "data"), Output("molecule", "data")],
        [Input("run-button", "n_clicks")],
        [
            State("upload-data", "contents"),
            State("upload-data", "filename"),
            State("interpolate-checkbox", "value"),
            State("slices-input", "value"),
            State("impute-checkbox", "value"),
            State("radius-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def upload_file(_, contents, filename, interpolate, slices, impute, radius):
        """
        Process uploaded CSV file and store data in cache.

        Args:
            contents (str): Base64 encoded file contents
            n_clicks (int): Number of clicks on the run button
            filename (str): Name of the uploaded file

        Returns:
            bool: True if processing was successful, False otherwise
        """
        # Check if a file was uploaded
        if contents is None:
            logger.warning("No file uploaded.")
            return False, ""

        try:
            # Extract and decode file content
            logger.info(f"Processing uploaded file: {filename}")
            cache.set(f"{session['session_id']}:filename", filename)
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            # Verify file type
            if "text/csv" not in content_type:
                logger.error(
                    f"Unsupported file type: {content_type}. Only CSV files are supported."
                )
                return False, ""

            # Parse CSV data
            logger.info("Parsing CSV data...")
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

            # Rename 'region' column to 'tissue_id' if it exists
            if "region" in df.columns:
                df = df.rename(columns={"region": "tissue_id"})

            # Ensure 'tissue_id' column exists
            if "tissue_id" not in df.columns:
                logger.error("CSV file must contain a 'tissue_id' or 'region' column.")
                return False, ""

            # Extract tissue IDs
            tissue_ids = df["tissue_id"].unique().tolist()
            cache.set(f"{session['session_id']}:tissue_ids", tissue_ids)
            logger.info(f"Found {len(tissue_ids)} unique tissue IDs")

            # Process molecule columns
            columns = df.columns[1:].tolist()
            metadata_columns = [
                "spotId",
                "raster",
                "x",
                "y",
                "z",
                "Date",
                "Class",
                "tissue_id",
                "roi",
            ]
            molecules_list = [col for col in columns if col not in metadata_columns]

            # Store data in cache
            cache.set(f"{session['session_id']}:molecules_list", molecules_list)
            cache.set(f"{session['session_id']}:df", df)

            # Log summary information
            logger.info(
                f"DataFrame loaded with {len(df)} rows and {len(df.columns)} columns."
            )
            logger.info(f"Found {len(molecules_list)} molecule columns.")
            logger.debug(f"Molecule columns: {molecules_list}")

            ref_coumpound = get_ref_compound(df, molecules_list[0])
            if os.path.exists(
                os.path.join("workspaces", filename.replace(".csv", ".npy"))
            ):
                logger.info(f"Warp Matrix already created for this file. Skipping...")
                warp_matrix = np.load(
                    os.path.join("workspaces", filename.replace(".csv", ".npy"))
                )
            else:
                logger.info("Most prevalent compound: ", ref_coumpound)
                try:
                    logger.info("Creating reference compound matrix...")
                    ref_compound_matrix = create_compound_matrix(
                        df, ref_coumpound, reverse=True
                    )
                    logger.info("Creating warp matrix...")
                    warp_matrix = calculate_warp_matrix(ref_compound_matrix)
                    cache.set(f"{session['session_id']}:warp_matrix", warp_matrix)
                    np.save(
                        os.path.join("workspaces", filename.replace(".csv", ".npy")),
                        warp_matrix,
                    )
                except Exception as e:
                    logger.error(f"Error creating warp matrix: {str(e)}")
                    return False, ""

            logger.info("Starting to load DataFrame into NumPy arrays...")

            df, compound_matrix = normalize(
                ref_coumpound, df, molecules_list, filename, cache
            )
            compound_matrix = align(
                ref_coumpound, df, molecules_list, filename, warp_matrix, cache
            )
            
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
            cache.set(f"{session['session_id']}:interpolate", interpolate)
            cache.set(f"{session['session_id']}:impute", impute)
            cache.set(f"{session['session_id']}:slices", slices)
            cache.set(f"{session['session_id']}:radius", radius)
            cache.set(f"{session['session_id']}:ref_compound", ref_coumpound)
            return True, ref_coumpound

        except Exception as e:
            logger.error(f"Error processing uploaded file: {str(e)}")
            return False, ""
