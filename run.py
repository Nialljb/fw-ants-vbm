#!/usr/bin/env python
"""The run script."""
import logging, subprocess, sys

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
from app.gatherDemographics import get_demo
from app.ants_vbm import vbm
from app.parser import parse_config

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

# Check if FSL output type is set to NIFTI_GZ
subprocess.run(["echo $FSLOUTPUTTYPE"],
                            shell=True,
                            check=True)

def main(context: GearToolkitContext) -> None:
    # """Parses metadata in the SDK to determine which template to use for the subject VBM analysis"""
    print("pulling metadata...")
    subject_label, session_label, target_template = get_demo()

    print("running ants vbm script...")
    # vbm(subject_label, session_label)
    
    print("parsing config...")    
    input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81 = parse_config(context)

    print("running volume estimation...")
    e_code = vbm(subject_label, session_label, target_template, input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81)
    sys.exit(e_code)

    # command = vbm(subject_label, session_label) #"/flywheel/v0/app/main.py"
    # command

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)