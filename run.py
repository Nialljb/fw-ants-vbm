#!/usr/bin/env python
"""The run script."""
import logging, subprocess

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
# from app.test.test_fsl import test_fsl
from app.command_line import exec_command
from app.metadata import get_metadata
from app.ants_vbm import vbm

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

# Check if FSL output type is set to NIFTI_GZ
# test_fsl()
subprocess.run(["echo $FSLOUTPUTTYPE"],
                            shell=True,
                            check=True)

def main(context: GearToolkitContext) -> None:
    # """Parses metadata in the SDK to determine which template to use for the subject VBM analysis"""
    print("pulling metadata...")
    subject_label, session_label = get_metadata()

    print("running ants vbm script...")
    # vbm(subject_label, session_label)
    
    command = vbm(subject_label, session_label) #"/flywheel/v0/app/main.py"
    # # os.system(command)

    #This is what it is all about
    exec_command(
    command,
    #dry_run=gear_options["dry-run"],
    shell=False,
    cont_output=True,
        )

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)