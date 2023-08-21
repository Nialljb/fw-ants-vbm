"""The fw_gear_bids_qsiprep package."""
from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__package__)
except PackageNotFoundError:  # pragma: no cover
    pass
