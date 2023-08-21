"""Parser module to parse gear config.json."""

from typing import Tuple
from flywheel_gear_toolkit import GearToolkitContext

def parse_config(
    gear_context: GearToolkitContext,
     
) -> Tuple[dict, dict, dict]: # Add dict for each set of outputs
    """Parse the config and other options from the context, both gear and app options.

    Returns:
        gear_inputs
        gear_options: options for the gear
        app_options: options to pass to the app
    """

    # Gear Inputs
    # Changed to call directly (user input)
    gear_inputs = {
        "axi": gear_context.get_input_path("input")
    }


    # ##   Gear config   ## #
    # some options here not relevent/called
    # Manifest options can be set by Dev (not seen by user). These can be altered in the manifest and avoids needing to change anything else
    # Config options are those to be selected by user (can also have default values)
    gear_options = {
        "kcl-app-binary": gear_context.manifest.get("custom").get("kcl-app-binary"),
        "kcl-app-modalities": gear_context.manifest.get("custom").get("kcl-app-modalities"),
        "analysis-level": gear_context.manifest.get("custom").get("analysis-level"),
        "output-dir": gear_context.output_dir,
        "destination-id": gear_context.destination["id"],
        "work-dir": gear_context.work_dir,
        "client": gear_context.client,
    }

    # set the output dir name:
    gear_options["output_analysis_id_dir"] = (
        gear_options["output-dir"] / gear_options["destination-id"]
    )

    # ##   App options:   ## #
    """ Notes on inputs:  These notes follow the input order as documented here:
    https://github.com/ANTsX/ANTs/blob/master/Scripts/antsMultivariateTemplateConstruction2.sh 

    """

    app_options_keys = [
    "parc",
    "vol",
    "QC" 
]
    # keys here should be pulled from config (file generated after user selections on platform).
    # These may still be manifest defaults but allows user input
    # If pulled directly from manifest will not collect user choices. 
    app_options = {key: gear_context.config.get(key) for key in app_options_keys}

    # gear_inputs, 
    return gear_inputs, gear_options, app_options