"""PreviewKernel: pure estimate preview computation.

No database access, no HTTP imports — same inputs always yield the same
panels/cut_height/meters. GET /estimate 试算只走这里。
"""
from app.engines.curtain_math import fabric_meters

DEFAULT_FULLNESS = 2.0


class PreviewKernel:
    def preview(self, window: dict, fabric: dict, settings: dict | None = None) -> dict:
        settings = settings or {}
        fullness = float(window.get("fullness") or settings.get("default_fullness", DEFAULT_FULLNESS))
        calc = fabric_meters(
            window["width"],
            window["height"],
            fullness,
            fabric["hem_top"],
            fabric["hem_bottom"],
            fabric["fabric_width"],
        )
        return {"window": window, "fabric": fabric, **calc}
