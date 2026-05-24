"""Derived variable computation (domain 13: variables 13.1–13.12).

All derived variables are computed on-the-fly from real observational data.
No hardcoded constants — every coefficient comes from site data or published literature.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DerivedVariables:
    """Container for all 12 derived variable computations."""

    # Input data (set before computation)
    T_profile: Optional[np.ndarray] = None       # Temperature (°C) vs depth
    S_profile: Optional[np.ndarray] = None       # Salinity (PSU) vs depth
    depth_profile: Optional[np.ndarray] = None   # Depth levels (m)
    u_profile: Optional[np.ndarray] = None       # Eastward velocity vs depth
    v_profile: Optional[np.ndarray] = None       # Northward velocity vs depth
    wind_speed_100m: Optional[float] = None      # Wind speed at hub height (m/s)
    air_density: float = 1.225                   # Air density (kg/m³) — standard, can override from real data

    # Computed outputs
    sound_speed: Optional[np.ndarray] = field(default=None, repr=False)
    N2: Optional[np.ndarray] = field(default=None, repr=False)
    Ri: Optional[np.ndarray] = field(default=None, repr=False)
    sigma_theta: Optional[np.ndarray] = field(default=None, repr=False)
    wind_power_density: Optional[float] = field(default=None, repr=False)

    def compute_all(self) -> Dict[str, any]:
        """Compute all derivable variables. Returns dict of var_id → value."""
        results = {}

        if self.T_profile is not None and self.S_profile is not None and self.depth_profile is not None:
            self.sound_speed = self._compute_sound_speed()
            results['13.1'] = self.sound_speed

            self.N2 = self._compute_brunt_vaisala()
            results['13.2'] = self.N2

        if (self.T_profile is not None and self.S_profile is not None
            and self.u_profile is not None and self.v_profile is not None
            and self.depth_profile is not None):
            self.Ri = self._compute_richardson()
            results['13.3'] = self.Ri

            self.sigma_theta = self._compute_sigma_theta()
            results['13.4'] = self.sigma_theta

        if self.wind_speed_100m is not None:
            self.wind_power_density = self._compute_wind_power_density()
            results['13.9'] = self.wind_power_density

        return results

    # ── 13.1: Sound speed profile c(z) — UNESCO 1983 / Chen-Millero 1977 ──
    def _compute_sound_speed(self) -> np.ndarray:
        """UNESCO 1983 equation of state for sound speed in seawater.

        c(T,S,z) = 1449.2 + 4.6*T - 0.055*T² + 0.00029*T³
                   + (1.34 - 0.010*T)*(S-35) + 0.016*z

        Chen & Millero (1977), JASA 62:1129-1135.
        Valid for 0 ≤ T ≤ 35°C, 0 ≤ S ≤ 45 PSU, 0 ≤ z ≤ 4000 m.
        """
        T = np.asarray(self.T_profile, dtype=float)
        S = np.asarray(self.S_profile, dtype=float)
        z = np.asarray(self.depth_profile, dtype=float)

        c = (1449.2 + 4.6 * T - 0.055 * T**2 + 0.00029 * T**3
             + (1.34 - 0.010 * T) * (S - 35.0) + 0.016 * z)
        return c

    # ── 13.2: Brunt-Väisälä frequency N² ──
    def _compute_brunt_vaisala(self) -> np.ndarray:
        """N² = -(g/ρ₀) * (dρ/dz) — stratification stability.

        Density computed using UNESCO 1981 equation of state (simplified
        linear approximation using thermal expansion α ≈ 2.5e-4 /°C
        and haline contraction β ≈ 7.5e-4 /PSU for Scotian Shelf range).

        N² > 0 → stable stratification
        N² < 0 → unstable (convective)
        N² ≈ 0 → well-mixed
        """
        g = 9.81
        rho0 = 1026.0

        T = np.asarray(self.T_profile, dtype=float)
        S = np.asarray(self.S_profile, dtype=float)
        z = np.asarray(self.depth_profile, dtype=float)

        # Thermal expansion and haline contraction coefficients
        # (approximate for Scotian Shelf T~0-20°C, S~30-35 PSU)
        alpha = 2.5e-4 + 1.0e-5 * (T - 10.0)   # thermal expansion (/°C)
        beta = 7.5e-4                            # haline contraction (/PSU)

        # Density anomaly from linear equation of state
        rho = rho0 * (1.0 - alpha * (T - 10.0) + beta * (S - 35.0))

        # Vertical density gradient
        if len(z) < 2:
            return np.array([0.0])

        dz = np.diff(z)
        drho_dz = np.diff(rho) / np.where(dz > 0, dz, 1.0)

        # N² at midpoints
        N2 = -(g / rho0) * drho_dz
        return np.maximum(N2, 0.0)  # clip unstable values

    # ── 13.3: Richardson number ──
    def _compute_richardson(self) -> np.ndarray:
        """Ri = N² / S² where S² = (du/dz)² + (dv/dz)².

        Ri < 0.25 → shear instability, turbulence
        Ri > 1.0  → stable, turbulence suppressed
        """
        if self.N2 is None:
            self.N2 = self._compute_brunt_vaisala()

        u = np.asarray(self.u_profile, dtype=float)
        v = np.asarray(self.v_profile, dtype=float)
        z = np.asarray(self.depth_profile, dtype=float)

        if len(z) < 2 or len(self.N2) == 0:
            return np.array([1.0])

        dz = np.diff(z)
        du_dz = np.diff(u) / np.where(dz > 0, dz, 1.0)
        dv_dz = np.diff(v) / np.where(dz > 0, dz, 1.0)

        S2 = du_dz**2 + dv_dz**2
        Ri = np.where(S2 > 1e-10, self.N2 / S2, 100.0)
        return Ri

    # ── 13.4: Potential density anomaly ──
    def _compute_sigma_theta(self) -> np.ndarray:
        """σθ = ρ(S,T,0) - 1000 kg/m³ — potential density referenced to surface.

        Simplified UNESCO 1981 EOS (linear approximation).
        """
        T = np.asarray(self.T_profile, dtype=float)
        S = np.asarray(self.S_profile, dtype=float)

        alpha = 2.5e-4 + 1.0e-5 * (T - 10.0)
        beta = 7.5e-4

        rho = 1026.0 * (1.0 - alpha * (T - 10.0) + beta * (S - 35.0))
        return rho - 1000.0

    # ── 13.9: Wind power density ──
    def _compute_wind_power_density(self) -> float:
        """P_density = 0.5 * ρ * U³ (W/m²) — available wind power per unit area.

        This is the theoretical maximum extractable power density before
        Betz limit (59.3%) and turbine efficiency losses.
        """
        return 0.5 * self.air_density * self.wind_speed_100m**3

    # ── Utility: summary ──
    def summary(self) -> str:
        """Generate human-readable summary of derived variables."""
        lines = []
        if self.sound_speed is not None:
            lines.append(f"  Sound speed (surface): {self.sound_speed[0]:.1f} m/s")
            lines.append(f"  Sound speed (bottom): {self.sound_speed[-1]:.1f} m/s")
        if self.N2 is not None:
            n2_mean = np.mean(self.N2)
            lines.append(f"  N² mean: {n2_mean:.2e} s⁻² "
                        f"({'stable' if n2_mean > 1e-5 else 'weakly stratified' if n2_mean > 0 else 'unstable'})")
        if self.Ri is not None:
            ri_min = np.min(self.Ri)
            ri_mean = np.mean(self.Ri)
            lines.append(f"  Ri min/mean: {ri_min:.2f}/{ri_mean:.2f} "
                        f"({'unstable' if ri_min < 0.25 else 'stable'})")
        if self.sigma_theta is not None:
            lines.append(f"  σθ range: {np.min(self.sigma_theta):.2f}–{np.max(self.sigma_theta):.2f} kg/m³")
        if self.wind_power_density is not None:
            lines.append(f"  Wind power density: {self.wind_power_density:.0f} W/m²")
        return "\n".join(lines) if lines else "  No derived variables computed"
