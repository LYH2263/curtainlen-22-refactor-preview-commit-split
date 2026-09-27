"""PreviewKernel: pure calculation kernel for estimates.

No database access, no FastAPI imports. Takes already-resolved plain
inputs (window dict, fabric dict, fullness) and returns the canonical
calculation result: panels / cut_height / meters. The same kernel output
is what CommitWriter persists, so preview and committed runs share one
caliber.
"""
from app.engines.curtain_math import fabric_meters

KERNEL_KEYS = ("panels", "cut_height", "meters")


class PreviewKernel:
    @staticmethod
    def resolve_fullness(window: dict, default_fullness: float) -> float:
        """Window fullness wins; fall back to the settings default."""
        return float(window.get("fullness") or default_fullness)

    @staticmethod
    def preview(window: dict, fabric: dict, fullness: float) -> dict:
        calc = fabric_meters(
            window["width"],
            window["height"],
            fullness,
            fabric["hem_top"],
            fabric["hem_bottom"],
            fabric["fabric_width"],
        )
        return {k: calc[k] for k in KERNEL_KEYS}
