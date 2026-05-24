"""Advanced statistical tool implementations.

Each function here implements a complete scientific tool that can be
called from the engine's _dispatch() method. All functions:
- Accept real data (no synthetic/mock inputs)
- Return ToolResult with StatResults (bootstrap CI, effect sizes, benchmarks)
- Handle missing data gracefully

These complement the basic tool implementations in engine.py ToolRunner.
"""

import numpy as np
from scipy import stats
import time, warnings
from typing import Dict, List, Optional, Callable, Tuple

from marine_platform.engine import ToolResult, StatResult, StatsFramework
from marine_platform.variables.registry import get_variable, VARIABLES

warnings.filterwarnings('ignore')


# ══════════════════════════════════════════════════════════════════════════════
# A12: Sobol' Variance-Based Global Sensitivity Analysis
# ══════════════════════════════════════════════════════════════════════════════

def run_sobol_sensitivity(
    model_func: Callable,
    param_names: List[str],
    bounds: List[Tuple[float, float]],
    n_base: int = 1024,
    sf: StatsFramework = None,
) -> ToolResult:
    """Run Sobol' variance-based sensitivity analysis.

    Saltelli et al. (2010) estimator: N base samples → N*(k+2) model evaluations.
    Computes first-order (S1) and total-effect (ST) indices with bootstrap CIs.

    Args:
        model_func: f(params_vector) → scalar output
        param_names: list of parameter names
        bounds: list of (low, high) for each parameter
        n_base: base sample size (powers of 2 recommended for Sobol' sequences)
    """
    t0 = time.time()
    sf = sf or StatsFramework()
    result = ToolResult(tool_id="A12_Sobol", status="ok")
    result.variable_count = len(param_names)

    k = len(param_names)

    try:
        from marine_platform.science.sensitivity import SobolAnalyzer, ParameterSpace

        space = ParameterSpace(param_names, bounds)
        analyzer = SobolAnalyzer(model_func, space)

        sobol_result = analyzer.analyze(n_samples=n_base)

        # First-order indices
        S1 = sobol_result.get('S1', {})
        ST = sobol_result.get('ST', {})
        S1_ci = sobol_result.get('S1_ci', {})
        ST_ci = sobol_result.get('ST_ci', {})

        for name in param_names:
            if name in S1:
                s1_val = float(S1[name])
                result.statistics.append(sf.stat(
                    f"S1_{name}", s1_val, "",
                    notes="Sobol' first-order index (fraction of variance from parameter alone)",
                ))
            if name in ST:
                st_val = float(ST[name])
                result.statistics.append(sf.stat(
                    f"ST_{name}", st_val, "",
                    notes="Sobol' total-effect index (includes all interactions)",
                ))

        # Convergence check
        if S1_ci:
            max_ci_width = max(
                abs(ci[1] - ci[0]) for ci in S1_ci.values() if len(ci) == 2)
            result.statistics.append(sf.stat(
                "max_S1_ci_width", max_ci_width, "",
                published_range="<0.1", published_source="Convergence heuristic",
            ))

        result.outputs = {
            'S1': {k: float(v) for k, v in S1.items()},
            'ST': {k: float(v) for k, v in ST.items()},
            'n_evaluations': n_base * (k + 2),
            'converged': max_ci_width < 0.1 if S1_ci else None,
        }

    except Exception as e:
        result.status = "degraded"
        result.warnings.append(f"Sobol' analysis failed: {e}")

    result.timing_s = time.time() - t0
    return result


# ══════════════════════════════════════════════════════════════════════════════
# F2: Bayesian Model Averaging — Multi-Model Ensemble
# ══════════════════════════════════════════════════════════════════════════════

def run_bayesian_model_averaging(
    model_predictions: Dict[str, np.ndarray],
    validation_data: np.ndarray,
    sf: StatsFramework = None,
) -> ToolResult:
    """Run Bayesian Model Averaging across multiple model predictions.

    Computes BMA weights from marginal likelihood on validation data
    and generates posterior predictive distributions.

    Args:
        model_predictions: dict of model_name → predictions array (n_samples,)
        validation_data: observed values for weight computation (n_obs,)
    """
    t0 = time.time()
    sf = sf or StatsFramework()
    result = ToolResult(tool_id="F2_BMA_Ensemble", status="ok")
    result.variable_count = len(model_predictions)

    try:
        from marine_platform.science.mcmc import BayesianModelAverager

        bma = BayesianModelAverager(model_predictions, validation_data)
        weights = bma.compute_weights()

        # Posterior predictive
        posterior = bma.posterior_predictive()

        # Stats
        for model_name, weight in weights.items():
            result.statistics.append(sf.stat(
                f"BMA_weight_{model_name}", weight, "",
                notes="Posterior model probability from marginal likelihood",
            ))

        # Ensemble mean and prediction interval
        ens_mean = float(np.mean(posterior))
        ens_ci_low = float(np.percentile(posterior, 2.5))
        ens_ci_high = float(np.percentile(posterior, 97.5))
        ens_std = float(np.std(posterior))

        result.statistics.append(sf.stat("ensemble_mean", ens_mean, "",
            notes="BMA posterior predictive mean"))

        result.statistics.append(sf.stat("ensemble_std", ens_std, "",
            notes="BMA posterior predictive std (includes inter-model uncertainty)"))

        # Compare to individual models
        single_model_stds = []
        for name, preds in model_predictions.items():
            single_model_stds.append(float(np.std(preds)))

        result.statistics.append(sf.stat(
            "bma_vs_best_single_std_ratio", ens_std / max(min(single_model_stds), 1e-10), "",
            published_range="0.5-2.0",
            published_source="BMA should widen intervals vs single model (Hoeting et al. 1999)",
        ))

        result.outputs = {
            'weights': weights,
            'ensemble_mean': ens_mean,
            'ensemble_ci95': [ens_ci_low, ens_ci_high],
            'ensemble_std': ens_std,
            'n_models': len(model_predictions),
            'prediction_interval': ens_ci_high - ens_ci_low,
        }

    except Exception as e:
        result.status = "degraded"
        result.warnings.append(f"BMA failed: {e}")

    result.timing_s = time.time() - t0
    return result


