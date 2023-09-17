#!/usr/bin/env python
"""The run script."""
import logging, subprocess, sys

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
from app.gatherDemographics import get_demo
from app.ants_vbm import vbm
# from app.test.TEST_ants_vbm import vbm
from app.parser import parse_config

# Set up logging
log = logging.getLogger(__name__)

# Check if FSL output type is set to NIFTI_GZ
subprocess.run(["echo $FSLOUTPUTTYPE"],
                            shell=True,
                            check=True)

def main(context: GearToolkitContext) -> None:
    # """Parses metadata in the SDK to determine which template to use for the subject VBM analysis"""
    print("pulling metadata...")
    subject_label, session_label, target_template, age, patientSex = get_demo()

    print("parsing config...")    
    input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81 = parse_config(context)

    print("running volume estimation...")
    e_code = vbm(subject_label, session_label, target_template, age, patientSex, input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81)
    sys.exit(e_code)

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)