"""CommitWriter 测例:写入 calc_runs 后按 run_id 读回同一组数字。"""
import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history, settings_repo, windows, fabrics
from app.services.commit_writer import CommitWriter
from app.services.preview_kernel import PreviewKernel


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "t.db")
    seed.init_db()
    return tmp_path / "t.db"


def test_commit_writes_then_reads_back_same_numbers(db):
    out = CommitWriter().commit(1, 1, "n1")
    assert out["run_id"]
    stored = history.get_run(out["run_id"])
    assert stored["window_id"] == 1 and stored["fabric_id"] == 1
    assert stored["note"] == "n1"
    assert stored["result"]["panels"] == out["panels"] == 5
    assert stored["result"]["cut_height"] == out["cut_height"] == 2.85
    assert stored["result"]["meters"] == out["meters"] == 14.25


def test_commit_matches_preview_kernel_same_window_fabric(db):
    w = windows.get_window(1)
    f = fabrics.get_fabric(1)
    preview = PreviewKernel().preview(w, f, settings_repo.get_all())
    out = CommitWriter().commit(1, 1)
    assert out["panels"] == preview["panels"]
    assert out["cut_height"] == preview["cut_height"]
    assert out["meters"] == preview["meters"]


def test_commit_rejects_unknown_entities(db):
    with pytest.raises(HTTPException) as e:
        CommitWriter().commit(999, 1)
    assert e.value.status_code == 404


def test_commit_rejects_dirty_window(db):
    with pytest.raises(HTTPException) as e:
        CommitWriter().commit(3, 1)
    assert e.value.status_code == 422
