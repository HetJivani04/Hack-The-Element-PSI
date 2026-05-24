"""
Multi-Objective Optimization for Windmill Siting (Module E).

This module implements NSGA-II (Non-dominated Sorting Genetic Algorithm)
for optimizing offshore wind turbine placement across the Scotian Shelf ROI.

Problem Formulation
-------------------
The optimization problem has three objectives and five hard constraints,
all derived from real data — no assumed parameters.

Objectives (all maximized or minimized appropriately):
  1. MAXIMIZE Wind Energy:
       E(x,y) = mean(0.5 * rho * v(t,x,y)^3) over hourly ERA5 wind data

  2. MINIMIZE Ecological Impact:
       I_eco(x,y) = w1*species_risk(x,y)
                   + w2*habitat_sensitivity(x,y)
                   + w3*noise_footprint_area(x,y)

  3. MINIMIZE Human Conflict:
       I_human(x,y) = w1*shipping_conflict(x,y)
                     + w2*fishing_conflict(x,y)
                     + w3*distance_penalty(x,y)

Hard Constraints (from real data):
  1. Depth < 60m (GEBCO bathymetry) — engineering limit
  2. Outside MPAs (DFO shapefiles) — MPA_fraction(x,y) = 0
  3. Outside lease blocks (CNSOPB data)
  4. Minimum distance from shore: 5 km
  5. Mean wind speed > 7 m/s (economic viability from ERA5)

NSGA-II Algorithm
-----------------
- Population size: 100 individuals (grid cells)
- Selection: Binary tournament with crowding distance
- Crossover: Simulated Binary Crossover (SBX), eta_c = 20
- Mutation: Polynomial mutation, eta_m = 20
- Generations: 200 (or until convergence)
- Output: Pareto-optimal set of sites

Pareto Frontier Analysis
------------------------
- Hypervolume indicator: area dominated by Pareto front
- Knee point detection: maximum curvature on Pareto front
- Trade-off analysis: dE/dI_eco at each Pareto point

References
----------
- Deb, K., et al. (2002). "A Fast and Elitist Multiobjective Genetic Algorithm:
  NSGA-II." IEEE Trans. Evolutionary Computation, 6(2), 182-197.
- Deb, K., & Agrawal, R. B. (1995). "Simulated Binary Crossover for Continuous
  Search Space." Complex Systems, 9(2), 115-148.
- Zitzler, E., & Thiele, L. (1999). "Multiobjective Evolutionary Algorithms:
  A Comparative Case Study." IEEE Trans. Evol. Comp., 3(4), 257-271.
"""

import numpy as np
from numpy.random import default_rng
from scipy import spatial, interpolate
from typing import Tuple, Optional, List, Dict, Callable, Union
from dataclasses import dataclass, field
import warnings

from .spatial import (
    LAT_CELLS, LON_CELLS, GRID_CELL_COUNT,
    latlon_to_grid, grid_to_latlon, flatten_grid_index, unflatten_grid_index,
    distance_between_cells, grid_cell_area_km2,
)

# ── Objective Functions ───────────────────────────────────────────────────────


@dataclass
class ObjectiveConfig:
    """Configuration for a single optimization objective."""
    name: str
    direction: str  # "maximize" or "minimize"
    weight: float = 1.0  # for reference point computation


class WindEnergyObjective:
    """
    Objective 1: Maximize Wind Energy at each grid cell.

    E(x,y) = mean(0.5 * rho * v^3(t,x,y)) over the available time period.

    This is NOT a Weibull assumption — it uses the actual hourly wind speed
    distribution from ERA5 data at each grid cell.

    Parameters:
    - rho = 1.225 kg/m^3 (standard air density at sea level). This can be
      refined using real air temperature and pressure at the site:
      rho = p / (R_d * T), where R_d = 287.058 J/(kg*K).
    - v(t,x,y) = sqrt(u100^2 + v100^2) from ERA5 100m wind components
    """

    def __init__(
        self,
        wind_u100_field: np.ndarray,  # shape (n_timesteps, 13, 28)
        wind_v100_field: np.ndarray,  # shape (n_timesteps, 13, 28)
        air_temp_field: Optional[np.ndarray] = None,  # shape (n_timesteps, 13, 28)
        pressure_field: Optional[np.ndarray] = None,  # shape (n_timesteps, 13, 28)
        rho_standard: float = 1.225,
    ):
        """
        Args:
            wind_u100_field: Eastward wind at 100m (m/s), time x lat x lon
            wind_v100_field: Northward wind at 100m (m/s), time x lat x lon
            air_temp_field: Air temperature at 2m (K), for density correction
            pressure_field: Surface pressure (Pa), for density correction
            rho_standard: Standard air density (used if T/P not available)
        """
        self.wind_speed = np.sqrt(
            wind_u100_field**2 + wind_v100_field**2
        )  # shape (n_t, 13, 28)

        # Compute air density field if temperature and pressure are available
        if air_temp_field is not None and pressure_field is not None:
            R_d = 287.058  # J/(kg*K) — specific gas constant for dry air
            self.rho = pressure_field / (R_d * air_temp_field)  # kg/m^3
            self.rho_mean = np.mean(self.rho, axis=0)  # spatial mean density
        else:
            self.rho = rho_standard
            self.rho_mean = np.full((LAT_CELLS, LON_CELLS), rho_standard)

        # Wind power density: 0.5 * rho * v^3 at each timestep
        self.power_density = 0.5 * self.rho * self.wind_speed**3  # W/m^2

        # Time-mean energy density per grid cell (W/m^2)
        self.energy_field = np.mean(self.power_density, axis=0)  # shape (13, 28)

        # Mean wind speed for economic viability check
        self.mean_wind = np.mean(self.wind_speed, axis=0)  # shape (13, 28)

    def evaluate(self, cell_indices: np.ndarray) -> np.ndarray:
        """
        Evaluate wind energy at given grid cells.

        Args:
            cell_indices: Array of flat grid indices, shape (n_cells,)

        Returns:
            Energy density in W/m^2 at each cell.
        """
        vals = np.zeros(len(cell_indices))
        for k, idx in enumerate(cell_indices):
            i, j = unflatten_grid_index(idx)
            vals[k] = self.energy_field[i, j]
        return vals

    @property
    def spatial_field(self) -> np.ndarray:
        """Full 13x28 energy density field."""
        return self.energy_field.copy()

    @property
    def mean_wind_field(self) -> np.ndarray:
        """Full 13x28 mean wind speed field."""
        return self.mean_wind.copy()