# ══════════════════════════════════════════════════════════════════════════════
# F3: Hierarchical Bayesian Modeling
# ══════════════════════════════════════════════════════════════════════════════

def run_hierarchical_bayes(
    site_data: Dict[str, np.ndarray],
    regional_data: np.ndarray,
    n_iter: int = 5000,
    n_burnin: int = 1000,
    sf: StatsFramework = None,
) -> ToolResult:
    """Run hierarchical Bayesian model with regional/site/seasonal levels.

    Uses the HierarchicalBayesianModel from mcmc.py.
    Gibbs sampler for Normal-Normal hierarchy.

    Args:
        site_data: dict of site_name → data array (e.g., temperature timeseries)
        regional_data: pooled regional data array
    """
    t0 = time.time()
    sf = sf or StatsFramework()
    result = ToolResult(tool_id="F3_HierarchicalBayes", status="ok")
    result.variable_count = len(site_data)

    try:
        from marine_platform.science.mcmc import HierarchicalBayesianModel

        hbm = HierarchicalBayesianModel(site_data, regional_data)
        posterior = hbm.fit_gibbs(n_iter=n_iter, n_burnin=n_burnin)

        # Regional mean
        mu_region = posterior.get('mu_region', np.array([np.nan]))
        mu_mean = float(np.nanmean(mu_region))
        mu_ci = (float(np.nanpercentile(mu_region, 2.5)),
                 float(np.nanpercentile(mu_region, 97.5)))

        result.statistics.append(sf.stat("regional_mean", mu_mean, "",
            notes="Posterior mean of regional-level parameter"))

        # Site-level deviations
        site_deviations = posterior.get('site_deviations', {})
        for site_name, dev_samples in site_deviations.items():
            dev_mean = float(np.nanmean(dev_samples))
            result.statistics.append(sf.stat(
                f"site_deviation_{site_name[:15]}", dev_mean, "",
                notes="Site-level deviation from regional mean",
            ))

        # Variance partitioning
        sigma_region = float(np.nanmean(posterior.get('sigma_region', [np.nan])))
        sigma_site = float(np.nanmean(posterior.get('sigma_site', [np.nan])))
        sigma_season = float(np.nanmean(posterior.get('sigma_season', [np.nan])))

        total_var = sigma_region**2 + sigma_site**2 + sigma_season**2 + 1e-10
        result.statistics.append(sf.stat(
            "var_frac_region", sigma_region**2 / total_var * 100, "%",
            notes="Variance fraction at regional (Scotian Shelf) level",
        ))
        result.statistics.append(sf.stat(
            "var_frac_site", sigma_site**2 / total_var * 100, "%",
            notes="Variance fraction at site (turbine location) level",
        ))
        result.statistics.append(sf.stat(
            "var_frac_season", sigma_season**2 / total_var * 100, "%",
            notes="Variance fraction at seasonal (monthly) level",
        ))

        result.outputs = {
            'regional_mean': mu_mean,
            'regional_ci95': list(mu_ci),
            'sigma_region': sigma_region,
            'sigma_site': sigma_site,
            'sigma_season': sigma_season,
            'variance_partitioning': {
                'region_pct': sigma_region**2 / total_var * 100,
                'site_pct': sigma_site**2 / total_var * 100,
                'season_pct': sigma_season**2 / total_var * 100,
            },
        }

    except Exception as e:
        result.status = "degraded"
        result.warnings.append(f"Hierarchical Bayes failed: {e}")

    result.timing_s = time.time() - t0
    return result


# ══════════════════════════════════════════════════════════════════════════════
# C5: Formal Uncertainty Propagation
# ══════════════════════════════════════════════════════════════════════════════

