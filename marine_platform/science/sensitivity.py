"""
Sensitivity Analysis for the Marine Digital Twin Platform.

Implements two complementary global sensitivity analysis methods:

1. **Sobol' Indices (Variance-Based)**
   - First-order: S_i = V(E(Y|X_i)) / V(Y)
     The fraction of output variance explained by variable i alone (main effect).
   - Total-effect: S_Ti = 1 - V(E(Y|X_{-i})) / V(Y)
     Includes all interactions involving variable i.
   - Uses Saltelli's efficient Monte Carlo estimator (Saltelli et al. 2010).

2. **Morris Method (Screening)**
   - mu*: Mean absolute elementary effect — measures overall importance.
   - sigma: Standard deviation of elementary effects — measures nonlinearity/interactions.
   - Efficient for screening many input variables before detailed Sobol' analysis.

Input Variables Analyzed
------------------------
The variables to analyze depend on the module:
- Lagrangian: wind speed, current velocity, diffusivity Kz, release depth, time
- Wake: hub-height wind speed, surface roughness z0, turbine Ct
- Noise: source level, T profile, S profile, depth, pH
- Species: occurrence probability, detection threshold, noise level

References
----------
- Sobol, I. M. (2001). "Global sensitivity indices for nonlinear mathematical
  models and their Monte Carlo estimates." Math. Comput. Simul., 55(1-3), 271-280.
- Saltelli, A., et al. (2010). "Variance based sensitivity analysis of model
  output. Design and estimator for the total sensitivity index."
  Comput. Phys. Commun., 181(2), 259-270.
- Morris, M. D. (1991). "Factorial sampling plans for preliminary computational
  experiments." Technometrics, 33(2), 161-174.
- Campolongo, F., et al. (2007). "An effective screening design for sensitivity
  analysis of large models." Environ. Model. Softw., 22(10), 1509-1518.
"""

import numpy as np
from numpy.random import default_rng
from scipy import stats
from typing import Tuple, Optional, List, Dict, Callable, Union
from dataclasses import dataclass, field
import warnings


# ── Parameter Space ───────────────────────────────────────────────────────────


@dataclass
class ParameterSpec:
    """Specification for a single input parameter."""
    name: str
    lower: float
    upper: float
    distribution: str = "uniform"  # "uniform", "normal", "lognormal"
    # Distribution parameters
    mu: Optional[float] = None     # mean (for normal/lognormal)
    sigma: Optional[float] = None  # std (for normal/lognormal)
    unit: str = ""

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        """Generate n random samples from the parameter distribution."""
        if self.distribution == "uniform":
            return rng.uniform(self.lower, self.upper, n)
        elif self.distribution == "normal":
            # Truncate to bounds
            samples = rng.normal(self.mu, self.sigma, n)
            return np.clip(samples, self.lower, self.upper)
        elif self.distribution == "lognormal":
            mu_log = np.log(self.mu**2 / np.sqrt(self.mu**2 + self.sigma**2)) if self.mu else 0
            sigma_log = np.sqrt(np.log(1 + self.sigma**2 / self.mu**2)) if self.sigma else 1
            samples = rng.lognormal(mu_log, sigma_log, n)
            return np.clip(samples, self.lower, self.upper)
        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")


class ParameterSpace:
    """
    Manages the input parameter space for sensitivity analysis.

    Maps parameter names to their ranges, distributions, and sampling methods.
    """

    def __init__(self):
        self.params: Dict[str, ParameterSpec] = {}

    def add(
        self,
        name: str,
        lower: float,
        upper: float,
        distribution: str = "uniform",
        mu: Optional[float] = None,
        sigma: Optional[float] = None,
        unit: str = "",
    ):
        """Add a parameter to the space."""
        self.params[name] = ParameterSpec(
            name=name, lower=lower, upper=upper,
            distribution=distribution, mu=mu, sigma=sigma, unit=unit
        )

    def add_normal(self, name: str, mu: float, sigma: float, unit: str = ""):
        """Add a normally-distributed parameter (truncated at mu +/- 4*sigma)."""
        self.add(name, lower=mu - 4*sigma, upper=mu + 4*sigma,
                 distribution="normal", mu=mu, sigma=sigma, unit=unit)

    def add_lognormal(self, name: str, mu: float, sigma: float, unit: str = ""):
        """Add a lognormally-distributed parameter."""
        upper = mu * np.exp(3 * sigma / mu) if mu > 0 else 10
        self.add(name, lower=0.0, upper=upper,
                 distribution="lognormal", mu=mu, sigma=sigma, unit=unit)

    def sample(self, n: int, rng: Optional[np.random.Generator] = None) -> Dict[str, np.ndarray]:
        """Generate n samples for all parameters."""
        rng = rng if rng is not None else default_rng()
        return {name: spec.sample(n, rng) for name, spec in self.params.items()}

    @property
    def n_params(self) -> int:
        return len(self.params)

    @property
    def names(self) -> List[str]:
        return list(self.params.keys())

    @property
    def bounds(self) -> np.ndarray:
        """(n_params, 2) array of [lower, upper] bounds."""
        return np.array([[p.lower, p.upper] for p in self.params.values()])