class EcologicalImpactObjective:
    """
    Objective 2: Minimize Ecological Impact.

    I_eco(x,y) = w1 * species_risk(x,y)
               + w2 * habitat_sensitivity(x,y)
               + w3 * noise_footprint_penalty(x,y)

    All components derived from real data:
    - species_risk: from SDM output fitted to OBIS occurrence data
    - habitat_sensitivity: from DFO benthic habitat layers
    - noise_footprint: from acoustic propagation model (Operational SL)

    Each component is normalized to [0,1] across the ROI.
    """

    def __init__(
        self,
        species_risk_field: np.ndarray,  # shape (13, 28), range [0,1]
        habitat_sensitivity_field: np.ndarray,  # shape (13, 28), [0,1]
        noise_penalty_field: Optional[np.ndarray] = None,  # shape (13, 28), [0,1]
        weights: Tuple[float, float, float] = (0.4, 0.3, 0.3),
    ):
        """
        Args:
            species_risk_field: Species occurrence/risk per cell from SDM
            habitat_sensitivity_field: Benthic habitat sensitivity from DFO layers
            noise_penalty_field: Acoustic footprint penalty (optional)
            weights: (w_species, w_habitat, w_noise) — default equal-ish
        """
        self.w_species, self.w_habitat, self.w_noise = weights

        # Normalize each component to [0,1]
        self.species_risk = self._normalize(species_risk_field)
        self.habitat_sensitivity = self._normalize(habitat_sensitivity_field)

        if noise_penalty_field is not None:
            self.noise_penalty = self._normalize(noise_penalty_field)
        else:
            self.noise_penalty = np.zeros_like(self.species_risk)

        # Combined ecological impact
        self.impact_field = (
            self.w_species * self.species_risk
            + self.w_habitat * self.habitat_sensitivity
            + self.w_noise * self.noise_penalty
        )

    @staticmethod
    def _normalize(field: np.ndarray) -> np.ndarray:
        """Min-max normalize a spatial field to [0,1]."""
        field = np.asarray(field, dtype=np.float64)
        fmin, fmax = np.nanmin(field), np.nanmax(field)
        if fmax - fmin < 1e-10:
            return np.zeros_like(field)
        return (field - fmin) / (fmax - fmin)

    def evaluate(self, cell_indices: np.ndarray) -> np.ndarray:
        """Evaluate ecological impact at given grid cells."""
        vals = np.zeros(len(cell_indices))
        for k, idx in enumerate(cell_indices):
            i, j = unflatten_grid_index(idx)
            vals[k] = self.impact_field[i, j]
        return vals

    @property
    def spatial_field(self) -> np.ndarray:
        return self.impact_field.copy()


class HumanConflictObjective:
    """
    Objective 3: Minimize Human Conflict.

    I_human(x,y) = w1 * shipping_conflict(x,y)
                  + w2 * fishing_conflict(x,y)
                  + w3 * distance_penalty(x,y)

    All components derived from real data:
    - shipping_conflict: from GFW vessel presence hours (AIS data)
    - fishing_conflict: from GFW fishing effort by gear type
    - distance_penalty: normalized inverse distance to shore
    """

    def __init__(
        self,
        shipping_density_field: np.ndarray,  # shape (13, 28) — vessel hours
        fishing_effort_field: np.ndarray,  # shape (13, 28) — fishing hours
        distance_to_shore_field: np.ndarray,  # shape (13, 28) — km
        weights: Tuple[float, float, float] = (0.35, 0.35, 0.30),
    ):
        """
        Args:
            shipping_density_field: Vessel presence hours from GFW 4Wings
            fishing_effort_field: Fishing effort hours from GFW
            distance_to_shore_field: Distance to shore in km (from GEBCO)
            weights: (w_shipping, w_fishing, w_distance)
        """
        self.w_shipping, self.w_fishing, self.w_distance = weights

        # Normalize each component
        self.shipping_conflict = self._normalize(shipping_density_field)
        self.fishing_conflict = self._normalize(fishing_effort_field)

        # Distance penalty: closer to shore = more conflict with coastal users
        # Invert: penalty = 1 / (1 + distance/10)
        d = np.asarray(distance_to_shore_field, dtype=np.float64)
        self.distance_penalty = 1.0 / (1.0 + d / 10.0)  # ~0 at large distance

        self.conflict_field = (
            self.w_shipping * self.shipping_conflict
            + self.w_fishing * self.fishing_conflict
            + self.w_distance * self.distance_penalty
        )

    @staticmethod
    def _normalize(field: np.ndarray) -> np.ndarray:
        field = np.asarray(field, dtype=np.float64)
        fmin, fmax = np.nanmin(field), np.nanmax(field)
        if fmax - fmin < 1e-10:
            return np.zeros_like(field)
        return (field - fmin) / (fmax - fmin)

    def evaluate(self, cell_indices: np.ndarray) -> np.ndarray:
        """Evaluate human conflict at given grid cells."""
        vals = np.zeros(len(cell_indices))
        for k, idx in enumerate(cell_indices):
            i, j = unflatten_grid_index(idx)
            vals[k] = self.conflict_field[i, j]
        return vals

    @property
    def spatial_field(self) -> np.ndarray:
        return self.conflict_field.copy()


