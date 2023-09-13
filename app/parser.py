"""Parser module to parse gear config.json."""

from typing import Tuple
from flywheel_gear_toolkit import GearToolkitContext

def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[str, bool, bool, bool, bool, bool]:
    """Parses the config info.
    Args:
        gear_context: Context.

    Returns:
        Tuple of input image path, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81

    """
    input = gear_context.get_input_path("input")
    HarvardOxford_Cortical = gear_context.config.get("HarvardOxford_Cortical")
    HarvardOxford_Subcortical = gear_context.config.get("HarvardOxford_Subcortical")
    Glasser = gear_context.config.get("Glasser")
    Jolly = gear_context.config.get("Jolly")
    ICBM81 = gear_context.config.get("ICBM81")

    return input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81