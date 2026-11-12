"""Duncan-Chang (hyperbolic) stress-strain model and calibration tools."""
import numpy as np
from scipy.optimize import least_squares

SIGMA3 = 100.0   # confining pressure [kPa]
RF = 0.9         # failure ratio (fixed)


def forward_model(theta, strain, sigma3=SIGMA3, rf=RF):
    """Deviator stress q [kPa] for theta = (Ei [kPa], phi [deg], c [kPa])."""
    ei, phi, c = theta
    phi_rad = np.radians(phi)
    q_f = (2 * c * np.cos(phi_rad) + 2 * sigma3 * np.sin(phi_rad)) / (1 - np.sin(phi_rad))
    q_ult = q_f / rf
    return strain / (1.0 / ei + strain / q_ult)


def add_noise(q, noise_factor=0.01, seed=42):
    """Add Gaussian noise. Noise std is a fraction of the local stress."""
    rng = np.random.default_rng(seed)
    noisy = q + rng.normal(0.0, noise_factor * q)
    noisy[0] = 0.0
    return noisy


def rmse(theta, strain, q_measured):
    """Root mean square error between model and measurement [kPa]."""
    return float(np.sqrt(np.mean((forward_model(theta, strain) - q_measured) ** 2)))


def calibrate(strain, q_measured, theta0, bounds):
    """Find the parameters with the smallest misfit (bounded least squares)."""
    def residuals(theta):
        return forward_model(theta, strain) - q_measured
    lo, hi = zip(*bounds)
    # x_scale: parameters differ by orders of magnitude
    return least_squares(residuals, theta0, bounds=(lo, hi), x_scale=np.array(hi) - np.array(lo))
