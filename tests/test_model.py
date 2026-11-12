import numpy as np
from src.duncan_chang import forward_model, add_noise, calibrate

STRAIN = np.linspace(0, 0.05, 200)
TRUE = np.array([50e3, 30.0, 20.0])

def test_zero_strain_gives_zero_stress():
    assert forward_model(TRUE, STRAIN)[0] == 0.0

def test_stress_is_increasing():
    assert np.all(np.diff(forward_model(TRUE, STRAIN)) > 0)

def test_calibration_recovers_ei_and_noise_free_curve():
    q = forward_model(TRUE, STRAIN)
    res = calibrate(STRAIN, q, [100e3, 25.0, 10.0], [(10e3, 200e3), (20, 40), (0, 30)])
    assert np.max(np.abs(forward_model(res.x, STRAIN) - q)) < 1.0