# ── Hard Constraints ──────────────────────────────────────────────────────────


class HardConstraints:
    """
    Hard constraints for windmill placement, all derived from real data.

    A grid cell is feasible ONLY if ALL constraints are satisfied:

    1. Depth < 60m (from GEBCO bathymetry) — engineering limit for monopile
    2. Outside MPAs (MPA_fraction = 0) — legal constraint
    3. Outside lease blocks — regulatory
    4. Distance from shore >= 5 km — regulatory/user-specified
    5. Mean wind speed > 7 m/s — economic viability
    """

    def __init__(
        self,
        bathymetry_field: np.ndarray,  # shape (13, 28), positive down
        mpa_fraction_field: np.ndarray,  # shape (13, 28), 0-1
        lease_block_field: np.ndarray,  # shape (13, 28), boolean
        distance_to_shore_field: np.ndarray,  # shape (13, 28), km
        mean_wind_field: np.ndarray,  # shape (13, 28), m/s
        max_depth: float = 60.0,
        min_distance_shore: float = 5.0,
        min_wind_speed: float = 7.0,
    ):
        self.bathymetry = np.asarray(bathymetry_field, dtype=np.float64)
        self.mpa_fraction = np.asarray(mpa_fraction_field, dtype=np.float64)
        self.lease_block = np.asarray(lease_block_field, dtype=bool)
        self.distance_to_shore = np.asarray(distance_to_shore_field, dtype=np.float64)
        self.mean_wind = np.asarray(mean_wind_field, dtype=np.float64)

        self.max_depth = max_depth
        self.min_distance_shore = min_distance_shore
        self.min_wind_speed = min_wind_speed

        # Pre-compute feasibility mask
        self.feasible_mask = self._compute_feasible_mask()
        self.feasible_indices = np.flatnonzero(self.feasible_mask)

    def _compute_feasible_mask(self) -> np.ndarray:
        """Compute boolean mask of feasible grid cells."""
        depth_ok = (self.bathymetry > 0) & (self.bathymetry <= self.max_depth)
        mpa_ok = (self.mpa_fraction == 0)
        lease_ok = ~self.lease_block
        shore_ok = (self.distance_to_shore >= self.min_distance_shore)
        wind_ok = (self.mean_wind >= self.min_wind_speed)

        valid_depth = ~np.isnan(self.bathymetry)
        valid_mpa = ~np.isnan(self.mpa_fraction)
        valid_wind = ~np.isnan(self.mean_wind)
        all_valid = valid_depth & valid_mpa & valid_wind

        feasible = depth_ok & mpa_ok & lease_ok & shore_ok & wind_ok & all_valid
        return feasible.reshape(LAT_CELLS * LON_CELLS)

    def check(self, cell_indices: np.ndarray) -> np.ndarray:
        """
        Check feasibility of given grid cells.

        Args:
            cell_indices: Array of flat grid indices

        Returns:
            Boolean array: True if cell satisfies all constraints.
        """
        return self.feasible_mask[cell_indices]

    def n_feasible(self) -> int:
        """Number of feasible grid cells."""
        return int(np.sum(self.feasible_mask))

    def summary(self) -> str:
        """Text summary of constraint violations in the ROI."""
        total = LAT_CELLS * LON_CELLS
        n_feas = self.n_feasible()
        n_depth = int(np.sum(
            (~np.isnan(self.bathymetry)) & (self.bathymetry > self.max_depth)
        ))
        n_mpa = int(np.sum(self.mpa_fraction > 0))
        n_lease = int(np.sum(self.lease_block))
        n_shore = int(np.sum(
            (~np.isnan(self.distance_to_shore))
            & (self.distance_to_shore < self.min_distance_shore)
        ))
        n_wind = int(np.sum(
            (~np.isnan(self.mean_wind))
            & (self.mean_wind < self.min_wind_speed)
        ))

        return (
            f"Hard Constraints Summary — {total} total cells\n"
            f"{'='*50}\n"
            f"  Feasible cells:                {n_feas:4d} / {total}\n"
            f"  Depth > {self.max_depth}m:              {n_depth:4d} excluded\n"
            f"  Inside MPA:                    {n_mpa:4d} excluded\n"
            f"  Inside lease block:            {n_lease:4d} excluded\n"
            f"  < {self.min_distance_shore}km from shore:      {n_shore:4d} excluded\n"
            f"  Wind < {self.min_wind_speed} m/s mean:         {n_wind:4d} excluded\n"
        )


