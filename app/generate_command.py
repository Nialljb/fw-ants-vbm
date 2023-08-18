from typing import List, Tuple, Union
from app.command_line import  build_command_list

def generate_command(gear_inputs: dict, gear_options: dict, app_options: dict,) -> List[str]:
    """Build the main command line command to run.

    This method should be the same for FW and XNAT instances. It is also BIDS-App
    generic.

    Args:
        gear_options (dict): options for the gear, from config.json
        app_options (dict): options for the app, from config.json
    Returns:
        cmd (list of str): command to execute
    """
    # Common to all BIDS Apps (https://github.com/BIDS-Apps), start with the command
    # itself and the 3 positional args: bids path, output dir, analysis-level
    # ("participant"/"group").
    # This should be done here in case there are nargs='*' arguments
    # (PV: Not sure if this is the case anymore. Their template seems to
    # suggest so, but not the general documentation.)
    
    # TO DO: add in all the other options
    print("gear input: ", gear_inputs["axi"])

    cmd = [
        # will need to ammend this to pull relevent files
        str(gear_options["kcl-app-binary"]),
        gear_inputs["axi"], 
        gear_inputs["cor"],
        gear_inputs["sag"]
    ]
    #print("cmd is: ", cmd)

    # get app parameters and pass them to the command
    command_parameters = {}

    for key, val in app_options.items():
        print("key val pair: ", key, val)
        # these arguments are passed directly to the command as is
        if key == "kcl_app_args" and val:
            kcl_app_args = val.split(" ")
            # append this list to the cmd:
            cmd.extend(kcl_app_args)

        else:
            command_parameters[key] = val

    # # check to see if we need to skip the bids-validation:
    # if not gear_options["run-bids-validation"]:
    #     command_parameters["skip-bids-validation"] = True

    cmd = build_command_list(cmd, command_parameters)
    print("cmd is: ", cmd)
    print("cmd param are: ", command_parameters)
    
    for ii, cc in enumerate(cmd):
        print("loop", ii, cc)
        if cc.startswith("--verbose"):
            # The app takes a "-v/--verbose" boolean flag (either present or not),
            # while the config verbose argument would be "--verbose=v".
            # So replace "--verbose=<v|vv|vvv>' with '-<v|vv|vvv>':
            cmd[ii] = "-" + cc.split("=")[1]

        elif " " in cc:
            # When there are spaces in an element of the list, it means that the
            # argument is a space-separated list, so take out the "=" separating the
            # argument from the value. e.g.:
            #     "--foo=bar fam" -> "--foo bar fam"
            # this allows argparse "nargs" to work properly
            cmd[ii] = cc.replace("=", " ")

    return cmd