"""路由层:GET 试算走 PreviewKernel,POST 保存走 CommitWriter,
同窗同布下预览回包与提交后按 run_id 读回的 panels/meters 口径一致。"""
import pytest
from fastapi.testclient import TestClient

from app import seed
from app.main import app
from app.repositories import history


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "t.db")
    seed.init_db()
    return TestClient(app)


def test_get_preview_does_not_persist(client):
    r = client.get("/api/estimate", params={"window_id": 1, "fabric_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["panels"] == 5 and body["meters"] == 14.25
    assert "run_id" not in body
    assert history.list_runs() == []


def test_post_commit_persists_and_matches_preview(client):
    preview = client.get("/api/estimate", params={"window_id": 2, "fabric_id": 2}).json()
    r = client.post("/api/estimate", json={"window_id": 2, "fabric_id": 2, "note": "hi"})
    assert r.status_code == 200
    committed = r.json()
    assert committed["run_id"]
    stored = history.get_run(committed["run_id"])
    for key in ("panels", "cut_height", "meters"):
        assert preview[key] == committed[key] == stored["result"][key]


def test_post_rejects_dirty_window(client):
    r = client.post("/api/estimate", json={"window_id": 3, "fabric_id": 1})
    assert r.status_code == 422
