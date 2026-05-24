# Marine Digital Twin Platform — Scientific Modeling Framework
#
# Core modules:
#   spatial   — Grid definitions, geospatial utilities, common coordinate transforms
#   mcmc      — Bayesian inference, MCMC sampling, BMA, uncertainty propagation
#   optimization — NSGA-II multi-objective Pareto optimization for windmill siting
#   windmill_effects — Physical, biological, and human effects of offshore wind turbines
#   sensitivity — Sobol' and Morris sensitivity analysis via SALib
#
# Every parameter used here is derived from real data. No fabricated coefficients.
# See: api/variables.md for the 169-variable source catalog.
# See: platform/architecture.md for system architecture and module specifications.

from .spatial import (
    ROI_BOUNDS,
    SPATIAL_RESOLUTION,
    LAT_CELLS,
    LON_CELLS,
    GRID_CELL_COUNT,
    latlon_to_grid,
    grid_to_latlon,
    is_in_roi,
    grid_cell_area_km2,
    distance_between_cells,
    build_grid_mesh,
)

from .mcmc import (
    BayesianModelAverager,
    HierarchicalBayesianModel,
    MCMCEnsembleSampler,
    UncertaintyPropagator,
    compute_marginal_likelihood_gaussian,
    fit_weibull_prior,
    fit_normal_prior,
    fit_beta_prior,
    gelman_rubin_diagnostic,
    effective_sample_size,
)

from .optimization import (
    NSGA2Optimizer,
    WindEnergyObjective,
    EcologicalImpactObjective,
    HumanConflictObjective,
    HardConstraints,
    ParetoFrontAnalyzer,
)

from .windmill_effects import (
    TurbineSpecification,
    WindWakeModel,
    UnderwaterNoiseModel,
    FoundationScourModel,
    ElectromagneticFieldModel,
    SpeciesExposureRisk,
    CumulativeImpactAssessor,
    LagrangianParticleTracker,
    AcousticPropagationModel,
    EnvironmentalVariableModifier,
)

from .sensitivity import (
    SobolAnalyzer,
    MorrisAnalyzer,
    ParameterSpace,
)

__version__ = "0.1.0"
__all__ = [
    # Spatial
    "ROI_BOUNDS", "SPATIAL_RESOLUTION", "LAT_CELLS", "LON_CELLS",
    "GRID_CELL_COUNT", "latlon_to_grid", "grid_to_latlon",
    "is_in_roi", "grid_cell_area_km2", "distance_between_cells",
    "build_grid_mesh",
    # MCMC
    "BayesianModelAverager", "HierarchicalBayesianModel",
    "MCMCEnsembleSampler", "UncertaintyPropagator",
    "compute_marginal_likelihood_gaussian",
    "fit_weibull_prior", "fit_normal_prior", "fit_beta_prior",
    "gelman_rubin_diagnostic", "effective_sample_size",
    # Optimization
    "NSGA2Optimizer", "WindEnergyObjective",
    "EcologicalImpactObjective", "HumanConflictObjective",
    "HardConstraints", "ParetoFrontAnalyzer",
    # Windmill effects
    "TurbineSpecification", "WindWakeModel",
    "UnderwaterNoiseModel", "FoundationScourModel",
    "ElectromagneticFieldModel", "SpeciesExposureRisk",
    "CumulativeImpactAssessor", "LagrangianParticleTracker",
    "AcousticPropagationModel", "EnvironmentalVariableModifier",
    # Sensitivity
    "SobolAnalyzer", "MorrisAnalyzer", "ParameterSpace",
]
