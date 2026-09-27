"""CommitWriter tests: persist a run, then read it back by run_id."""
import pytest
from fastapi import HTTPException

from app import seed
from app.engines.preview_kernel import PreviewKernel
from app.repositories import history
from app.repositories.windows import get_window
from app.repositories.fabrics import get_fabric
from app.services.commit_writer import CommitWriter


@pytest.fixture()
def seeded_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test_commit.db"
    monkeypatch.setattr("app.db.DB_PATH", db_file)
    seed.init_db()
    return db_file


def test_commit_writes_run_and_reads_back_same_numbers(seeded_db):
    w, f = get_window(1), get_fabric(1)
    preview = PreviewKernel.preview(w, f, PreviewKernel.resolve_fullness(w, 2.0))

    out = CommitWriter.commit(1, 1, "check")

    assert out["run_id"] is not None
    assert out["panels"] == preview["panels"]
    assert out["meters"] == preview["meters"]

    run = history.get_run(out["run_id"])
    assert run is not None
    assert run["note"] == "check"
    assert run["result"]["panels"] == preview["panels"]
    assert run["result"]["cut_height"] == preview["cut_height"]
    assert run["result"]["meters"] == preview["meters"]


def test_preview_and_commit_share_caliber(seeded_db):
    w, f = get_window(2), get_fabric(2)
    fullness = PreviewKernel.resolve_fullness(w, 2.0)
    preview = PreviewKernel.preview(w, f, fullness)

    run_id = CommitWriter.commit(2, 2)["run_id"]
    persisted = history.get_run(run_id)["result"]

    assert persisted["panels"] == preview["panels"]
    assert persisted["meters"] == preview["meters"]


def test_commit_rejects_dirty_window(seeded_db):
    with pytest.raises(HTTPException) as exc:
        CommitWriter.commit(3, 1)
    assert exc.value.status_code == 422
    assert history.list_runs() == []


def test_commit_rejects_missing_entities(seeded_db):
    with pytest.raises(HTTPException) as exc:
        CommitWriter.commit(999, 1)
    assert exc.value.status_code == 404
    assert history.list_runs() == []
