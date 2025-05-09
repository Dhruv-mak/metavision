from dash import Output, Input, State
import logging
import os
import pandas as pd
import io
import base64

logger = logging.getLogger(__name__)


def register_form_callback(app):
    """
    Register the callback for the form submission.
    """
        
    @app.callback(
        [],
        [Input("upload-data", "contents"), Input("run-button", "n_clicks")],
        State("upload-data", "filename"),
    )
    def upload_file(contents, _, filename):
        """
        Callback to handle file upload.
        """
        logger.info("File upload callback triggered.")
        if contents is not None:
            logger.info(f"File {filename} uploaded successfully.")
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            logger.info(f"Received file with content type: {content_type}")
            logger.info(f"The type of content_type is: {type(content_type)}")
            if content_type == "data:text/csv;base64":
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                molecules_list = df.columns.tolist()
                logger.info(f"DataFrame loaded with {len(df)} rows and {len(df.columns)} columns.")
                logger.info(f"Columns: {molecules_list}")
            else:
                logger.error("Unsupported file type.")
                return None, None
            return df, filename
        else:
            logger.warning("No file uploaded.")
            return None, None