# ── Sobol' Sensitivity Analysis ───────────────────────────────────────────────


class SobolAnalyzer:
    """
    Sobol' variance-based global sensitivity analysis.

    Decomposes the output variance of a model Y = f(X_1, ..., X_k) into
    contributions from each input variable and their interactions.

    First-order index S_i:
        S_i = V(E(Y|X_i)) / V(Y)

        The fraction of total output variance that would be eliminated if
        X_i were fixed to its true value. Measures the MAIN EFFECT of X_i.

    Total-effect index S_Ti:
        S_Ti = 1 - V(E(Y|X_{-i})) / V(Y)
             = E(V(Y|X_{-i})) / V(Y)

        The fraction of variance that remains when all variables EXCEPT X_i
        are fixed. Includes all interactions involving X_i. If S_Ti ~= 0,
        X_i is non-influential and can be fixed anywhere in its range.

    Estimator (Saltelli et al. 2010):
        Uses two independent sample matrices A and B (N x k), and k matrices
        A_B^{(i)} where column i comes from B and all others from A.

        V(E(Y|X_i)) = (1/N) * sum_{j=1}^N f(A)_j * f(A_B^{(i)})_j - f0^2
        V(Y) = (1/N) * sum_{j=1}^N f(A)_j^2 - f0^2

        where f0 = (1/N) * sum f(A)_j

    Computational cost: N * (k + 2) model evaluations, where N is the
    base sample size (typically 1000-10000) and k is the number of parameters.

    IMPORTANT: For the windmill platform, this is computationally expensive
    if the model is a full simulation. For Lagrangian tracking or acoustic
    propagation, consider using a surrogate model (Gaussian process emulator)
    for the Sobol' analysis.
    """

    def __init__(
        self,
        model_fn: Callable[[np.ndarray], np.ndarray],
        param_space: ParameterSpace,
        rng: Optional[np.random.Generator] = None,
    ):
        """
        Args:
            model_fn: Function that takes (N, k) array and returns (N,) array.
                     This is the simulation to analyze.
            param_space: ParameterSpace defining input parameters
            rng: Random number generator (reproducibility)
        """
        self.model_fn = model_fn
        self.param_space = param_space
        self.rng = rng if rng is not None else default_rng()
        self.k = param_space.n_params
        self.names = param_space.names

        # Results storage
        self.S1: Optional[np.ndarray] = None  # First-order indices
        self.ST: Optional[np.ndarray] = None  # Total-effect indices
        self.S2: Optional[np.ndarray] = None  # Second-order indices (optional)
        self.confidence: Optional[Dict] = None

    def analyze(
        self,
        N: int = 1000,
        calc_second_order: bool = False,
        confidence_level: float = 0.95,
        seed: Optional[int] = None,
        verbose: bool = False,
    ) -> Dict:
        """
        Compute Sobol' sensitivity indices.

        Args:
            N: Base sample size. Total evaluations = N * (k + 2).
               For k=5 params: N=1000 -> 7,000 evaluations.
               Start with N=500 for screening, N=2000+ for publication.
            calc_second_order: If True, compute S_ij (k*(k-1)/2 extra evaluations)
            confidence_level: For bootstrap confidence intervals (default 0.95)
            seed: Random seed for reproducibility
            verbose: Print progress

        Returns:
            Dict with S1, ST, confidence intervals, and summary table.
        """
        if seed is not None:
            self.rng = default_rng(seed)

        k = self.k
        bounds = self.param_space.bounds  # (k, 2)

        if verbose:
            print(f"Generating Sobol' samples: N={N}, k={k}")
            print(f"Total model evaluations: {N * (k + 2)}")

        # Generate sample matrices A and B in [0,1]^k
        A = self.rng.uniform(0, 1, (N, k))
        B = self.rng.uniform(0, 1, (N, k))

        # Scale to parameter ranges
        A_scaled = self._scale_samples(A)
        B_scaled = self._scale_samples(B)

        # Evaluate model at A and B
        if verbose:
            print("Evaluating f(A)...")
        fA = self.model_fn(A_scaled)

        if verbose:
            print("Evaluating f(B)...")
        fB = self.model_fn(B_scaled)

        # Total variance estimate
        f0_sq = np.mean(fA)**2
        Vy = np.mean(fA**2) - f0_sq

        if Vy < 1e-15:
            warnings.warn("Model output has negligible variance. Check model function.")
            return {
                "S1": np.zeros(k),
                "ST": np.zeros(k),
                "Vy": Vy,
                "warning": "Zero output variance",
            }

        # Compute first-order and total-effect indices
        S1 = np.zeros(k)
        ST = np.zeros(k)

        for i in range(k):
            if verbose and k > 5:
                print(f"  Parameter {i+1}/{k}: {self.names[i]}")

            # Build C_i: A with column i from B
            C_i = A.copy()
            C_i[:, i] = B[:, i]
            C_i_scaled = self._scale_samples(C_i)

            fC = self.model_fn(C_i_scaled)

            # First-order estimator (Saltelli 2010, Eq. 20)
            S1[i] = (np.mean(fB * fC) - f0_sq) / Vy

            # Total-effect estimator (Saltelli 2010, Eq. 21)
            ST[i] = 1.0 - (np.mean(fA * fC) - f0_sq) / Vy

        # Clamp to [0, 1]
        S1 = np.clip(S1, 0, 1)
        ST = np.clip(ST, 0, 1)

        # Enforce S1_i <= ST_i (theoretically required)
        ST = np.maximum(ST, S1)

        self.S1 = S1
        self.ST = ST

        # Bootstrap confidence intervals
        ci_s1 = np.zeros((k, 2))
        ci_st = np.zeros((k, 2))

        n_bootstrap = 500
        for i in range(k):
            bs_s1 = np.zeros(n_bootstrap)
            bs_st = np.zeros(n_bootstrap)
            for b in range(n_bootstrap):
                idx = self.rng.choice(N, size=N, replace=True)
                bs_s1[b] = np.mean(fB[idx] * fC[idx]) - np.mean(fA[idx])**2
                bs_st[b] = 1.0 - (np.mean(fA[idx] * fC[idx]) - np.mean(fA[idx])**2)
            bs_s1 /= Vy
            bs_st /= Vy
            bs_s1 = np.clip(bs_s1, 0, 1)
            bs_st = np.clip(bs_st, 0, 1)

            alpha = (1 - confidence_level) / 2
            ci_s1[i] = np.percentile(bs_s1, [100*alpha, 100*(1-alpha)])
            ci_st[i] = np.percentile(bs_st, [100*alpha, 100*(1-alpha)])

        self.confidence = {
            "S1_ci": ci_s1,
            "ST_ci": ci_st,
            "confidence_level": confidence_level,
        }

        # Second-order indices (optional, computationally expensive)
        if calc_second_order and k > 1:
            S2 = np.zeros((k, k))
            for i in range(k):
                for j in range(i+1, k):
                    # Build D_ij: A with columns i,j from B
                    D_ij = A.copy()
                    D_ij[:, i] = B[:, i]
                    D_ij[:, j] = B[:, j]
                    D_ij_scaled = self._scale_samples(D_ij)
                    fD = self.model_fn(D_ij_scaled)

                    # V_ij = E(f(A) * f(D_ij)) - f0^2
                    V_ij = np.mean(fA * fD) - f0_sq
                    # S_ij = (V_ij - V_i - V_j) / V(Y)
                    V_i = S1[i] * Vy
                    V_j = S1[j] * Vy
                    S2[i, j] = (V_ij - V_i - V_j) / Vy
                    S2[j, i] = S2[i, j]
            self.S2 = S2

        return {
            "S1": S1,
            "ST": ST,
            "Vy": Vy,
            "S1_ci": ci_s1,
            "ST_ci": ci_st,
            "parameter_names": self.names,
            "N_evaluations": N * (k + 2),
        }

    def _scale_samples(self, U: np.ndarray) -> np.ndarray:
        """Scale [0,1] samples to parameter ranges."""
        bounds = self.param_space.bounds  # (k, 2)
        scaled = np.zeros_like(U)
        for i in range(self.k):
            scaled[:, i] = bounds[i, 0] + U[:, i] * (bounds[i, 1] - bounds[i, 0])
        return scaled

    def summary(self) -> str:
        """Text summary of Sobol' analysis results."""
        if self.S1 is None or self.ST is None:
            return "Sobol' analysis not yet computed. Call analyze() first."

        # Rank by total-effect index
        order = np.argsort(-self.ST)

        lines = [
            "Sobol' Variance-Based Sensitivity Analysis",
            "=" * 70,
            f"{'Parameter':25s} {'S1':>8s} {'ST':>8s} {'S1 CI':>18s} {'ST CI':>18s}",
            "-" * 70,
        ]

        ci_s1 = self.confidence["S1_ci"] if self.confidence else np.zeros((self.k, 2))
        ci_st = self.confidence["ST_ci"] if self.confidence else np.zeros((self.k, 2))

        for idx in order:
            name = self.names[idx][:24]
            s1_str = f"{self.S1[idx]:.4f}" if self.S1[idx] > 0.001 else "<0.001"
            st_str = f"{self.ST[idx]:.4f}" if self.ST[idx] > 0.001 else "<0.001"
            s1_ci = f"[{ci_s1[idx,0]:.3f}, {ci_s1[idx,1]:.3f}]"
            st_ci = f"[{ci_st[idx,0]:.3f}, {ci_st[idx,1]:.3f}]"
            lines.append(f"{name:25s} {s1_str:>8s} {st_str:>8s} {s1_ci:>18s} {st_ci:>18s}")

        lines.append("-" * 70)

        # Interpretation
        lines.append("\nInterpretation:")
        lines.append(f"  Total output variance: {np.mean(self.ST):.4f}")

        dominant = np.argmax(self.ST)
        lines.append(f"  Most influential: {self.names[dominant]} (ST = {self.ST[dominant]:.4f})")

        # Check for interactions
        for i in range(self.k):
            if self.ST[i] - self.S1[i] > 0.1:
                lines.append(
                    f"  Interaction detected: {self.names[i]} "
                    f"(ST - S1 = {self.ST[i] - self.S1[i]:.3f})"
                )

        # Non-influential parameters
        non_inf = [self.names[i] for i in range(self.k) if self.ST[i] < 0.01]
        if non_inf:
            lines.append(f"  Non-influential (ST < 0.01): {', '.join(non_inf)}")

        return "\n".join(lines)


