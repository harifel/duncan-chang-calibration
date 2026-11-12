"""Make teaching animations: RMSE residuals and optimizer search.

Run from the repo root:  python -m src.make_gifs
Output: graphics/*.gif, graphics/*.png, graphics/frames_*/ (PNG frames for LaTeX 'animate').
The slides in slides/ use these files.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from scipy.optimize import least_squares

from src.duncan_chang import forward_model, add_noise, rmse

OUT = Path("graphics")
STRAIN = np.linspace(0, 0.05, 200)
THETA_TRUE = [50e3, 30.0, 20.0]
BOUNDS = [(10e3, 200e3), (20.0, 40.0), (0.0, 30.0)]
START = [100e3, 25.0, 10.0]
GUESSES = {"Guess A": [100e3, 25, 10], "Guess B": [20e3, 35, 5],
           "Guess C": [150e3, 22, 28]}

GRAY, ACCENT, INK = "#9a9a9a", "#e4002b", "#222222"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.dpi": 100})

if not Path("data/synthetic_test.csv").exists():
    from src import make_data
    make_data.main()
Q_MEAS = np.loadtxt("data/synthetic_test.csv", delimiter=",", skiprows=1)[:, 1]
DEMO_THETA = [60e3, 25.0, 10.0]      # example values for the model slide (not the truth)


def save_gif(frames_dir, gif_name, fps_ms=120, hold_last=10):
    files = sorted(frames_dir.glob("f-*.png"))
    ims = [Image.open(f).convert("P", palette=Image.ADAPTIVE) for f in files]
    durs = [fps_ms] * len(ims)
    durs[-1] = fps_ms * hold_last
    ims[0].save(OUT / gif_name, save_all=True, append_images=ims[1:],
                duration=durs, loop=0, disposal=2)


def fresh(d):
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("f-*.png"):
        f.unlink()
    return d


# ---------------------------------------------------------------- RMSE
PARAM_LABELS = ["E_i [kPa]", "phi [deg]", "c [kPa]"]


def param_table(ax, theta, name, rmse_value, show_true=True):
    """Small table: true parameters versus the parameters used in the model."""
    ax.axis("off")
    fmt = lambda v: f"{v:,.1f}".replace(",", " ")
    if show_true:
        rows = [[lab, fmt(t), fmt(u)] for lab, t, u in zip(PARAM_LABELS, THETA_TRUE, theta)]
        cols = ["Parameter", "True", name]
    else:
        rows = [[lab, fmt(u)] for lab, u in zip(PARAM_LABELS, theta)]
        cols = ["Parameter", name]
    tab = ax.table(cellText=rows, colLabels=cols,
                   loc="center", cellLoc="right", colLoc="right")
    tab.auto_set_font_size(False)
    tab.set_fontsize(12)
    tab.scale(1.0, 1.9)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#f0f0f0")
        if c == 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"
    ax.set_title(f"RMSE = {rmse_value:.1f} kPa", loc="left", fontsize=14,
                 color=ACCENT, weight="bold")


def draw_residuals(ax, theta, title):
    q_mod = forward_model(theta, STRAIN)
    ax.vlines(STRAIN[::4] * 100, q_mod[::4], Q_MEAS[::4], color=ACCENT,
              lw=1.2, alpha=0.8, label="difference")
    ax.plot(STRAIN * 100, Q_MEAS, ".", color=GRAY, ms=4, label="measured")
    ax.plot(STRAIN * 100, q_mod, color=INK, lw=2, label="model")
    ax.set_xlabel("Strain [%]")
    ax.set_ylabel("Stress q [kPa]")
    ax.set_ylim(0, 330)
    ax.set_title(title, loc="left", fontsize=13)
    ax.legend(loc="lower right", frameon=False)


def residual_figure(theta, name, show_true=True):
    fig, (ax, axt) = plt.subplots(1, 2, figsize=(11, 4.2),
                                  gridspec_kw={"width_ratios": [1.5, 1]})
    draw_residuals(ax, theta, name)
    param_table(axt, theta, name, rmse(theta, STRAIN, Q_MEAS), show_true)
    fig.tight_layout()
    return fig


def make_rmse():
    """Blind version first (no true values), then the reveal version."""
    d = fresh(OUT / "frames_rmse_blind")
    k = 0
    for name, th in GUESSES.items():
        for _ in range(8):
            fig = residual_figure(th, name, show_true=False)
            fig.savefig(d / f"f-{k:03d}.png"); plt.close(fig); k += 1
    save_gif(d, "rmse_residuals_blind.gif", fps_ms=150, hold_last=6)
    fig = residual_figure(GUESSES["Guess A"], "Guess A", show_true=False)
    fig.savefig(OUT / "rmse_residuals_blind.png", dpi=200); plt.close(fig)

    d = fresh(OUT / "frames_rmse")
    thetas = list(GUESSES.items()) + [("Optimized", least_squares(
        lambda t: forward_model(t, STRAIN) - Q_MEAS, START,
        bounds=tuple(zip(*BOUNDS)),
        x_scale=np.array([b[1] - b[0] for b in BOUNDS])).x)]
    k = 0
    for name, th in thetas:
        for _ in range(8):
            fig = residual_figure(th, name)
            fig.savefig(d / f"f-{k:03d}.png"); plt.close(fig); k += 1
    save_gif(d, "rmse_residuals.gif", fps_ms=150, hold_last=6)
    return k


def make_model_and_data():
    """Model slide (example parameters) and the measured data (no truth)."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(STRAIN * 100, forward_model(DEMO_THETA, STRAIN), color=INK, lw=2)
    # E_i = initial slope of the curve (q = E_i * strain; strain axis is in %)
    e_pct = DEMO_THETA[0] / 100
    x_end = 0.3
    ax.plot([0, x_end], [0, e_pct * x_end], "--", color=ACCENT, lw=2.2)
    ax.annotate(r"initial slope $E_i$", xy=(x_end * 0.6, e_pct * x_end * 0.6),
                xytext=(0.8, 40), color=ACCENT, fontsize=12,
                arrowprops=dict(arrowstyle="->", color=ACCENT))
    # phi' and c' set the ultimate stress that the curve approaches at large strain
    q_end = float(forward_model(DEMO_THETA, np.array([10.0]))[0])
    ax.axhline(q_end, xmin=0.05, color=GRAY, ls="--", lw=1.5)
    ax.text(5.0, q_end + 8, r"ultimate stress: set by $\varphi'$ and $c'$",
            ha="right", color=INK, fontsize=12)
    ax.set_xlabel("Strain [%]"); ax.set_ylabel("Stress q [kPa]"); ax.set_ylim(0, 330)
    ax.set_title("Model with example parameters", loc="left")
    fig.tight_layout(); fig.savefig(OUT / "model_demo.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(STRAIN * 100, Q_MEAS, ".", color=GRAY, ms=5)
    ax.set_xlabel("Strain [%]"); ax.set_ylabel("Stress q [kPa]"); ax.set_ylim(0, 330)
    ax.set_title("Measured data (noisy)", loc="left")
    fig.tight_layout(); fig.savefig(OUT / "measured_only.png", dpi=200); plt.close(fig)


# ----------------------------------------------------------- optimizer
def run_optimizer():
    evals = []
    def res(t):
        evals.append(np.array(t))
        return forward_model(t, STRAIN) - Q_MEAS
    r = least_squares(res, START, bounds=tuple(zip(*BOUNDS)),
                      x_scale=np.array([b[1] - b[0] for b in BOUNDS]))
    return np.array(evals), r.x


def landscape_phi_c(ei_fixed):
    ph = np.linspace(20, 40, 140)
    c = np.linspace(0, 30, 140)
    P, C = np.meshgrid(ph, c)
    phr = np.radians(P)
    qf = (2 * C * np.cos(phr) + 200 * np.sin(phr)) / (1 - np.sin(phr))
    q = STRAIN[None, None, :] / (1 / ei_fixed + STRAIN[None, None, :] / (qf[..., None] / 0.9))
    return P, C, np.sqrt(np.mean((q - Q_MEAS) ** 2, axis=-1))


def landscape(c_fixed):
    ei = np.linspace(10e3, 150e3, 140)
    ph = np.linspace(20, 40, 140)
    E, P = np.meshgrid(ei, ph)
    phr = np.radians(P)
    qf = (2 * c_fixed * np.cos(phr) + 200 * np.sin(phr)) / (1 - np.sin(phr))
    qult = qf / 0.9
    q = STRAIN[None, None, :] / (1 / E[..., None] + STRAIN[None, None, :] / qult[..., None])
    return E, P, np.sqrt(np.mean((q - Q_MEAS) ** 2, axis=-1))


# Fixed axes layout for the 15 x 8 in "search" figures (3 columns x 2 rows).
# The frames and the section figure use the same numbers, so the maps sit at the same
# place on every slide.
def fixed_layout(fig):
    fig.subplots_adjust(left=0.06, right=0.985, top=0.94, bottom=0.095, wspace=0.30, hspace=0.42)


def draw_map(ax, X, Y, Z, xs, ys, path_idx, true_xy, xlabel, ylabel, title):
    levels = np.geomspace(max(Z.min(), 1), Z.max(), 14)
    ax.contourf(X, Y, Z, levels=levels, cmap="Blues_r", alpha=0.9)
    ax.plot(xs, ys, ".", color=INK, ms=5, label="simulations")
    ax.plot(np.array(xs)[path_idx], np.array(ys)[path_idx], "-", color=ACCENT, lw=2)
    ax.plot(*true_xy, "*", color="gold", mec=INK, ms=16, label="true value")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.legend(loc="upper right", frameon=True, fontsize=9)


def make_optimizer():
    d = fresh(OUT / "frames_opt")
    evals, th_fit = run_optimizer()
    costs = np.array([rmse(t, STRAIN, Q_MEAS) for t in evals])
    best_idx = np.minimum.accumulate(costs)
    E, P, Z = landscape(THETA_TRUE[2])
    P2, C2, Z2 = landscape_phi_c(THETA_TRUE[0])
    n = len(evals)
    best_ids = [int(np.argmin(costs[:k + 1])) for k in range(n)]
    for k in range(n):
        th_b = evals[best_ids[k]]
        path_idx = sorted(set(best_ids[:k + 1]))
        fig, axs = plt.subplots(2, 3, figsize=(15, 8))
        ax = axs[0]
        # row 1: curve | E-phi map | RMSE history
        ax[0].plot(STRAIN * 100, Q_MEAS, ".", color=GRAY, ms=4, label="measured")
        ax[0].plot(STRAIN * 100, forward_model(th_b, STRAIN), color=ACCENT,
                   lw=2.2, label="best model so far")
        ax[0].set_xlabel("Strain [%]"); ax[0].set_ylabel("Stress q [kPa]")
        ax[0].set_ylim(0, 330); ax[0].legend(loc="lower right", frameon=False)
        ax[0].set_title("Curve", loc="left")
        draw_map(ax[1], E / 1e3, P, Z, evals[:k + 1, 0] / 1e3, evals[:k + 1, 1],
                 path_idx, (THETA_TRUE[0] / 1e3, THETA_TRUE[1]),
                 "$E_i$ [MPa]", "$\\varphi$ [deg]",
                 f"Map 1: $E_i$ and $\\varphi$  ($c$ = {THETA_TRUE[2]:.0f} kPa)")
        ax[2].step(np.arange(k + 1) + 1, best_idx[:k + 1], where="post", color=ACCENT, lw=2)
        ax[2].set_xlim(1, n); ax[2].set_ylim(best_idx.min() * 0.8, costs.max() * 1.2)
        ax[2].set_yscale("log")
        ax[2].set_xlabel("Number of simulations"); ax[2].set_ylabel("Best RMSE [kPa]")
        ax[2].set_title(f"RMSE = {best_idx[k]:.1f} kPa", loc="left")
        # row 2: table | phi-c map | parameter history
        param_table(axs[1][0], th_b, "Best so far", costs[best_ids[k]])
        draw_map(axs[1][1], P2, C2, Z2, evals[:k + 1, 1], evals[:k + 1, 2],
                 path_idx, (THETA_TRUE[1], THETA_TRUE[2]),
                 "$\\varphi$ [deg]", "$c$ [kPa]",
                 f"Map 2: $\\varphi$ and $c$  ($E_i$ = {THETA_TRUE[0]/1e3:.0f} MPa)")
        hist = np.array([evals[best_ids[j]] for j in range(k + 1)]) / np.array(THETA_TRUE)
        for col, lab, ls in zip(range(3), ["$E_i$", "$\\varphi$", "$c$"], ["-", "--", ":"]):
            axs[1][2].plot(np.arange(k + 1) + 1, hist[:, col], ls, color=INK, lw=2, label=lab)
        axs[1][2].axhline(1.0, color=ACCENT, lw=1)
        axs[1][2].set_xlim(1, n); axs[1][2].set_ylim(0.3, 2.1)
        axs[1][2].set_xlabel("Number of simulations")
        axs[1][2].set_ylabel("Parameter / true value")
        axs[1][2].set_title("Parameters (1 = true)", loc="left")
        axs[1][2].legend(loc="upper right", frameon=False, ncol=3)
        fixed_layout(fig)
        fig.savefig(d / f"f-{k:03d}.png", dpi=80); plt.close(fig)
    save_gif(d, "optimizer_search.gif", fps_ms=130, hold_last=12)
    return n


# --------------------------------------------------- cross-sections of the maps
def make_sections():
    """Same 3 x 2 grid as the search frames: maps in column 2 (with a section line through the
    true value), the RMSE along each line in column 3. Column 1 stays empty."""
    E, P, Z = landscape(THETA_TRUE[2])
    P2, C2, Z2 = landscape_phi_c(THETA_TRUE[0])
    i1 = np.argmin(abs(P[:, 0] - THETA_TRUE[1]))      # map 1: phi = true value, E_i varies
    j2 = np.argmin(abs(C2[:, 0] - THETA_TRUE[2]))     # map 2: c = true value, phi varies
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    for ax in axs[:, 0]:
        ax.axis("off")
    maps = [(axs[0][1], E / 1e3, P, Z, THETA_TRUE[0] / 1e3, THETA_TRUE[1], "$E_i$ [MPa]",
             "$\\varphi$ [deg]", f"Map 1: $E_i$ and $\\varphi$  ($c$ = {THETA_TRUE[2]:.0f} kPa)", THETA_TRUE[1]),
            (axs[1][1], P2, C2, Z2, THETA_TRUE[1], THETA_TRUE[2], "$\\varphi$ [deg]",
             "$c$ [kPa]", f"Map 2: $\\varphi$ and $c$  ($E_i$ = {THETA_TRUE[0]/1e3:.0f} MPa)", THETA_TRUE[2])]
    for ax, X, Y, Zm, tx, ty, xl, yl, ttl, level in maps:
        ax.contourf(X, Y, Zm, levels=np.geomspace(max(Zm.min(), 1), Zm.max(), 14),
                    cmap="Blues_r", alpha=0.9)
        ax.axhline(level, color=ACCENT, ls="--", lw=2.2)
        ax.plot(tx, ty, "*", color="gold", mec=INK, ms=16)
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(ttl, loc="left")
    profiles = [(axs[0][2], E[i1] / 1e3, Z[i1], THETA_TRUE[0] / 1e3, "$E_i$ [MPa]"),
                (axs[1][2], P2[j2], Z2[j2], THETA_TRUE[1], "$\\varphi$ [deg]")]
    for ax, x, z, tx, xl in profiles:
        ax.plot(x, z, color=ACCENT, lw=2.2)
        ax.axvline(tx, color=INK, ls=":", lw=1.2)
        ax.set_yscale("log"); ax.set_xlabel(xl); ax.set_ylabel("RMSE [kPa]")
        ax.set_title("RMSE along the dashed line", loc="left")
    fixed_layout(fig)
    fig.savefig(OUT / "map_sections.png", dpi=80); plt.close(fig)


# --------------------------------------------------- identifiability map
def make_identifiability():
    ph = np.linspace(20, 40, 160); c = np.linspace(0, 30, 160)
    P, C = np.meshgrid(ph, c); phr = np.radians(P)
    qf = (2 * C * np.cos(phr) + 200 * np.sin(phr)) / (1 - np.sin(phr))
    q = STRAIN[None, None, :] / (1 / 50e3 + STRAIN[None, None, :] / (qf[..., None] / 0.9))
    Z = np.sqrt(np.mean((q - Q_MEAS) ** 2, axis=-1))
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    cs = ax.contourf(P, C, Z, levels=np.geomspace(max(Z.min(), 1), Z.max(), 14),
                     cmap="Blues_r")
    ax.plot(THETA_TRUE[1], THETA_TRUE[2], "*", color="gold", mec=INK, ms=16, label="true value")
    ax.set_xlabel("$\\varphi$ [deg]"); ax.set_ylabel("$c$ [kPa]")
    ax.set_title("RMSE map ($E_i$ = 50 MPa): a long valley", loc="left")
    fig.colorbar(cs, label="RMSE [kPa]"); ax.legend(loc="upper right")
    fig.tight_layout(); fig.savefig(OUT / "identifiability_phi_c.png", dpi=200)
    plt.close(fig)


# ------------------------------------------- identifiability: one, two and three tests
SIGMAS = [100.0, 200.0, 300.0, 400.0]   # confining pressures of the tests [kPa]


def make_more_tests(n_max=4, fname="identifiability_more_tests.png", fig_w=17.6, h_map=3.3):
    """phi-c RMSE maps (E_i fixed at the true value, same colour scale as the one-test map)
    for 1 to 4 tests (sigma3 = 100, 200, ... kPa), plus the fit of all three parameters to the same data."""
    q_meas = [Q_MEAS] + [add_noise(forward_model(THETA_TRUE, STRAIN, sigma3=sg), 0.01, seed=42 + i)
                         for i, sg in enumerate(SIGMAS[1:], 1)]
    ph = np.linspace(20, 40, 160); c = np.linspace(0, 30, 160)
    P, C = np.meshgrid(ph, c); phr = np.radians(P)

    def sq_err(sg, qm):
        qf = (2 * C * np.cos(phr) + 2 * sg * np.sin(phr)) / (1 - np.sin(phr))
        q = STRAIN[None, None, :] / (1 / THETA_TRUE[0] + STRAIN[None, None, :] / (qf[..., None] / 0.9))
        return np.mean((q - qm) ** 2, axis=-1)

    lo, hi = zip(*BOUNDS)
    results, maps, acc = [], [], 0
    for n in range(1, len(SIGMAS) + 1):
        acc = acc + sq_err(SIGMAS[n - 1], q_meas[n - 1])
        maps.append(np.sqrt(acc / n))
        res = lambda t: np.concatenate([forward_model(t, STRAIN, sigma3=SIGMAS[k]) - q_meas[k]
                                        for k in range(n)])
        results.append(least_squares(res, START, bounds=(lo, hi), x_scale=np.array(hi) - np.array(lo)).x)
    levels = np.geomspace(max(maps[0].min(), 1), maps[0].max(), 14)   # same as the one-test slide
    sig_txt = lambda n: (f"{SIGMAS[0]:.0f}" if n == 1 else
                         ", ".join(f"{s:.0f}" for s in SIGMAS[:n]) if n == 2 else
                         f"{SIGMAS[0]:.0f}-{SIGMAS[n - 1]:.0f}")
    titles = [f"{n} test{'s' if n > 1 else ''}: $\\sigma_3$ = {sig_txt(n)} kPa" for n in range(1, n_max + 1)]
    # Mohr circles at failure (true parameters), the true envelope and the envelope of the fit
    ph_t, c_t = np.radians(THETA_TRUE[1]), THETA_TRUE[2]
    qf_true = lambda sg: (2 * c_t * np.cos(ph_t) + 2 * sg * np.sin(ph_t)) / (1 - np.sin(ph_t))
    x_max = SIGMAS[-1] + qf_true(SIGMAS[-1]) + 20
    # Explicit layout in inches: the Mohr diagram sits directly below its map and is exactly as wide.
    y_max = qf_true(SIGMAS[-1]) / 2 * 1.08
    left, right, gap = 0.9, 1.9, 0.45
    aw = (fig_w - left - right - (n_max - 1) * gap) / n_max       # axes width [in]
    h_mohr = aw * y_max / x_max                                    # equal scaling: circles stay round
    b_mohr = 0.65
    b_map = b_mohr + h_mohr + 0.75
    fig_h = b_map + h_map + 0.5
    fig = plt.figure(figsize=(fig_w, fig_h))
    rect = lambda i, b, h: [(left + i * (aw + gap)) / fig_w, b / fig_h, aw / fig_w, h / fig_h]
    axs = [fig.add_axes(rect(i, b_map, h_map)) for i in range(n_max)]
    axm = [fig.add_axes(rect(i, b_mohr, h_mohr)) for i in range(n_max)]
    for n, (ax, am, ttl, Z, th) in enumerate(zip(axs, axm, titles, maps, results), start=1):
        cs = ax.contourf(P, C, np.clip(Z, levels[0], levels[-1]), levels=levels, cmap="Blues_r")
        ax.plot(THETA_TRUE[1], THETA_TRUE[2], "*", color="gold", mec=INK, ms=16)
        ax.plot(th[1], th[2], "o", color=INK, ms=6)
        ax.set_xlim(20, 40); ax.set_ylim(0, 30)
        ax.annotate(f"$\\varphi$ = {th[1]:.1f}$^\\circ$, $c$ = {th[2]:.1f} kPa", xy=(th[1], th[2]),
                    xytext=(0.97, 0.05), textcoords="axes fraction", ha="right", fontsize=10,
                    bbox=dict(boxstyle="round", fc="white", ec=INK, alpha=0.9))
        ax.set_xlabel("$\\varphi$ [deg]"); ax.set_title(ttl, loc="left")
        print(ttl, "fit: E_i = %.0f, phi = %.1f, c = %.1f" % tuple(th))
        # tau-sigma diagram: Mohr circles from the measured end of each test, true envelope, envelope with the fitted phi, c
        xs = np.array([0.0, x_max])
        am.plot(xs, c_t + xs * np.tan(ph_t), color=ACCENT, lw=3.0, alpha=0.5)
        am.plot(xs, th[2] + xs * np.tan(np.radians(th[1])), color=INK, lw=1.4, ls="--")
        am.text(0.03, 0.95, f"$\\varphi$ = {th[1]:.1f}$^\\circ$\n$c$ = {th[2]:.1f} kPa",
                transform=am.transAxes, va="top", fontsize=10)
        th_arc = np.linspace(0, np.pi, 100)
        for sg, qm in zip(SIGMAS[:n], q_meas[:n]):
            r = qm[-1] / 2            # measured deviator stress at the end of the test (5 % strain)
            am.plot(sg + r + r * np.cos(th_arc), r * np.sin(th_arc), color=INK, lw=1.6)
        am.set_xlim(0, x_max); am.set_ylim(0, y_max)
        am.set_xlabel("$\\sigma$ [kPa]")
        if n > 1:
            ax.tick_params(labelleft=False); am.tick_params(labelleft=False)
    axs[0].set_ylabel("$c$ [kPa]")
    axm[0].set_ylabel("$\\tau$ [kPa]")
    axs[0].plot([], [], "*", color="gold", mec=INK, ms=12, label="true value")
    axs[0].plot([], [], "o", color=INK, ms=6, label="fitted")
    axs[0].legend(loc="upper right", frameon=True, fontsize=9)
    axm[0].plot([], [], color=ACCENT, lw=3.0, alpha=0.5, label="true envelope")
    axm[0].plot([], [], color=INK, lw=1.4, ls="--", label="fitted envelope")
    axm[0].plot([], [], color=INK, lw=1.6, label="measured end of test")
    axm[0].legend(loc="lower right", frameon=True, fontsize=8)
    cax = fig.add_axes([(fig_w - right + 0.55) / fig_w, b_map / fig_h, 0.25 / fig_w, h_map / fig_h])
    fig.colorbar(cs, cax=cax, label="RMSE [kPa]")
    fig.savefig(OUT / fname, dpi=200, bbox_inches="tight"); plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    make_model_and_data()
    print("rmse frames:", make_rmse())
    print("optimizer frames:", make_optimizer())
    make_identifiability()
    make_sections()
    make_more_tests(2, "identifiability_two_tests.png", fig_w=12.0, h_map=2.7)
    make_more_tests()


if __name__ == "__main__":
    main()
