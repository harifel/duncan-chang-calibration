"""Check that the figure scripts run on the demo data and the fit is good."""
import numpy as np
import pytest

from src import make_viz_examples as viz
from src.duncan_chang import rmse


@pytest.fixture(scope="module")
def demo():
    strain, q_meas, _ = viz.load()
    return strain, q_meas


def test_figures_are_written(tmp_path, monkeypatch, demo):
    monkeypatch.setattr(viz, "OUT", tmp_path)       # do not touch graphics/
    monkeypatch.chdir(viz.Path(__file__).resolve().parents[1])
    viz.main()
    for name in ["viz_bad.png", "viz_good.png", "viz_rmse.png", "optimizer_history.png"]:
        assert (tmp_path / name).stat().st_size > 1000


def test_final_rmse_is_below_3_kpa(demo):
    strain, q_meas = demo
    steps, theta_end = viz.run_optimizer(strain, q_meas)
    assert rmse(theta_end, strain, q_meas) < 3.0
    assert 50 < steps[0][1] < 60                     # start about 56 kPa
    assert 60 < rmse(viz.GUESS, strain, q_meas) < 68  # manual guess about 64 kPa


def test_run_is_deterministic(demo):
    strain, q_meas = demo
    first = viz.run_optimizer(strain, q_meas)[1]
    second = viz.run_optimizer(strain, q_meas)[1]
    assert np.array_equal(first, second)
