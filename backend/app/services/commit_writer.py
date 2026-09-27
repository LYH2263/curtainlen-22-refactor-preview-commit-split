"""CommitWriter: the only path that persists estimates.

Validates the window/fabric entities, resolves fullness from settings,
delegates the math to PreviewKernel, then writes the kernel result into
calc_runs. Reading the run back by run_id yields the same panels/meters
as a preview for the same window+fabric.
"""
from fastapi import HTTPException

from app.engines.preview_kernel import PreviewKernel
from app.repositories import fabrics, history, settings_repo, windows


class CommitWriter:
    @staticmethod
    def commit(window_id: int, fabric_id: int, note: str = "") -> dict:
        w = windows.get_window(window_id)
        f = fabrics.get_fabric(fabric_id)
        if not w or not f:
            raise HTTPException(404, "not found")
        if w.get("data_quality") == "dirty":
            raise HTTPException(422, "dirty window")
        settings = settings_repo.get_all()
        fullness = PreviewKernel.resolve_fullness(w, settings.get("default_fullness", 2.0))
        result = PreviewKernel.preview(w, f, fullness)
        run_id = history.insert_run(window_id, fabric_id, result, note)
        return {"run_id": run_id, **result}