def run_uncertainty_propagation(
    impact_chain: List[Callable],
    input_distributions: List[np.ndarray],
    n_monte_carlo: int = 10000,
    sf: StatsFramework = None,
) -> ToolResult:
    """Propagate uncertainty through the entire impact chain.

    Monte Carlo ensemble approach: sample from input distributions,
    pass through each function in the impact chain, compute output distribution.

    Args:
        impact_chain: list of functions f_i(x) → y, composed as f_n(...(f_1(x)))
        input_distributions: list of input samples for each chain link
    """
    t0 = time.time()
    sf = sf or StatsFramework()
    result = ToolResult(tool_id="C5_UncertaintyPropagation", status="ok")
    result.variable_count = len(input_distributions)

    try:
        from marine_platform.science.mcmc import UncertaintyPropagator

        propagator = UncertaintyPropagator(impact_chain, input_distributions)
        ensemble = propagator.propagate(n_samples=n_monte_carlo)

        # Output distribution statistics
        output_mean = float(np.nanmean(ensemble))
        output_std = float(np.nanstd(ensemble))
        output_ci_low = float(np.nanpercentile(ensemble, 2.5))
        output_ci_high = float(np.nanpercentile(ensemble, 97.5))

        result.statistics.append(sf.stat(
            "output_mean", output_mean, "",
            notes="Mean of propagated output distribution",
        ))
        result.statistics.append(sf.stat(
            "output_std", output_std, "",
            notes="Std dev of propagated output (total uncertainty)",
        ))
        result.statistics.append(sf.stat(
            "output_ci95_width", output_ci_high - output_ci_low, "",
            notes="95% CI width — measure of total uncertainty",
        ))

        # Convergence check
        if len(ensemble) > 1000:
            running_mean = np.cumsum(ensemble) / np.arange(1, len(ensemble) + 1)
            last_pct_change = abs(running_mean[-1] - running_mean[-100]) / max(abs(running_mean[-1]), 1e-10)
            converged = last_pct_change < 0.001  # 0.1% change in last 100 samples
            result.statistics.append(sf.stat(
                "convergence_check", last_pct_change, "",
                published_range="<0.001",
                published_source="MC convergence: <0.1% mean change in last 100 samples",
            ))

        result.outputs = {
            'mean': output_mean,
            'std': output_std,
            'ci95': [output_ci_low, output_ci_high],
            'n_samples': n_monte_carlo,
            'converged': converged if len(ensemble) > 1000 else None,
        }

    except Exception as e:
        result.status = "degraded"
        result.warnings.append(f"Uncertainty propagation failed: {e}")

    result.timing_s = time.time() - t0
    return result


# ══════════════════════════════════════════════════════════════════════════════
# E1 Auxiliary: ParetoFront Analysis (post-NSGA-II)
# ══════════════════════════════════════════════════════════════════════════════

def run_pareto_analysis(
    pareto_objectives: np.ndarray,
    objective_names: List[str],
    sf: StatsFramework = None,
) -> ToolResult:
    """Analyze Pareto front: knee point, trade-offs, hypervolume.

    Run AFTER NSGA-II optimization to extract decision-relevant insights.

    Args:
        pareto_objectives: (n_solutions, n_objectives) array
        objective_names: names of each objective
    """
    t0 = time.time()
    sf = sf or StatsFramework()
    result = ToolResult(tool_id="E2_ParetoAnalysis", status="ok")
    result.variable_count = pareto_objectives.shape[1]

    try:
        from marine_platform.science.optimization import ParetoFrontAnalyzer

        analyzer = ParetoFrontAnalyzer(pareto_objectives, objective_names)

        # Knee point
        knee = analyzer.knee_point()
        if knee is not None:
            for i, name in enumerate(objective_names):
                result.statistics.append(sf.stat(
                    f"knee_point_{name}", float(knee[i]), "",
                    notes="Knee point — best trade-off solution",
                ))

        # Trade-off matrix
        tradeoffs = analyzer.trade_off_matrix()
        for (name_i, name_j), rate in tradeoffs.items():
            result.statistics.append(sf.stat(
                f"tradeoff_{name_i}_vs_{name_j}", float(rate), "",
                notes="Marginal rate of substitution between objectives",
            ))

        # Hypervolume
        hv = analyzer.compute_hypervolume()
        result.statistics.append(sf.stat(
            "hypervolume", float(hv), "",
            published_range=">0", published_source="Zitzler & Thiele (1999)",
            notes="Hypervolume indicator — larger = better Pareto front coverage",
        ))

        result.outputs = {
            'knee_point': knee.tolist() if knee is not None else None,
            'trade_offs': {f"{k[0]}_vs_{k[1]}": float(v) for k, v in tradeoffs.items()},
            'hypervolume': float(hv),
            'n_pareto_solutions': pareto_objectives.shape[0],
        }

    except Exception as e:
        result.status = "degraded"
        result.warnings.append(f"Pareto analysis failed: {e}")

    result.timing_s = time.time() - t0
    return result
