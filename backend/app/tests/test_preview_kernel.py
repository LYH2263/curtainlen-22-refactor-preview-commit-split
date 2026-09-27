"""PreviewKernel 单测:纯计算,不得连接 SQLite。"""
import subprocess
import sys
from pathlib import Path

from app.services.preview_kernel import PreviewKernel

WINDOW = {"id": 1, "name": "客厅落地窗", "width": 3.0, "height": 2.6, "fullness": 2.0, "data_quality": "clean"}
FABRIC = {"id": 1, "name": "遮光1.4m", "fabric_width": 1.4, "hem_top": 0.10, "hem_bottom": 0.15, "data_quality": "clean"}


def test_preview_panels_cut_height_meters():
    r = PreviewKernel().preview(WINDOW, FABRIC, {"default_fullness": "2.0"})
    assert r["panels"] == 5
    assert r["cut_height"] == 2.85
    assert r["meters"] == 14.25
    assert r["window"] is WINDOW and r["fabric"] is FABRIC


def test_preview_falls_back_to_default_fullness():
    w = {**WINDOW, "fullness": None}
    r = PreviewKernel().preview(w, FABRIC, {"default_fullness": "1.5"})
    assert r["finished_width"] == 4.5
    assert r["panels"] == 4


def test_preview_deterministic_same_inputs():
    k = PreviewKernel()
    assert k.preview(WINDOW, FABRIC) == k.preview(WINDOW, FABRIC)


def test_kernel_module_does_not_import_db():
    code = "import sys; import app.services.preview_kernel; print('app.db' in sys.modules)"
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, check=True,
        cwd=Path(__file__).resolve().parents[2],
    )
    assert out.stdout.strip() == "False"