# ── Morris Sensitivity Analysis ───────────────────────────────────────────────


class MorrisAnalyzer:
    """
    Morris method for factor screening.

    Computes elementary effects (EE) for each input parameter:

        EE_i = [f(X + Delta_i) - f(X)] / Delta_i

    where Delta_i is a step in the i-th input direction.

    Statistics:
    - mu*: Mean of absolute elementary effects
           Measures overall importance (sensitivity magnitude)
    - sigma: Standard deviation of EE
             Measures nonlinearity and interaction effects
    - mu: Mean (signed) elementary effects for direction

    Interpretation:
    - High mu*, low sigma: Linear, additive effect
    - High mu*, high sigma: Nonlinear or interactive effect
    - Low mu*, low sigma: Non-influential parameter
    - Low mu*, high sigma: Nonlinearities but low overall effect

    The Morris method is much cheaper than Sobol' — it requires only
    r * (k + 1) evaluations, where r is the number of trajectories
    (typically 10-50) and k is the number of parameters.

    For k=10, r=20: 220 evaluations vs Sobol' N=1000 -> 12,000 evaluations.
    Use Morris for initial screening, Sobol' for final quantification.
    """

    def __init__(
        self,
        model_fn: Callable[[np.ndarray], np.ndarray],
        param_space: ParameterSpace,
        rng: Optional[np.random.Generator] = None,
    ):
        """
        Args:
            model_fn: Function (N, k) -> (N,) array
            param_space: ParameterSpace
            rng: Random generator
        """
        self.model_fn = model_fn
        self.param_space = param_space
        self.rng = rng if rng is not None else default_rng()
        self.k = param_space.n_params
        self.names = param_space.names

        self.mu_star: Optional[np.ndarray] = None
        self.sigma: Optional[np.ndarray] = None
        self.mu: Optional[np.ndarray] = None

    def analyze(
        self,
        n_trajectories: int = 20,
        n_levels: int = 4,
        seed: Optional[int] = None,
        verbose: bool = False,
    ) -> Dict:
        """
        Compute Morris elementary effects.

        Args:
            n_trajectories: Number of radial trajectories (10-50 recommended).
                           More trajectories = more reliable ranking.
            n_levels: Number of grid levels (typically 4 or 6).
                     Delta = n_levels / (2*(n_levels - 1))
            seed: Random seed for reproducibility
            verbose: Print progress

        Returns:
            Dict with mu_star, sigma, mu, and interpretation.
        """
        if seed is not None:
            self.rng = default_rng(seed)

        k = self.k
        bounds = self.param_space.bounds  # (k, 2)

        # Grid step size
        Delta = n_levels / (2 * (n_levels - 1))

        # Pre-allocate
        EE = np.zeros((n_trajectories, k))

        if verbose:
            print(f"Morris screening: {n_trajectories} trajectories, {k} parameters")
            print(f"Total evaluations: {n_trajectories * (k + 1)}")

        for traj in range(n_trajectories):
            if verbose and n_trajectories > 10 and traj % 5 == 0:
                print(f"  Trajectory {traj+1}/{n_trajectories}")

            # Random starting point on the p-level grid
            X_start = self._random_grid_point(n_levels)

            # Random permutation for variable ordering
            perm = self.rng.permutation(k)

            # Previous model output
            X_prev = X_start.copy()
            X_prev_scaled = self._unscale(X_prev, n_levels)
            Y_prev = self.model_fn(X_prev_scaled.reshape(1, k))[0]

            for idx, i in enumerate(perm):
                # Step in direction i
                X_new = X_prev.copy()
                X_new[i] += Delta if self.rng.uniform() < 0.5 else -Delta
                X_new[i] = np.clip(X_new[i], 0, 1)

                X_new_scaled = self._unscale(X_new, n_levels)
                Y_new = self.model_fn(X_new_scaled.reshape(1, k))[0]

                # Elementary effect
                step = X_new[i] - X_prev[i]
                if abs(step) > 1e-15:
                    EE[traj, i] = (Y_new - Y_prev) / step
                else:
                    EE[traj, i] = 0.0

                X_prev = X_new
                Y_prev = Y_new

        # Compute statistics
        self.mu = np.mean(EE, axis=0)
        self.mu_star = np.mean(np.abs(EE), axis=0)
        self.sigma = np.std(EE, axis=0, ddof=1)

        return {
            "mu_star": self.mu_star,
            "mu": self.mu,
            "sigma": self.sigma,
            "parameter_names": self.names,
            "n_trajectories": n_trajectories,
            "n_evaluations": n_trajectories * (k + 1),
        }

    def _random_grid_point(self, n_levels: int) -> np.ndarray:
        """Generate a random point on the p-level grid in [0,1]^k."""
        levels = np.linspace(0, 1, n_levels)
        idx = self.rng.integers(0, n_levels, self.k)
        return levels[idx]

    def _unscale(self, U: np.ndarray, n_levels: int) -> np.ndarray:
        """Unscale from [0,1] grid to parameter bounds."""
        bounds = self.param_space.bounds
        scaled = np.zeros(self.k)
        for i in range(self.k):
            scaled[i] = bounds[i, 0] + U[i] * (bounds[i, 1] - bounds[i, 0])
        return scaled

    def classify_parameters(self) -> Dict[str, List[str]]:
        """
        Classify parameters based on Morris results.

        Returns:
            Dict with keys:
                "linear": Nearly linear effects (low sigma/mu_star)
                "nonlinear": Nonlinear but not strongly interactive
                "interactive": Strong interactions (high sigma/mu_star)
                "non_influential": Negligible effect
        """
        if self.mu_star is None or self.sigma is None:
            raise RuntimeError("Call analyze() first.")

        # Thresholds from Campolongo et al. (2007)
        mu_star_mean = np.mean(self.mu_star)
        sigma_mean = np.mean(self.sigma)

        linear = []
        nonlinear = []
        interactive = []
        non_inf = []

        for i in range(self.k):
            ms = self.mu_star[i]
            sig = self.sigma[i]

            if ms < 0.01 * max(mu_star_mean, 1e-10):
                non_inf.append(self.names[i])
            elif sig / max(ms, 1e-10) < 0.1:
                linear.append(self.names[i])
            elif sig / max(ms, 1e-10) < 1.0:
                nonlinear.append(self.names[i])
            else:
                interactive.append(self.names[i])

        return {
            "linear": linear,
            "nonlinear": nonlinear,
            "interactive": interactive,
            "non_influential": non_inf,
        }

    def summary(self) -> str:
        """Text summary of Morris screening results."""
        if self.mu_star is None:
            return "Morris analysis not yet computed. Call analyze() first."

        order = np.argsort(-self.mu_star)

        lines = [
            "Morris Elementary Effects Screening",
            "=" * 60,
            f"{'Parameter':25s} {'mu*':>10s} {'sigma':>10s} {'sigma/mu*':>10s}",
            "-" * 60,
        ]

        for idx in order:
            name = self.names[idx][:24]
            ratio = self.sigma[idx] / max(self.mu_star[idx], 1e-10)
            lines.append(
                f"{name:25s} {self.mu_star[idx]:10.4f} "
                f"{self.sigma[idx]:10.4f} {ratio:10.3f}"
            )

        lines.append("-" * 60)

        # Classification
        classes = self.classify_parameters()
        if classes["non_influential"]:
            lines.append(f"\nNon-influential: {', '.join(classes['non_influential'])}")
        if classes["linear"]:
            lines.append(f"Linear/additive: {', '.join(classes['linear'])}")
        if classes["nonlinear"]:
            lines.append(f"Nonlinear: {', '.join(classes['nonlinear'])}")
        if classes["interactive"]:
            lines.append(f"Interactive: {', '.join(classes['interactive'])}")

        return "\n".join(lines)


