"""PreviewKernel tests: pure math, must never touch SQLite."""
import sqlite3

import pytest

from app.engines.preview_kernel import KERNEL_KEYS, PreviewKernel


@pytest.fixture(autouse=True)
def _no_sqlite(monkeypatch):
    def _blocked(*args, **kwargs):
        raise AssertionError("PreviewKernel must not connect to SQLite")
    monkeypatch.setattr(sqlite3, "connect", _blocked)


WINDOW = {"width": 3.0, "height": 2.6, "fullness": 2.0}
FABRIC = {"fabric_width": 1.4, "hem_top": 0.10, "hem_bottom": 0.15}


def test_preview_panels_cut_height_meters():
    r = PreviewKernel.preview(WINDOW, FABRIC, 2.0)
    assert r == {"panels": 5, "cut_height": 2.85, "meters": 14.25}
    assert set(r) == set(KERNEL_KEYS)


def test_resolve_fullness_uses_window_then_default():
    assert PreviewKernel.resolve_fullness({"fullness": 2.2}, 2.0) == 2.2
    assert PreviewKernel.resolve_fullness({"fullness": None}, 2.0) == 2.0
    assert PreviewKernel.resolve_fullness({}, 1.8) == 1.8


def test_preview_narrow_single_panel():
    r = PreviewKernel.preview(
        {"width": 1.0, "height": 2.0, "fullness": 1.5},
        {"fabric_width": 2.8, "hem_top": 0.0, "hem_bottom": 0.0},
        1.5,
    )
    assert r["panels"] == 1
    assert r["cut_height"] == 2.0
    assert r["meters"] == 2.0


def test_preview_is_deterministic():
    a = PreviewKernel.preview(WINDOW, FABRIC, 2.0)
    b = PreviewKernel.preview(WINDOW, FABRIC, 2.0)
    assert a == b
