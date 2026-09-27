from fastapi import APIRouter, HTTPException, Query
from app.repositories import fabrics, settings_repo, windows
from app.schemas.estimate import EstimateRequest
from app.services.commit_writer import CommitWriter
from app.services.preview_kernel import PreviewKernel

router = APIRouter()
kernel = PreviewKernel()
writer = CommitWriter(kernel)


@router.get("/estimate")
def get_est(window_id: int = Query(...), fabric_id: int = Query(...)):
    w = windows.get_window(window_id)
    f = fabrics.get_fabric(fabric_id)
    if not w or not f:
        raise HTTPException(404, "not found")
    if w.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty window")
    return kernel.preview(w, f, settings_repo.get_all())


@router.post("/estimate")
def post_est(body: EstimateRequest):
    return writer.commit(body.window_id, body.fabric_id, body.note)