# ── Factory function for Lagrangian sensitivity analysis ──────────────────────


def setup_lagrangian_sensitivity(
    param_ranges: Optional[Dict[str, Tuple[float, float]]] = None,
) -> ParameterSpace:
    """
    Set up the parameter space for Lagrangian particle tracking sensitivity.

    Default parameter ranges are based on the Scotian Shelf environmental
    variability and published sensitivity studies.

    Args:
        param_ranges: Optional override for parameter ranges.
                     Dict of param_name -> (lower, upper).

    Returns:
        Configured ParameterSpace.
    """
    defaults = {
        "wind_speed_100m": (3.0, 25.0, "uniform"),      # m/s — cut-in to cut-out
        "current_speed": (0.01, 2.0, "uniform"),         # m/s — Scotian Shelf range
        "diffusivity_Kz": (1e-5, 1e-2, "lognormal"),    # m^2/s
        "release_depth": (0.0, 200.0, "uniform"),        # m
        "stokes_drift_factor": (0.5, 1.5, "uniform"),    # multiplier on Stokes drift
        "windage_factor": (0.0, 0.05, "uniform"),        # fraction of 10m wind
        "tidal_amplitude_factor": (0.8, 1.2, "uniform"), # multiplier on tidal amplitude
    }

    ranges = param_ranges or defaults

    space = ParameterSpace()
    for name, (lo, hi, dist) in ranges.items():
        space.add(name, lo, hi, distribution=dist)

    return space


