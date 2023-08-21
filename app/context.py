"""Hosts the GearToolkitContext class. Provides gear helper functions."""
import argparse
import json
import logging
import os
import pathlib
import sys
import tempfile
import typing as t
import warnings
from pprint import pformat
from shutil import rmtree

try:
    import flywheel

    HAVE_FLYWHEEL = True
except (ModuleNotFoundError, ImportError) as e:
    HAVE_FLYWHEEL = False


from flywheel_gear_toolkit.logging import configure_logging
from utils.metadata import Metadata
from app.constants import BOTTOM_UP_PARENT_HIERARCHY, FILE_OBJECT_DICT

log = logging.getLogger(__name__)


def convert_config_type(input_str):
    """Converts strings in the format ``<value>:<type>`` (i.e. '4:integer') to a type
    consistent with the strin   g preceded by the last `:`

    Args:
        input_str (str): A string in ``<value>:<type>`` format.

    Raises:
        ValueError: If input_str is not a string or the type is not recognized.

    Returns:
        object: A value consistent with the type specified.
    """
    if not isinstance(input_str, str):
        raise ValueError(f"input_str {input_str} is not str")

    if ":" not in input_str:
        input_str = input_str + ":"

    input_str, type_str = input_str.rsplit(":", maxsplit=1)

    type_str = type_str.lower()

    if type_str in ["boolean", "bool"] and input_str.lower() == "true":
        output = True

    elif type_str in ["boolean", "bool"] and input_str.lower() == "false":
        output = False

    elif type_str in ["boolean", "bool"] and input_str.lower() not in [
        "false",
        "true",
    ]:
        raise ValueError(f"Cannot convert {input_str} to a boolean")

    elif type_str in ["str", "", "string"]:
        output = input_str

    elif type_str == "number":
        if "." in input_str:
            output = float(input_str)
        else:
            output = int(input_str)

    elif type_str == "float":

        output = float(input_str)

    elif type_str in ["integer", "int"]:
        output = int(input_str)

    else:
        raise ValueError(f"Unrecognized type_str: {type_str}")

    return output