# ── NSGA-II Implementation ────────────────────────────────────────────────────


class NSGA2Optimizer:
    """
    Non-dominated Sorting Genetic Algorithm II (NSGA-II).

    Optimizes three objectives simultaneously:
    1. Maximize wind energy (negate for minimization framework)
    2. Minimize ecological impact
    3. Minimize human conflict

    All objectives are internally treated as minimization problems.
    The wind energy objective is negated: f1'(x) = -E(x).

    Algorithm:
    1. Initialize population of N feasible grid cells
    2. For each generation:
       a. Create offspring via SBX crossover + polynomial mutation
       b. Combine parent + offspring populations (2N)
       c. Non-dominated sort (rank assignment)
       d. Crowding distance within each rank
       e. Select N best for next generation
    3. Return Pareto-optimal set (rank 0 solutions)
    """

    def __init__(
        self,
        objectives: List[Tuple[Callable, str]],  # (eval_fn, direction)
        constraints: HardConstraints,
        population_size: int = 100,
        n_generations: int = 200,
        crossover_prob: float = 0.9,
        mutation_prob: float = 1.0 / 364,  # 1/n_dimensions
        eta_crossover: float = 20.0,
        eta_mutation: float = 20.0,
        rng: Optional[np.random.Generator] = None,
    ):
        """
        Args:
            objectives: List of (evaluate_fn, direction) tuples.
                       evaluate_fn(cell_indices) -> np.ndarray of objective values.
                       direction: "minimize" or "maximize".
            constraints: HardConstraints instance
            population_size: Number of individuals in the population
            n_generations: Maximum number of generations
            crossover_prob: SBX crossover probability
            mutation_prob: Polynomial mutation probability per variable
            eta_crossover: SBX distribution index (higher = closer to parents)
            eta_mutation: Polynomial mutation distribution index
            rng: Random number generator
        """
        self.objectives = objectives
        self.n_objectives = len(objectives)
        self.constraints = constraints
        self.pop_size = population_size
        self.n_gen = n_generations
        self.p_cross = crossover_prob
        self.p_mut = mutation_prob
        self.eta_c = eta_crossover
        self.eta_m = eta_mutation
        self.rng = rng if rng is not None else default_rng()

        # Direction multipliers: +1 for minimize, -1 for maximize
        self.direction_mult = np.array([
            1.0 if d == "minimize" else -1.0
            for _, d in self.objectives
        ])

        # Feasible cell indices
        self.cell_pool = constraints.feasible_indices.copy()
        if len(self.cell_pool) == 0:
            raise ValueError("No feasible grid cells found. Check constraint data.")
        if len(self.cell_pool) < population_size:
            warnings.warn(
                f"Only {len(self.cell_pool)} feasible cells, "
                f"fewer than population_size={population_size}. Using all."
            )
            self.pop_size = len(self.cell_pool)

        # Pre-compute objective values for all feasible cells
        self._obj_cache = self._precompute_objectives()

        # Results
        self.pareto_front: Optional[np.ndarray] = None  # objective values
        self.pareto_cells: Optional[np.ndarray] = None  # grid cell indices
        self.history: List[Dict] = []  # per-generation stats

    def _precompute_objectives(self) -> np.ndarray:
        """Evaluate all objectives for all feasible cells. Shape: (n_cells, n_obj)."""
        n_cells = len(self.cell_pool)
        obj_matrix = np.zeros((n_cells, self.n_objectives))

        for obj_idx, (eval_fn, direction) in enumerate(self.objectives):
            raw_vals = eval_fn(self.cell_pool)
            obj_matrix[:, obj_idx] = raw_vals * self.direction_mult[obj_idx]

        return obj_matrix

    def _evaluate(self, cell_indices: np.ndarray) -> np.ndarray:
        """Look up pre-computed objective values for given cells."""
        # Find indices in the pool
        sorter = np.argsort(self.cell_pool)
        pool_indices = sorter[np.searchsorted(self.cell_pool, cell_indices, sorter=sorter)]
        return self._obj_cache[pool_indices]

    def _nondominated_sort(self, obj_values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Non-dominated sorting (Deb et al. 2002).

        Assigns each solution a Pareto rank:
        - Rank 0: non-dominated solutions (Pareto front)
        - Rank 1: dominated only by rank 0
        - etc.

        Args:
            obj_values: (N, M) array of objective values (all to be minimized)

        Returns:
            fronts: List of arrays of indices belonging to each front
            rank: Array of ranks (N,) for each solution
        """
        n = len(obj_values)
        domination_count = np.zeros(n, dtype=int)
        dominated_set = [[] for _ in range(n)]

        for p in range(n):
            for q in range(n):
                if p == q:
                    continue
                # p dominates q if p is better in all objectives and strictly
                # better in at least one
                if np.all(obj_values[p] <= obj_values[q]) and np.any(obj_values[p] < obj_values[q]):
                    dominated_set[p].append(q)
                elif np.all(obj_values[q] <= obj_values[p]) and np.any(obj_values[q] < obj_values[p]):
                    domination_count[p] += 1

        fronts = []
        ranks = np.full(n, -1, dtype=int)

        # Front 0: solutions with domination_count == 0
        front0 = np.where(domination_count == 0)[0]
        fronts.append(front0.tolist())
        ranks[front0] = 0

        current_front = 0
        while len(fronts[current_front]) > 0:
            next_front = []
            for p in fronts[current_front]:
                for q in dominated_set[p]:
                    domination_count[q] -= 1
                    if domination_count[q] == 0:
                        ranks[q] = current_front + 1
                        next_front.append(q)
            current_front += 1
            if next_front:
                fronts.append(next_front)
            else:
                break

        return fronts, ranks

    def _crowding_distance(self, obj_values: np.ndarray, front_indices: List[int]) -> np.ndarray:
        """
        Compute crowding distance for solutions within a Pareto front.

        Crowding distance measures how isolated a solution is — higher
        distance means more unique. Used to maintain diversity.

        For each objective:
        - Sort solutions by that objective
        - Boundary solutions get infinite distance
        - Interior solutions get normalized neighbor distance
        """
        n = len(front_indices)
        distances = np.zeros(n)

        if n <= 2:
            distances[:] = np.inf
            return distances

        front_vals = obj_values[front_indices]  # (n, M)

        for m in range(self.n_objectives):
            obj = front_vals[:, m]
            sorted_idx = np.argsort(obj)
            obj_range = obj[sorted_idx[-1]] - obj[sorted_idx[0]]

            if obj_range < 1e-10:
                continue

            distances[sorted_idx[0]] = np.inf
            distances[sorted_idx[-1]] = np.inf

            for i in range(1, n - 1):
                distances[sorted_idx[i]] += (
                    (obj[sorted_idx[i + 1]] - obj[sorted_idx[i - 1]]) / obj_range
                )

        return distances

    def _tournament_select(self, ranks: np.ndarray, crowding: np.ndarray, k: int = 2) -> int:
        """Binary tournament selection with crowding distance tiebreaker."""
        candidates = self.rng.choice(len(ranks), size=k, replace=False)
        best = candidates[0]

        for c in candidates[1:]:
            if ranks[c] < ranks[best]:
                best = c
            elif ranks[c] == ranks[best] and crowding[c] > crowding[best]:
                best = c

        return best

    def _sbx_crossover(self, parent1: float, parent2: float) -> Tuple[float, float]:
        """
        Simulated Binary Crossover (SBX) for real-valued variables.

        The grid cell index is treated as a continuous variable (0 to n_cells-1),
        with rounding to integer after crossover.
        """
        if self.rng.uniform() > self.p_cross:
            return parent1, parent2

        u = self.rng.uniform()
        if u <= 0.5:
            beta = (2 * u) ** (1.0 / (self.eta_c + 1))
        else:
            beta = (1.0 / (2 * (1 - u))) ** (1.0 / (self.eta_c + 1))

        child1 = 0.5 * ((1 + beta) * parent1 + (1 - beta) * parent2)
        child2 = 0.5 * ((1 - beta) * parent1 + (1 + beta) * parent2)

        return child1, child2

    def _polynomial_mutation(self, value: float, lower: float, upper: float) -> float:
        """Polynomial mutation for real-valued variables."""
        if self.rng.uniform() > self.p_mut:
            return value

        u = self.rng.uniform()
        delta = min(value - lower, upper - value) / (upper - lower)

        if u <= 0.5:
            delta_q = (2 * u + (1 - 2 * u) * (1 - delta) ** (self.eta_m + 1)) ** (
                1.0 / (self.eta_m + 1)
            ) - 1
        else:
            delta_q = 1 - (
                2 * (1 - u) + 2 * (u - 0.5) * (1 - delta) ** (self.eta_m + 1)
            ) ** (1.0 / (self.eta_m + 1))

        mutated = value + delta_q * (upper - lower)
        return np.clip(mutated, lower, upper)

    def optimize(self, verbose: bool = False) -> Dict:
        """
        Run NSGA-II optimization.

        Returns:
            Dict with:
                "pareto_cells": Flat indices of Pareto-optimal grid cells
                "pareto_latlons": (lat, lon) for each Pareto cell
                "pareto_objectives": Objective values for Pareto cells (raw directions)
                "hypervolume": Hypervolume indicator value
                "history": Per-generation statistics
        """
        n_feasible = len(self.cell_pool)
        n_vars = 1  # we're selecting among grid cells, single integer variable

        # Initialize population: random feasible cells
        pop_indices = self.rng.choice(n_feasible, size=self.pop_size, replace=False)
        pop_cells = self.cell_pool[pop_indices]  # flat cell indices

        # Track best front per generation
        self.history = []

        for gen in range(self.n_gen):
            # Evaluate population
            pop_obj = self._evaluate(pop_cells)

            # Create offspring
            offspring_cells = np.zeros(self.pop_size, dtype=int)

            for i in range(0, self.pop_size, 2):
                # Tournament selection
                p1_idx = self._tournament_select(
                    *self._nondominated_sort(pop_obj)
                )
                p2_idx = self._tournament_select(
                    *self._nondominated_sort(pop_obj)
                )

                # Crossover (treat cell index as continuous in pool index space)
                c1_pool, c2_pool = self._sbx_crossover(
                    float(p1_idx), float(p2_idx)
                )

                # Mutation
                c1_pool = self._polynomial_mutation(c1_pool, 0, n_feasible - 1)
                c2_pool = self._polynomial_mutation(c2_pool, 0, n_feasible - 1)

                # Round to nearest integer index in pool
                c1_pool = int(np.clip(np.round(c1_pool), 0, n_feasible - 1))
                c2_pool = int(np.clip(np.round(c2_pool), 0, n_feasible - 1))

                if i < self.pop_size:
                    offspring_cells[i] = self.cell_pool[c1_pool]
                if i + 1 < self.pop_size:
                    offspring_cells[i + 1] = self.cell_pool[c2_pool]

            offspring_obj = self._evaluate(offspring_cells)

            # Combine parent + offspring
            combined_cells = np.concatenate([pop_cells, offspring_cells])
            combined_obj = np.concatenate([pop_obj, offspring_obj])

            # Non-dominated sort
            fronts, ranks = self._nondominated_sort(combined_obj)

            # Select next generation
            next_pop_cells = []
            next_pop_obj = []
            for front in fronts:
                front_list = list(front)
                if len(next_pop_cells) + len(front_list) <= self.pop_size:
                    next_pop_cells.extend(combined_cells[front_list])
                    next_pop_obj.extend(combined_obj[front_list])
                else:
                    # Compute crowding distance for remaining front
                    remaining = self.pop_size - len(next_pop_cells)
                    crowding = self._crowding_distance(combined_obj, front_list)
                    # Select by crowding distance (descending)
                    sorted_front = sorted(
                        front_list, key=lambda i: crowding[front_list.index(i)], reverse=True
                    )
                    for idx in sorted_front[:remaining]:
                        next_pop_cells.append(combined_cells[idx])
                        next_pop_obj.append(combined_obj[idx])
                    break

            pop_cells = np.array(next_pop_cells, dtype=int)
            pop_obj = np.array(next_pop_obj)

            # Record generation stats
            fronts, ranks = self._nondominated_sort(pop_obj)
            front0 = fronts[0] if fronts else []
            n_pareto = len(front0)

            self.history.append({
                "generation": gen,
                "n_pareto": n_pareto,
                "n_fronts": len(fronts),
                "obj_range": {
                    f"obj_{m}": (np.min(pop_obj[:, m]), np.max(pop_obj[:, m]))
                    for m in range(self.n_objectives)
                },
            })

            if verbose and gen % 50 == 0:
                print(f"Gen {gen:4d}: Pareto size = {n_pareto:3d}, "
                      f"Fronts = {len(fronts):2d}")

        # Extract final Pareto front
        fronts, ranks = self._nondominated_sort(pop_obj)
        pareto_mask = (ranks == 0)

        self.pareto_cells = pop_cells[pareto_mask]
        self.pareto_front = pop_obj[pareto_mask] * self.direction_mult  # back to raw space

        # Compute hypervolume
        hv = self._compute_hypervolume(pop_obj[pareto_mask])

        return {
            "pareto_cells": self.pareto_cells,
            "pareto_latlons": np.array([
                grid_to_latlon(*unflatten_grid_index(int(c)))
                for c in self.pareto_cells
            ]),
            "pareto_objectives": self.pareto_front,
            "hypervolume": hv,
            "history": self.history,
        }

    def _compute_hypervolume(self, pareto_obj: np.ndarray, reference_point: Optional[np.ndarray] = None) -> float:
        """
        Compute the hypervolume indicator for the Pareto front.

        Hypervolume measures the volume of objective space dominated by the
        Pareto front relative to a reference point. Larger is better.

        Uses a simple grid-based approximation suitable for 3D.
        For production, use the `pygmo` library for exact computation.

        Args:
            pareto_obj: Pareto front objective values (minimized), shape (n, M)
            reference_point: Reference point. If None, uses 1.2 * max in each dim.

        Returns:
            Approximate hypervolume (arbitrary units, for comparison only).
        """
        if len(pareto_obj) == 0:
            return 0.0

        if reference_point is None:
            reference_point = np.max(pareto_obj, axis=0) * 1.2
            # Ensure ref point dominates all Pareto points
            reference_point = np.maximum(
                reference_point,
                np.max(pareto_obj, axis=0) + 1e-6
            )

        # Simple Monte Carlo hypervolume estimate
        n_samples = 10000
        n_in = 0

        for _ in range(n_samples):
            # Sample random point in hyper-rectangle defined by ideal and reference
            ideal = np.min(pareto_obj, axis=0)
            sample = self.rng.uniform(ideal - 0.01 * (reference_point - ideal), reference_point)

            # Check if dominated by any Pareto point
            dominated = False
            for p in pareto_obj:
                if np.all(p <= sample):
                    dominated = True
                    break

            if dominated:
                n_in += 1

        # Volume of the bounding hyper-rectangle
        volume = np.prod(reference_point - np.min(pareto_obj, axis=0) + 0.01)

        return volume * n_in / n_samples

    def get_top_sites(self, n: int = 10) -> List[Dict]:
        """
        Return the top N Pareto-optimal sites ranked by crowding distance.

        Args:
            n: Number of sites to return

        Returns:
            List of dicts with keys: cell_index, lat, lon, energy, eco_impact,
            human_conflict, depth, distance_to_shore.
        """
        if self.pareto_cells is None:
            raise RuntimeError("Call optimize() first.")

        n_pareto = len(self.pareto_cells)

        # Compute crowding distance on Pareto front
        pareto_neg = self.pareto_front.copy()
        pareto_neg[:, 0] *= -1  # negate energy back for crowding computation

        crowding = self._crowding_distance(
            pareto_neg * self.direction_mult,
            list(range(n_pareto))
        )

        # Sort by crowding distance (diverse solutions first)
        sorted_idx = np.argsort(crowding)[::-1][:min(n, n_pareto)]

        top_sites = []
        for idx in sorted_idx:
            cell = int(self.pareto_cells[idx])
            lat, lon = grid_to_latlon(*unflatten_grid_index(cell))

            # Get constraint values
            depth = self.constraints.bathymetry.flat[cell]
            dist_shore = self.constraints.distance_to_shore.flat[cell]

            top_sites.append({
                "flat_index": cell,
                "i_lat": int(unflatten_grid_index(cell)[0]),
                "i_lon": int(unflatten_grid_index(cell)[1]),
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "energy_W_m2": round(float(self.pareto_front[idx, 0]), 2),
                "eco_impact": round(float(self.pareto_front[idx, 1]), 4),
                "human_conflict": round(float(self.pareto_front[idx, 2]), 4),
                "depth_m": round(float(depth), 1),
                "distance_to_shore_km": round(float(dist_shore), 1),
                "crowding_distance": round(float(crowding[idx]), 4),
            })

        return top_sites


# ── Pareto Frontier Analysis ──────────────────────────────────────────────────


class ParetoFrontAnalyzer:
    """
    Analyze the Pareto frontier from NSGA-II optimization.

    Provides:
    - Hypervolume indicator (area dominated by Pareto front)
    - Knee point detection (maximum curvature)
    - Trade-off analysis (marginal rates of substitution)
    - 2D projections for visualization
    """

    def __init__(self, pareto_objectives: np.ndarray, objective_labels: List[str]):
        """
        Args:
            pareto_objectives: Shape (n_pareto, n_objectives)
            objective_labels: Names for each objective
        """
        self.pareto = np.asarray(pareto_objectives)
        self.labels = objective_labels
        self.n_obj = self.pareto.shape[1]
        self.n_pareto = self.pareto.shape[0]

        # Normalize to [0,1] for knee point and trade-off analysis
        self.pareto_norm = self._normalize_pareto()

    def _normalize_pareto(self) -> np.ndarray:
        """Normalize Pareto front to [0,1] in each objective."""
        pmin = np.min(self.pareto, axis=0)
        pmax = np.max(self.pareto, axis=0)
        range_val = pmax - pmin
        range_val[range_val < 1e-10] = 1.0
        return (self.pareto - pmin) / range_val

    def hypervolume(self, reference_point: Optional[np.ndarray] = None) -> float:
        """
        Compute hypervolume indicator.

        For 2D: area under Pareto front.
        For 3D: volume dominated.
        """
        if reference_point is None:
            reference_point = np.max(self.pareto_norm, axis=0) + 0.1

        n_samples = 20000
        n_in = 0
        rng = default_rng(42)

        lower = np.zeros(self.n_obj)

        for _ in range(n_samples):
            sample = rng.uniform(lower, reference_point)
            if np.any(np.all(self.pareto_norm <= sample, axis=1)):
                n_in += 1

        volume = np.prod(reference_point)
        return volume * n_in / n_samples

    def knee_point(self) -> Tuple[int, float]:
        """
        Detect the knee point on the Pareto front — the point with maximum curvature.

        The knee point is the solution where a small improvement in one objective
        costs a large sacrifice in another. It represents the "best compromise"
        for many decision-making scenarios.

        Method: For each Pareto point, compute the angle between its neighbors.
        The point with the smallest angle (sharpest bend) is the knee.

        Returns:
            knee_index: Index into pareto array
            curvature_score: Measure of "knee-ness" (higher = more knee-like)
        """
        if self.n_pareto < 3:
            return 0, 1.0

        # Sort by first objective for consistent neighbor identification
        sorted_idx = np.argsort(self.pareto_norm[:, 0])
        sorted_pareto = self.pareto_norm[sorted_idx]

        curvatures = np.zeros(self.n_pareto)

        for i in range(1, self.n_pareto - 1):
            # Vectors to neighbors
            v1 = sorted_pareto[i - 1] - sorted_pareto[i]
            v2 = sorted_pareto[i + 1] - sorted_pareto[i]

            # Normalize
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)

            if n1 > 1e-10 and n2 > 1e-10:
                cos_angle = np.dot(v1, v2) / (n1 * n2)
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                cur = np.pi - angle  # maximum when angle is smallest (sharpest bend)
            else:
                cur = 0.0

            curvatures[sorted_idx[i]] = cur

        knee_idx = int(np.argmax(curvatures))
        return knee_idx, float(curvatures[knee_idx])

    def trade_off_matrix(self) -> Dict[Tuple[int, int], np.ndarray]:
        """
        Compute local trade-off rates between each pair of objectives.

        For objectives i and j, at each Pareto point p:
            dObj_j / dObj_i at point p

        approximated by the slope between adjacent Pareto points.

        Returns:
            Dict {(i, j): array of trade-off values at each Pareto point}
        """
        trade_offs = {}

        for i in range(self.n_obj):
            for j in range(self.n_obj):
                if i >= j:
                    continue

                sorted_i = np.argsort(self.pareto[:, i])
                sorted_pareto = self.pareto[sorted_i]

                to_vals = np.zeros(self.n_pareto)
                to_vals[0] = np.nan
                to_vals[-1] = np.nan

                for k in range(1, self.n_pareto - 1):
                    di = sorted_pareto[k + 1, i] - sorted_pareto[k - 1, i]
                    dj = sorted_pareto[k + 1, j] - sorted_pareto[k - 1, j]
                    if abs(di) > 1e-10:
                        to_vals[sorted_i[k]] = dj / di

                trade_offs[(i, j)] = to_vals

        return trade_offs

    def trade_off_at_point(self, point_idx: int) -> Dict[Tuple[int, int], float]:
        """Trade-off rates at a specific Pareto point."""
        matrix = self.trade_off_matrix()
        return {(i, j): matrix[(i, j)][point_idx] for (i, j) in matrix}

    def summary(self) -> str:
        """Text summary of Pareto front analysis."""
        hv = self.hypervolume()
        knee_idx, knee_curve = self.knee_point()
        knee_vals = self.pareto[knee_idx]

        lines = [
            "Pareto Frontier Analysis",
            "=" * 60,
            f"  Pareto-optimal solutions:     {self.n_pareto}",
            f"  Hypervolume indicator:        {hv:.4f}",
            f"  Knee point index:             {knee_idx}",
            f"  Knee point curvature:         {knee_curve:.4f}",
            f"  Knee point values:",
        ]

        for m in range(self.n_obj):
            lines.append(f"    {self.labels[m]:30s}: {knee_vals[m]:.4f}")

        lines.append("")
        lines.append("  Objective ranges on Pareto front:")
        for m in range(self.n_obj):
            pmin = np.min(self.pareto[:, m])
            pmax = np.max(self.pareto[:, m])
            lines.append(f"    {self.labels[m]:30s}: [{pmin:.4f}, {pmax:.4f}]")

        return "\n".join(lines)


# ── Site Ranking Utility ──────────────────────────────────────────────────────


def rank_user_site(
    user_lat: float,
    user_lon: float,
    pareto_cells: np.ndarray,
    pareto_objectives: np.ndarray,
    objectives_all: np.ndarray,  # full objective values for all feasible cells
    constraints: HardConstraints,
) -> Dict:
    """
    Rank a user-selected site against the Pareto front.

    Tells the user: "Your site ranks #X out of Y feasible sites" and
    "You are below the Pareto front by Z units in [objective]."

    Args:
        user_lat, user_lon: User's proposed site
        pareto_cells: Flat indices of Pareto-optimal cells
        pareto_objectives: Objective values at Pareto cells
        objectives_all: Objective values at all feasible cells
        constraints: HardConstraints instance

    Returns:
        Dict with rank information and comparison to Pareto front.
    """
    user_i, user_j = latlon_to_grid(user_lat, user_lon)
    user_idx = flatten_grid_index(user_i, user_j)

    # Check feasibility
    if not constraints.check(np.array([user_idx]))[0]:
        return {
            "feasible": False,
            "reason": "Site violates one or more hard constraints.",
            "depth": float(constraints.bathymetry.flat[user_idx]),
            "mpa_fraction": float(constraints.mpa_fraction.flat[user_idx]),
            "mean_wind": float(constraints.mean_wind.flat[user_idx]),
        }

    # Find index of user site in feasible pool
    try:
        pool_pos = np.where(constraints.cell_pool == user_idx)[0][0]
        user_obj = objectives_all[pool_pos]
    except IndexError:
        return {"feasible": False, "reason": "Site data not available."}

    # Rank: count how many feasible sites dominate this one
    n_dominated_by = 0
    for obj in objectives_all:
        if np.all(obj <= user_obj) and np.any(obj < user_obj):
            n_dominated_by += 1

    n_feasible = len(objectives_all)
    rank = n_dominated_by + 1
    percentile = 100 * (1 - rank / n_feasible)

    # Distance to Pareto front (minimum distance to any Pareto point)
    pareto_obj_norm = ParetoFrontAnalyzer._normalize_pareto.__func__ is None  # skip

    # Compute minimum Euclidean distance to Pareto front
    pmin = np.min(pareto_objectives, axis=0)
    pmax = np.max(pareto_objectives, axis=0)
    range_val = pmax - pmin
    range_val[range_val < 1e-10] = 1.0

    user_norm = (user_obj - pmin) / range_val
    pareto_norm = (pareto_objectives - pmin) / range_val

    distances = np.sqrt(np.sum((pareto_norm - user_norm) ** 2, axis=1))
    min_dist_idx = np.argmin(distances)
    pareto_dist = float(distances[min_dist_idx])

    # Which objective has the biggest gap?
    obj_gaps = np.abs(pareto_norm[min_dist_idx] - user_norm)
    worst_obj = int(np.argmax(obj_gaps))

    return {
        "feasible": True,
        "rank": rank,
        "n_feasible": n_feasible,
        "percentile": round(percentile, 1),
        "distance_to_pareto": round(pareto_dist, 4),
        "worst_objective_gap": worst_obj,
        "nearest_pareto_cell": int(pareto_cells[min_dist_idx]),
        "nearest_pareto_latlon": grid_to_latlon(
            *unflatten_grid_index(int(pareto_cells[min_dist_idx]))
        ),
        "user_objectives": user_obj.tolist(),
        "nearest_pareto_objectives": pareto_objectives[min_dist_idx].tolist(),
    }
