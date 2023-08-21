"""The module to host a few constants"""

FILE_OBJECT_DICT = {
    "classification": {"Intent": [], "Measurement": []},
    "info": {},
    "measurements": [],
    "mimetype": "",
    "modality": "",
    "size": 0,
    "tags": [],
    "type": "",
}

TOP_DOWN_PARENT_HIERARCHY = ["group", "project", "subject", "session", "acquisition"]
BOTTOM_UP_PARENT_HIERARCHY = list(reversed(TOP_DOWN_PARENT_HIERARCHY))
FW_HOME = "/flywheel/v0"