def parse_context_args(input_args=None):
    """Parses sys.argv (or input args if provided).

    Argument names that are not prefixed with ``--`` or ``-`` will be ignored.
    Destination can be specified with -d <destination_id>:<destination_type> at the
    command line or as `input_args` as ``['-d',
    '<destination_id>:<destination_type>']``

    Args:
        input_args(list, optional): An optional list of arguments to provide to
            argparse. If not provided, sys.argv will be used instead.
            (Default value = None).

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    if not isinstance(input_args, list):
        input_args = sys.argv
    else:
        # coerce to strings if they were passed as an argument
        input_args = [str(item) for item in input_args]

    # fromfile_prefix_chars allows parsing of file containing newline-delimited
    # arguments with @<path to file>
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument(
        "--destination",
        "-d",
        help="<fw container id>:<fw container type>",
        default="aex:acquisition",
    )
    parser.add_argument("--api-key", "-key", help="Flywheel API key", default="")
    _, unknown = parser.parse_known_args(input_args)
    # allows arbitrary arguments to be passed, such as config and file inputs
    for arg in unknown:
        if arg.startswith(("-", "--")):
            # you can pass any arguments to add_argument
            # Supported syntax: -key value, -key=value, --key value or --key=value
            if "=" in arg:
                parser.add_argument(arg.split("=")[0])
            else:
                parser.add_argument(arg)
    args, unknown = parser.parse_known_args(input_args)
    return args


class GearToolkitContext:
    """Provides helper functions for gear development, namely for accessing the gear's
    `config.json` and `manifest.json`

    Args:
        gear_path (str, optional): A path to use, default behavior will use the current
            working directory (``os.getcwd()``).
        manifest_path (str, optional): A path to the gear's manifest.json file,
            defaults to ``self.path/'manifest.json'``.
        config_path (str, optional): A path to the gear's config.json file, defaults to
            ``self._path/'config.json'``.
        input_args (list, optional): List of arguments to parse to generate a
            ``config.json`` file. If not provided, ``sys.argv`` will be parsed instead.
        tempdir (bool, optional): whether to use ``tempfile.TemporaryDirectory()`` for
            ``_path``, defaults to False. Useful for testing.
        log_metadata (bool, optional): whether to log .metadata.json to log upon write,
            defaults to True.

    Attributes:
        _path (pathlib.Path): The result of ``pathlib.Path(gear_path or
            os.getcwd()).resolve()``.
        _client (flywheel.Client): An instance of the Flywheel client if a valid API
            key was provided or a user is currently logged into the Flywheel CLI.
        metadata (dict): Dictionary that stores updates to be dumped to
            `.metadata.json`.
        _temp_dir (tempfile.TemporaryDirectory): None unless initialized with
            `tempdir=True`.
        manifest (dict): Dictionary representation of `manifest.json`.
        config_json (dict): Dictionary representation of `config.json`.
    """

    def __init__(
        self,
        gear_path=None,
        manifest_path=None,
        config_path=None,
        input_args=None,
        tempdir=False,
        log_metadata=True,
        fail_on_validation=True,
    ):
        self._temp_dir = None
        if tempdir:
            self._temp_dir = tempfile.TemporaryDirectory()
            gear_path = self._temp_dir.name

        self._path = pathlib.Path(gear_path or os.getcwd()).resolve()
        self._client = None
        self._out_dir = None
        self._work_dir = None
        self._log_metadata = log_metadata
        self.fail_on_validation = fail_on_validation
        self.manifest = self._load_json(manifest_path or self._path / "manifest.json")
        self.config_json = self._load_json(config_path or self._path / "config.json")
        self.config_from_args(input_args=input_args)
        # Needs to be last
        self.metadata = Metadata(self)

    # def init_logging(self, default_config_name=None, update_config=None):
    #     """Configures logging via `gear_toolkit.logging.templated.configure_logging`.

    #     If no ``default_config_name`` is provided, will get `debug` from the
    #     configuration options. If `debug` is False or not defined in the gear
    #     configuration options, ``default_config_name`` will be set to info.

    #     If `update_config` is not provided, manifest['custom']['log_config'] will be
    #     used (if defined in the manifest).

    #     Args:
    #         default_config_name (str, optional): A string, 'info' or 'debug', indicating
    #             the default template to use. (Defaults to 'info').
    #         update_config (dict, optional): A dictionary containing the keys, subkeys,
    #             and values of the templates to update. (Defaults to None).
    #     """
    #     if not default_config_name:
    #         if self.config.get("debug"):
    #             default_config_name = "debug"
    #         else:
    #             default_config_name = "info"
    #     if not update_config:
    #         if self.manifest:
    #             if isinstance(self.manifest.get("custom"), dict):
    #                 update_config = self.manifest["custom"].get("log_config", None)

    #     configure_logging(
    #         default_config_name=default_config_name,
    #         update_config=update_config,
    #     )
    #     return default_config_name, update_config

    # @property
    # def config(self):
    #     """Get the config dictionary from config.json.

    #     Returns:
    #         dict: The configuration dictionary.
    #     """
    #     return self.config_json["config"]

    # @property
    # def destination(self):
    #     """Get the destination reference.

    #     Returns:
    #         dict: The destination dictionary.
    #     """
    #     return self.config_json["destination"]

    # @property
    # def work_dir(self):
    #     """Get the absolute path to a work directory.

    #     Returns:
    #         pathlib.Path: The absolute path to work.
    #     """
    #     if self._work_dir is None:
    #         self._work_dir = self._path / "work"
    #         if not self._work_dir.exists():
    #             self._work_dir.mkdir(parents=True)
    #     return self._work_dir

    # @property
    # def output_dir(self):
    #     """Get the absolute path to the output directory.

    #     Returns:
    #         pathlib.Path: The absolute path to outputs.
    #     """
    #     if self._out_dir is None:
    #         self._out_dir = self._path / "output"
    #         if not self._out_dir.exists():
    #             self._out_dir.mkdir(parents=True)
    #     return self._out_dir

    # @property
    # def client(self):
    #     """Wrapper around self.get_client()"""
    #     if not self._client:
    #         self._client = self.get_client()
    #     return self._client

    # def get_client(self):
    #     """Get the SDK client, if an api key input exists or CLI client exists.

    #     Returns:
    #       flywheel.Client: The Flywheel SDK client.
    #     """
    #     if not HAVE_FLYWHEEL:
    #         warnings.warn(
    #             "Please install the `sdk` extra or install `flywheel-sdk` within"
    #             " your gear in order to use the SDK client."
    #         )
    #         return None
    #     api_key = None
    #     client = None
    #     for inp in self.config_json["inputs"].values():
    #         if inp["base"] == "api-key" and inp["key"]:
    #             api_key = inp["key"]
    #             try:
    #                 client = flywheel.Client(api_key)
    #             except Exception as exc:  # pylint: disable=broad-except
    #                 log.error(
    #                     "An exception was raised when initializing client: %s",
    #                     exc,
    #                     exc_info=True,
    #                 )
    #     if api_key is None:
    #         try:
    #             client = flywheel.Client()
    #         except Exception as exc:  # pylint: disable=broad-except
    #             log.error(
    #                 "No api_key was provided and exception was raised when "
    #                 "attempting to log in via CLI %s",
    #                 exc,
    #                 exc_info=True,
    #             )
    #     return client

    # def log_config(self):
    #     """Print the configuration and input files to the logger"""
    #     # Log destination
    #     log.info(
    #         "Destination is %s=%s",
    #         self.destination.get("type"),
    #         self.destination.get("id"),
    #     )

    #     # Log file inputs
    #     for inp_name, inp in self.config_json["inputs"].items():
    #         if inp["base"] != "file":
    #             continue

    #         container_type = inp.get("hierarchy", {}).get("type")
    #         container_id = inp.get("hierarchy", {}).get("id")
    #         file_name = inp.get("location", {}).get("name")

    #         log.info(
    #             'Input file "%s" is %s from %s=%s',
    #             inp_name,
    #             file_name,
    #             container_type,
    #             container_id,
    #         )

    #     # Log configuration values
    #     for key, value in self.config.items():
    #         log.info('Config "%s=%s"', key, value)

    def get_input(self, name):
        """The manifest.json has a field for 'inputs'. These are often the files to be analyzed
        or that aid in analyis (e.g., masks). This method gets the file named as the input ("name").

        Args:
            name (str): The name of the input.

        Returns:
            dict: The input dictionary, or None if not found.

        Example:
            gtk_context = GearTookitContext()
            gtk_context.get_input('input_image')
        """
        return self.config_json["inputs"].get(name)

    # def get_input_file_object(self, name):
    #     """Get the specified input file object from config.json
    #     Args:
    #         name (str): The name of the input.

    #     Returns:
    #         dict: The input dictionary, or None if not found.
    #     """
    #     inp = self.get_input(name)
    #     if inp is None:
    #         return None
    #     if inp["base"] != "file":
    #         raise ValueError(f"The specified input {name} is not a file")
    #     return inp["object"]

    # def get_input_file_object_value(self, name, key):
    #     """Get the value of the input file metadata from config.json.
    #     Args:
    #         name (str): The name of the input.
    #         key (str): The name of the file container metadata

    #     Raises:
    #         ValueError: if the input exists, but is not a file.

    #     Returns:
    #         Union[str, list, dict]: The value of the specified file metadata, or None if not found.
    #     """

    #     inp_obj = self.get_input_file_object(name)

    #     return inp_obj.get(key, None) if key in inp_obj.keys() else None

    def get_input_path(self, name):
        """Get the full path to the given input file.
        Sourced from the 'inputs' field in the manifest.json

        Args:
            name (str): The name of the input.

        Raises:
            ValueError: if the input exists, but is not a file.

        Returns:
            str: The path to the input file if it exists, otherwise None.
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp["base"] != "file":
            raise ValueError(f"The specified input {name} is not a file")
        return inp["location"]["path"]

    def get_input_filename(self, name):
        """Get the the filename of given input file.
        Sourced from the 'inputs' field in the manifest.json

        Args:
            name (str): The name of the input.

        Raises:
            ValueError: if the input exists, but is not a file.

        Returns:
            str: The filename to the input file if it exists, otherwise None.
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp["base"] != "file":
            raise ValueError(f"The specified input {name} is not a file")
        return inp["location"]["name"]

    # def get_container_from_ref(self, ref):
    #     """Returns the container from its reference

    #     Args:
    #         ref (dict): A dictionary with type and id keys defined.

    #     Returns:
    #         Container: A flywheel container.
    #     """
    #     container_type = ref.get("type")
    #     getter = getattr(self.client, f"get_{container_type}")
    #     return getter(ref.get("id"))

    # def get_destination_container(self):
    #     """Returns the destination container."""
    #     return self.get_container_from_ref(self.destination)

    # def get_parent(self, container):
    #     """Returns parent container of container input."""
    #     if container.container_type == "analysis":
    #         return self.get_container_from_ref(container.parent)
    #     elif container.container_type == "file":
    #         return container.parent
    #     elif container.container_type == "group":
    #         raise TypeError("Group container does not have a parent.")
    #     else:
    #         for cont_type in BOTTOM_UP_PARENT_HIERARCHY:
    #             if not container.parents.get(cont_type):
    #                 # not defined, parent must be up the hierarchy
    #                 continue
    #             return self.get_container_from_ref(
    #                 {"type": cont_type, "id": container.parents.get(cont_type)}
    #             )

    # def get_destination_parent(self):
    #     """Returns the parent container of the destination container."""
    #     dest = self.get_destination_container()
    #     return self.get_parent(dest)

    # def open_input(self, name, mode="r", **kwargs):
    #     """Open the named input file, derived from the 'inputs' field in the manifest.

    #     Args:
    #         name (str): The name of the input.
    #         mode (str): The open mode (Default value = 'r').
    #         **kwargs (dict): Keyword arguments for `open`.

    #     Raises:
    #         ValueError: If input ``name`` is not defined in config_json.
    #         FileNotFoundError: If the path in the config_json for input ``name`` is
    #             not a file/
    #     Returns:
    #         File: The file object.
    #     """
    #     path = self.get_input_path(name)
    #     if path is None:
    #         raise ValueError(f"Input {name} is not defined in the config.json")
    #     if not os.path.isfile(path):
    #         raise FileNotFoundError(f"Input {name} does not exist at {path}")
    #     return open(path, mode, **kwargs)

    # def open_output(self, name, mode="w", **kwargs):
    #     """Open the named output file.

    #     Args:
    #         name (str): The name of the output.
    #         mode (str): The open mode (Default value = 'w').
    #         **kwargs (dict): Keyword arguments for `open`.

    #     Returns:
    #         File: The file object.
    #     """
    #     path = self.output_dir / name
    #     return path.open(mode, **kwargs)

    # def update_container_metadata(
    #     self, container_type, deep: bool = True, **kwargs
    # ) -> None:  # pragma: no cover
    #     """Wrapper around Metadata().update_container()."""
    #     warnings.warn(
    #         (
    #             "GearTookitContext.update_container_metadata() is deprecated. "
    #             "Please use GearTookitContext.metadata.update_container()."
    #         ),
    #         DeprecationWarning,
    #     )
    #     self.metadata.update_container(container_type, deep, **kwargs)

    # def update_file_metadata(
    #     self, file_: t.Any, deep: bool = True, **kwargs
    # ) -> None:  # pragma: no cover
    #     """Wrapper around Metadata().update_file()."""
    #     warnings.warn(
    #         (
    #             "GearTookitContext.update_file_metadata() is deprecated. "
    #             "Please use GearTookitContext.metadata.update_file()."
    #         ),
    #         DeprecationWarning,
    #     )
    #     self.metadata.update_file(
    #         file_, deep, container_type=self.destination["type"], **kwargs
    #     )

    # def update_destination_metadata(
    #     self, deep: bool = True, **kwargs
    # ) -> None:  # pragma: no cover
    #     """Wrapper around Metadata().update_container()."""
    #     warnings.warn(
    #         (
    #             "GearTookitContext.update_destination_metadata() is deprecated. "
    #             "Please use GearTookitContext.metadata.update_container()."
    #         ),
    #         DeprecationWarning,
    #     )
    #     self.metadata.update_container(self.destination["type"], deep, **kwargs)

    # def get_context_value(self, name):
    #     """Get the context input for name.
    #     (Checks the type of input selected. i.e., files are not context input) # not sure on this interpretation

    #     Args:
    #         name (str): The name of the input.

    #     Returns:
    #         dict: The input context value, or None if not found.
    #     """
    #     inp = self.get_input(name)
    #     if not inp:
    #         return None
    #     if inp["base"] != "context":
    #         raise ValueError(f"The specified input {name} is not a context input")
    #     return inp.get("value")

    # def download_session_bids(self, target_dir=None, **kwargs):
    #     """Download the session in bids format to target_dir.

    #     Args:
    #         target_dir (str): The destination directory (otherwise work/bids will be
    #             used) (Default value: 'work/bids').
    #         kwargs (dict): kwargs for `flywheel_bids.export_bids.download_bids_dir`.

    #     Returns:
    #         pathlib.Path: The absolute path to the downloaded bids directory.
    #     """
    #     (
    #         parent_id,
    #         target_dir,
    #         download_bids_dir,
    #         kwargs,
    #     ) = self._validate_bids_download(
    #         container_type="session", target_dir=target_dir, **kwargs
    #     )
    #     download_bids_dir(self.client, parent_id, "session", target_dir, **kwargs)
    #     return target_dir

    # def download_project_bids(self, target_dir=None, **kwargs):
    #     """Download the project in bids format to target_dir.

    #     Args:
    #         target_dir (str): The destination directory (otherwise work/bids will be
    #             used) (Default value = 'work/bids').
    #         src_data (bool): Whether or not to include src data (e.g. dicoms)
    #         (Default value = False).
    #         **kwargs: kwargs for ``flywheel_bids.export_bids.download_bids_dir``.

    #     Keyword Args:
    #         subjects (list): The list of subjects to include (via subject code)
    #             otherwise all subjects.
    #         sessions (list): The list of sessions to include (via session label)
    #             otherwise all sessions.
    #         folders (list): The list of folders to include (otherwise all folders) e.g.
    #             ['anat', 'func'].
    #         All the other kwargs for ``flywheel_bids.export_bids.download_bids_dir``.

    #     Returns:
    #         pathlib.Path: The absolute path to the downloaded bids directory.
    #     """
    #     (
    #         parent_id,
    #         target_dir,
    #         download_bids_dir,
    #         kwargs,
    #     ) = self._validate_bids_download(
    #         container_type="project", target_dir=target_dir, **kwargs
    #     )
    #     download_bids_dir(self.client, parent_id, "project", target_dir, **kwargs)
    #     return target_dir

    # def __enter__(self):
    #     #        if self.report_usage_statistics:
    #     #            import multiprocessing
    #     #
    #     #            self.queue = multiprocessing.Manager().Queue()
    #     #            self.process = multiprocessing.Process(
    #     #                target=worker, args=(queue, interval), kwargs={"disk_usage": disk_usage}
    #     #            )
    #     #            process.start()
    #     return self

    # def __exit__(self, exc_type, exc_value, traceback):
    #     #        if self.report_usage_statistics:
    #     #            self.process.terminate()
    #     #            # finish subprocess and report on usage.
    #     #            msg = f"Function {func.__name__} used: \n"
    #     #            while not self.queue.empty():
    #     #                time, usage = queue.get()
    #     #                msg += f"time: {time}, usage: {usage}\n"
    #     #            log.info(msg)

    #     if exc_type is None or (
    #         issubclass(exc_type, SystemExit) and exc_value.code == 0
    #     ):
    #         self.metadata.update_zip_member_count(
    #             self.output_dir, container_type=self.destination["type"]
    #         )
    #         self.metadata.write(
    #             self.output_dir, self.fail_on_validation, self._log_metadata
    #         )
    #     else:
    #         self._clean_output()

    #     if self._temp_dir:
    #         self._temp_dir.cleanup()
    #     if self._client:
    #         sdk_usage = getattr(
    #             self._client.api_client.rest_client, "request_counts", None
    #         )
    #         if not sdk_usage:
    #             log.debug("SDK profiling not available in this version of flywheel-sdk")
    #         else:
    #             log.debug(f"SDK usage:\n{pformat(sdk_usage, indent=2)}")

    # def _validate_bids_download(self, container_type, target_dir, **kwargs):
    #     """Prepare and validate `flywheel_bids.export_bids.download_bids_dir` arguments.

    #     Args:
    #         container_type (str): The container type for which to download BIDs (i.e.
    #             "session", "project")
    #         target_dir (pathlib.Path or str or None): The path to which to download the
    #             BIDs hierarchy
    #         **kwargs: kwargs for ``flywheel_bids.export_bids.download_bids_dir``

    #     Returns:
    #         (tuple): Tuple containing:
    #             (str): ID of the destinations container's parent of type
    #                 `container_type`.
    #             (pathlib.Path): Path to which BIDS will be downloaded.
    #             (function): flywheel_bids.export_bids.download_bids_dir.
    #             (dict): Keyword arguments to be passed to download_bids_dir.
    #     """
    #     # Raise a specific error if BIDS not installed
    #     download_bids_dir = self._load_download_bids()

    #     if not target_dir:
    #         target_dir = self.work_dir / "bids"
    #     elif isinstance(target_dir, pathlib.Path):
    #         pass
    #     elif isinstance(target_dir, str):
    #         target_dir = pathlib.Path(target_dir)
    #     else:
    #         raise TypeError(
    #             f"BIDs target_dir {target_dir} is of unexpected type ({type(target_dir)})"
    #         )
    #     # create target_dir if it doesn't exist
    #     if not target_dir.exists():
    #         target_dir.mkdir(parents=True)

    #     # Cleanup kwargs
    #     for key in ("subjects", "sessions", "folders"):
    #         if key in kwargs and kwargs[key] is None:
    #             kwargs.pop(key)

    #     # Resolve container type from parents
    #     dest_container = self.client.get(self.destination["id"])

    #     parent_id = dest_container.get(container_type)
    #     if parent_id is None:
    #         parent_id = dest_container.get("parents", {}).get(container_type)

    #     if parent_id is None:
    #         raise RuntimeError("Cannot find {} from destination".format(container_type))

    #     log.info("Using source container: %s=%s", container_type, parent_id)

    #     return parent_id, target_dir, download_bids_dir, kwargs

    # def _load_download_bids(self):
    #     """Load the download_bids_dir function from flywheel_bids."""
    #     try:
    #         from flywheel_bids.export_bids import (  # pylint: disable=import-outside-toplevel
    #             download_bids_dir,
    #         )

    #         return download_bids_dir
    #     except ImportError:
    #         log.error("Cannot load flywheel-bids package.")
    #         log.error('Make sure it is installed with "pip install flywheel-bids"')
    #         raise RuntimeError(
    #             "Unable to load flywheel-bids package, make sure it is installed!"
    #         )

    # @staticmethod
    # def _load_json(filepath):
    #     """Return dictionary for input json file.

    #     Args:
    #       filepath (str): Path to a JSON file.

    #     Raises:
    #         RuntimeError: If filepath cannot be parsed as JSON.

    #     Returns:
    #         (dict): The dictionary representation of the JSON file at filepath.
    #     """
    #     json_dict = dict()
    #     if os.path.isfile(filepath):
    #         try:
    #             with open(filepath, "r") as f:
    #                 json_dict = json.load(f)
    #         except json.JSONDecodeError:
    #             raise RuntimeError(f"Cannot parse {filepath} as JSON.")

    #     return json_dict

    # def _clean_output(self):
    #     if self.config.get("debug") != "debug":
    #         log.info("Cleaning output folder.")
    #         for path in pathlib.Path(self.output_dir).glob("**/*"):
    #             if path.is_file():
    #                 path.unlink()
    #             elif path.is_dir():
    #                 rmtree(path)
    #     else:
    #         log.debug(f"Debug mode, skipping cleanup of {self.output_dir}")

    # def config_from_args(self, input_args=None):
    #     """Updates config_json dictionary using input_args (or sys.argv if input_args
    #     are not provided).

    #     If config.json exists at the path provided when the GearTookitContext was
    #     instantiated, sys.argv (or input_args if provided) will be used to update the
    #     config options and inputs.

    #     Inputs are discerned on the basis that ``os.path.isfile(<config value or input
    #     path>)`` evaluates as ``True``.

    #     If no config.json exists, a config_json object will be created with the
    #     following as the default (and updated where config/inputs are provided):
    #     ``{'config': {}, 'inputs': {},
    #     'destination': {'id': 'aex', 'type': 'acquisition'}}``

    #     Args:
    #         input_args(list, optional): An optional list of arguments to provide to
    #             argparse. If not provided, ``sys.argv`` will be used instead.
    #             (Default value = None).

    #     Returns:
    #         (dict): A dictionary representation of a Flywheel gear's config.json.

    #     Examples:
    #         >>> from flywheel_gear_toolkit import GearToolkitContext
    #         >>> context = GearToolkitContext()
    #         >>> context.config_from_args([])
    #         {'config': {},
    #          'inputs': {},
    #          'destination': {'id': 'aex', 'type': 'acquisition'}}
    #         >>> context.config_from_args(input_args=['-d', '5e0612a6f999360027e1aa9d:project'])
    #         {'config': {},
    #          'inputs': {},
    #          'destination': {'id': '5e0612a6f999360027e1aa9d', 'type': 'project'}}
    #         >>> context.config_from_args(input_args=['-config_key1', 'config_value1'])
    #         {'config': {'config_key1': 'config_value1'},
    #          'inputs': {},
    #          'destination': {'id': '5e0612a6f999360027e1aa9d', 'type': 'project'}}
    #         >>> context.config_from_args(['-file_input1', '/path/to/file_input_1'])
    #         {'config': {'config_key1': 'config_value1'},
    #          'inputs': {
    #                 'file_input1': {
    #                     'base': 'file',
    #                     'hierarchy': {'acquisition', 'aex'},
    #                     'location': {'name': 'parse_args1.txt',
    #                                  'path': '/path/to/file_input_1'},
    #                     'object': {
    #                         'classification': {'Intent': [], 'Measurement': []},
    #                         'info': {},
    #                         'measurements': [],
    #                         'mimetype': '',
    #                         'modality': '',
    #                         'size': <file size>,
    #                         'tags': [],
    #                         'type': ''
    #                     }
    #                 }},
    #          'destination': {'id': '5e0612a6f999360027e1aa9d', 'type': 'project'}}
    #     """
    #     args = parse_context_args(input_args=input_args)
    #     arg_dict = args.__dict__
    #     destination = arg_dict.pop("destination")
    #     if not self.config_json:
    #         config_dict = {"config": {}, "inputs": {}}
    #     else:
    #         config_dict = self.config_json

    #     if not config_dict.get("destination") or destination != "aex:acquisition":
    #         config_dict["destination"] = dict(
    #             zip(["id", "type"], destination.split(":"))
    #         )
    #     api_key = arg_dict.pop("api_key")
    #     if api_key:
    #         config_dict["inputs"]["api-key"] = {
    #             "base": "api-key",
    #             "key": api_key,
    #         }

    #     for key, value in arg_dict.items():
    #         parent_container_type = "acquisition"
    #         parent_id = "aex"
    #         value = str(value)
    #         path_str = value
    #         if len(value.split(":")) == 2:
    #             path_str, parent_container_type = value.split(":")
    #         elif len(value.split(":")) == 3:
    #             path_str, parent_container_type, parent_id = value.split(":")
    #         if os.path.isfile(str(path_str)):

    #             if not config_dict["inputs"].get(key):
    #                 config_dict["inputs"][key] = {
    #                     "base": "file",
    #                     "hierarchy": {
    #                         "id": parent_id,
    #                         "type": parent_container_type,
    #                     },
    #                     "location": {
    #                         "name": os.path.basename(path_str),
    #                         "path": path_str,
    #                     },
    #                     "object": FILE_OBJECT_DICT,
    #                 }
    #                 config_dict["inputs"][key]["object"]["size"] = os.stat(
    #                     path_str
    #                 ).st_size
    #         else:
    #             if not config_dict["config"].get(key):
    #                 config_dict["config"][key] = convert_config_type(value)

        # self.config_json = config_dict
        # return self.config_json
