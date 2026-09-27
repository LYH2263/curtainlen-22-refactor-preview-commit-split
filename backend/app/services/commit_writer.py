"""CommitWriter: validate entities, run PreviewKernel, persist to calc_runs.

POST /estimate 保存必须走这里。算与写分离:计算委托给 PreviewKernel,
本类只负责校验、取数、落库,并在写入后按 run_id 读回核对口径一致。
"""
from fastapi import HTTPException

from app.repositories import fabrics, history, settings_repo, windows
from app.services.preview_kernel import PreviewKernel


class CommitWriter:
    def __init__(self, kernel: PreviewKernel | None = None):
        self.kernel = kernel or PreviewKernel()

    def commit(self, window_id: int, fabric_id: int, note: str = "") -> dict:
        w = windows.get_window(window_id)
        f = fabrics.get_fabric(fabric_id)
        if not w or not f:
            raise HTTPException(404, "not found")
        if w.get("data_quality") == "dirty":
            raise HTTPException(422, "dirty window")
        result = self.kernel.preview(w, f, settings_repo.get_all())
        calc = {k: result[k] for k in ("finished_width", "panels", "cut_height", "meters", "fabric_width")}
        run_id = history.insert_run(window_id, fabric_id, calc, note)
        stored = history.get_run(run_id)
        if stored is None or stored["result"] != calc:
            raise HTTPException(500, "calc_runs readback mismatch")
        return {"window": w, "fabric": f, "run_id": run_id, **calc}