def setup_wake_sensitivity() -> ParameterSpace:
    """
    Set up parameter space for wind wake sensitivity analysis.

    Key parameters:
    - Wind speed at hub height (drives Ct and therefore deficit)
    - Surface roughness z0 (drives wake expansion rate alpha)
    - Turbulence intensity (drives wake recovery in Gaussian model)
    - Hub height (affects alpha through z_hub/z0 ratio)
    - Rotor diameter (scales the wake geometrically)
    """
    space = ParameterSpace()
    space.add("wind_speed_hub_ms", 3.0, 25.0, unit="m/s")
    space.add("surface_roughness_z0_m", 1e-6, 1e-2, distribution="lognormal", unit="m")
    space.add("turbulence_intensity", 0.02, 0.20, unit="dimensionless")
    space.add("hub_height_m", 100.0, 200.0, unit="m")
    space.add("rotor_diameter_m", 150.0, 260.0, unit="m")
    return space


def setup_noise_sensitivity() -> ParameterSpace:
    """
    Set up parameter space for underwater noise sensitivity analysis.

    Key parameters:
    - Source level (varies by turbine model and construction method)
    - Temperature (affects sound speed and absorption)
    - Salinity (affects absorption via MgSO4 and boric acid relaxation)
    - Water depth (determines spreading regime: spherical vs cylindrical)
    - pH (affects boric acid component of absorption)
    """
    space = ParameterSpace()
    space.add("source_level_dB", 120.0, 220.0, unit="dB re 1uPa @ 1m")
    space.add("temperature_C", -2.0, 25.0, unit="deg C")
    space.add("salinity_PSU", 25.0, 36.0, unit="PSU")
    space.add("water_depth_m", 10.0, 200.0, unit="m")
    space.add("pH", 7.7, 8.3, unit="pH total scale")
    return space
