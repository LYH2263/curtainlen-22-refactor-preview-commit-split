from fastapi import APIRouter, HTTPException, Query
from app.engines.preview_kernel import PreviewKernel
from app.repositories import fabrics, settings_repo, windows
from app.schemas.estimate import EstimateRequest
from app.services.commit_writer import CommitWriter

router = APIRouter()


@router.get("/estimate")
def get_est(window_id: int = Query(...), fabric_id: int = Query(...)):
    w = windows.get_window(window_id)
    f = fabrics.get_fabric(fabric_id)
    if not w or not f:
        raise HTTPException(404, "not found")
    if w.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty window")
    settings = settings_repo.get_all()
    fullness = PreviewKernel.resolve_fullness(w, settings.get("default_fullness", 2.0))
    return {"window": w, "fabric": f, "run_id": None, **PreviewKernel.preview(w, f, fullness)}


@router.post("/estimate")
def post_est(body: EstimateRequest):
    return CommitWriter.commit(body.window_id, body.fabric_id, body.note)
