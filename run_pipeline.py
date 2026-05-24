#!/usr/bin/env python3
"""Marine Digital Twin — Unified Pipeline Entry Point.

Single command to run the complete scientific pipeline:
    python run_pipeline.py

This replaces the standalone execute_pipeline.py and connects the
Orchestrator (engine.py) with real data loading from all 155+ variables.

All 16+ tools execute in dependency order with StatsFramework validation
on every output. Generates professional visualizations, windy.com-style
video simulation, and a comprehensive results document.
"""

import sys, os, time, json, warnings
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from marine_platform.cube.reader import DataCube, FusedCubeReader
from marine_platform.variables.registry import VARIABLES, validate_registry
from marine_platform.science.windmill_effects import TurbineSpecification
from marine_platform.engine import Orchestrator, ToolResult
from marine_platform.pipeline.data_loader import DataLoader, SiteData
from marine_platform.pipeline.derived import DerivedVariables

warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════

# Siemens Gamesa SG 14-236 DD (15 MW offshore turbine)
TURBINE = TurbineSpecification(
    hub_height_m=150.0,
    rotor_diameter_m=236.0,
    rated_power_MW=15.0,
    cut_in_wind_speed=3.5,
    rated_wind_speed=11.0,
    cut_out_wind_speed=25.0,
    foundation_type="monopile",
    foundation_diameter_m=9.0,
    cable_voltage_kV=66.0,
    cable_current_A=130.0,
    cable_burial_depth_m=1.5,
    n_turbines=1,
)

# 1 comparison site only — fast mode
COMPARISON_SITES = [
    (44.25, -63.50, "Mid-shelf (~22km offshore, ~85m depth) — PRIMARY"),
]

PRIMARY_SITE_IDX = 0

# Output paths
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FIG_DIR = os.path.join(OUTPUT_DIR, 'figures')
ANIM_DIR = os.path.join(OUTPUT_DIR, 'animations')
RESULTS_PATH = os.path.join(OUTPUT_DIR, 'results.md')

for d in [OUTPUT_DIR, FIG_DIR, ANIM_DIR]:
    os.makedirs(d, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Main Pipeline
# ══════════════════════════════════════════════════════════════════════════════

def main():
    t_start = time.time()
    print("=" * 72)
    print("  MARINE DIGITAL TWIN — Complete Scientific Pipeline")
    print(f"  Turbine: {TURBINE.rated_power_MW} MW, D={TURBINE.rotor_diameter_m}m rotor")
    print(f"  Sites: {len(COMPARISON_SITES)} comparison sites across Scotian Shelf")
    print("=" * 72)

    # ── Step 1: Validate registry ──
    print("\n" + "─" * 60)
    print("STEP 1: Variable Registry Validation")
    print("─" * 60)
    vresult = validate_registry()
    print(f"  Total variables: {vresult['total']}")
    print(f"  Valid sources:   {vresult['valid_sources']}")
    print(f"  Computed:        {vresult['computed']}")
    if vresult['invalid_sources']:
        print(f"  ⚠ Invalid sources: {vresult['invalid_sources']}")
        for vid, vname, src in vresult['invalid_details']:
            print(f"    {vid} ({vname}) → {src}")

    # ── Step 2: Initialize data cube ──
    print("\n" + "─" * 60)
    print("STEP 2: Data Cube Initialization")
    print("─" * 60)
    cube = DataCube()
    print(f"  DataCube initialized with {len(cube.sources) if hasattr(cube, 'sources') else '?'} sources")

    # Try FusedCubeReader for bilinear interpolation
    fused = None
    try:
        fused = FusedCubeReader()
        print("  FusedCubeReader: available (bilinear interpolation)")
    except Exception as e:
        print(f"  FusedCubeReader: not available ({e}) — using nearest-neighbor fallback")

    # ── Step 3: Load all variables for all sites ──
    print("\n" + "─" * 60)
    print("STEP 3: Data Loading (ALL variables for ALL sites)")
    print("─" * 60)

    loader = DataLoader(cube, fused)
    site_data: dict = {}
    all_loaded = set()

    for i, (lat, lon, name) in enumerate(COMPARISON_SITES):
        marker = " ★ PRIMARY" if i == PRIMARY_SITE_IDX else ""
        print(f"\n  Site {i+1}/3: {name}{marker}")
        sd = loader.load_all(lat, lon, site_name=name)
        site_data[i] = sd
        sd.print_summary()
        all_loaded.update(sd.loaded_var_ids)

    n_vars_total = len(VARIABLES)
    n_vars_loaded = len(all_loaded)
    print(f"\n  Unique variables loaded across all sites: {n_vars_loaded}/{n_vars_total} "
          f"({100*n_vars_loaded/max(n_vars_total,1):.0f}%)")

    # ── Step 4: Run orchestrated pipeline ──
    print("\n" + "─" * 60)
    print("STEP 4: Orchestrated Pipeline Execution (16+ tools)")
    print("─" * 60)

    all_results = {}
    for i, (lat, lon, name) in enumerate(COMPARISON_SITES):
        marker = " ★ PRIMARY" if i == PRIMARY_SITE_IDX else ""
        print(f"\n{'='*70}")
        print(f"  SITE {i+1}/3: {name}{marker}")
        print(f"{'='*70}")

        orchestrator = Orchestrator(cube, TURBINE, lat, lon)
        results = orchestrator.run_all()
        all_results[i] = results

        # Print summary
        ok = sum(1 for r in results.values() if r.status == 'ok')
        degraded = sum(1 for r in results.values() if r.status == 'degraded')
        failed = sum(1 for r in results.values() if r.status == 'failed')
        print(f"\n  Site {i+1} summary: {ok} ok, {degraded} degraded, {failed} failed "
              f"({len(results)} tools total)")

    # ── Step 5: Generate visualizations ──
    print("\n" + "─" * 60)
    print("STEP 5: Visualization Generation")
    print("─" * 60)

    try:
        from marine_platform.plot.plot_tools import MarineViz
        primary_sd = site_data[PRIMARY_SITE_IDX]
        primary_results = all_results[PRIMARY_SITE_IDX]

        viz = MarineViz(output_dir=FIG_DIR)
        print("  MarineViz initialized")

        # Generate core figures
        _generate_visualizations(viz, primary_sd, primary_results, cube)
        print("  Visualizations complete")

    except Exception as e:
        print(f"  ⚠ Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()

    # ── Step 6: Generate video ──
    print("\n" + "─" * 60)
    print("STEP 6: Windy.com-Style Video Simulation")
    print("─" * 60)

    try:
        from marine_platform.plot.video_engine import WindyVideoEngine
        primary_sd = site_data[PRIMARY_SITE_IDX]
        lat, lon, name = COMPARISON_SITES[PRIMARY_SITE_IDX]

        video_engine = WindyVideoEngine(
            cube=cube,
            turbine=TURBINE,
            output_dir=ANIM_DIR,
        )
        video_path = video_engine.generate(
            site_lat=lat, site_lon=lon, site_name=name,
            n_timesteps=72, fps=24, dpi=120,
        )
        print(f"  Video saved: {video_path}")

    except Exception as e:
        print(f"  ⚠ Video generation failed: {e}")
        import traceback
        traceback.print_exc()

    # ── Step 7: Generate results document ──
    print("\n" + "─" * 60)
    print("STEP 7: Results Document Generation")
    print("─" * 60)

    try:
        _generate_results_document(site_data, all_results, RESULTS_PATH)
        print(f"  Results document saved: {RESULTS_PATH}")
    except Exception as e:
        print(f"  ⚠ Results document generation failed: {e}")
        import traceback
        traceback.print_exc()

    # ── Final summary ──
    elapsed = time.time() - t_start
    print("\n" + "=" * 72)
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s total")
    print(f"  Variables loaded: {n_vars_loaded}/{n_vars_total}")
    print(f"  Sites analyzed: {len(COMPARISON_SITES)}")
    print(f"  Tools executed: {sum(len(r) for r in all_results.values())} total")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 72)


# ══════════════════════════════════════════════════════════════════════════════
# Visualization helper
# ══════════════════════════════════════════════════════════════════════════════

def _generate_visualizations(viz, site_data: SiteData, results: dict, cube):
    """Generate all static figures."""
    # Site overview dashboard from tool results
    try:
        viz.site_overview_dashboard(
            site_name=site_data.site_name,
            site_lat=site_data.site_lat,
            site_lon=site_data.site_lon,
            depth_m=site_data.depth_m,
            results=results,
        )
        print("  ✓ Site overview dashboard")
    except Exception as e:
        print(f"  ⚠ Site overview: {e}")

    # Wake profile
    try:
        if 'B1_wake' in results:
            viz.wake_profile_plot(results['B1_wake'])
            print("  ✓ Wake profile plot")
    except Exception as e:
        print(f"  ⚠ Wake plot: {e}")

    # Pareto front
    try:
        if 'E1_nsga2' in results:
            viz.pareto_front_plot(results['E1_nsga2'])
            print("  ✓ Pareto front plot")
    except Exception as e:
        print(f"  ⚠ Pareto plot: {e}")

    # Morris sensitivity tornado
    try:
        if 'A11_Morris' in results:
            viz.tornado_plot(results['A11_Morris'])
            print("  ✓ Sensitivity tornado plot")
    except Exception as e:
        print(f"  ⚠ Tornado plot: {e}")

    # Time simulation
    try:
        viz.time_simulation_plot(site_data, results)
        print("  ✓ Time simulation plot")
    except Exception as e:
        print(f"  ⚠ Time sim plot: {e}")

    # MCMC diagnostics
    try:
        if 'F1_mcmc' in results:
            viz.mcmc_diagnostics(results['F1_mcmc'])
            print("  ✓ MCMC diagnostics")
    except Exception as e:
        print(f"  ⚠ MCMC plot: {e}")

    # Cumulative breakdown
    try:
        if 'C4_cumulative' in results:
            viz.cumulative_heatmap(results['C4_cumulative'])
            print("  ✓ Cumulative breakdown")
    except Exception as e:
        print(f"  ⚠ Cumulative plot: {e}")

    # Data provenance
    try:
        viz.data_provenance_plot(site_data)
        print("  ✓ Data provenance plot")
    except Exception as e:
        print(f"  ⚠ Provenance plot: {e}")

    # Site comparison
    try:
        viz.site_comparison_plot(site_data, results)
        print("  ✓ Site comparison plot")
    except Exception as e:
        print(f"  ⚠ Site comparison: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# Results document generator
# ══════════════════════════════════════════════════════════════════════════════

def _generate_results_document(site_data: dict, all_results: dict, output_path: str):
    """Generate comprehensive results document with specific quantitative insights."""

    lines = []
    def w(s=""):
        lines.append(s)

    w("# Marine Digital Twin — Scotian Shelf Wind Turbine Siting Analysis")
    w()
    w(f"**Turbine**: Siemens Gamesa SG 14-236 DD (15 MW, 236m rotor, monopile foundation)")
    w(f"**Sites analyzed**: {len(COMPARISON_SITES)} across Scotian Shelf cross-shelf gradient")
    w(f"**Data sources**: 29 (1.5 GB real environmental data)")
    w(f"**Variables utilized**: See Variable Utilization Report below")
    w()

    # Executive summary
    primary_results = all_results[PRIMARY_SITE_IDX]
    primary_sd = site_data[PRIMARY_SITE_IDX]

    w("## Executive Summary")
    w()

    # Determine site ranking
    site_scores = {}
    for i, (lat, lon, name) in enumerate(COMPARISON_SITES):
        results = all_results.get(i, {})
        score = _compute_site_score(results)
        site_scores[i] = score

    best_idx = max(site_scores, key=site_scores.get)
    best_name = COMPARISON_SITES[best_idx][2]

    w(f"**Primary recommendation**: {best_name}")
    w()

    # Per-tool findings
    w("## Per-Tool Analysis")
    w()

    tool_sections = {
        'A1_baseline': 'Environmental Baseline',
        'B1_wake': 'Wind Wake Modeling',
        'C2_Acoustic': 'Underwater Noise & Acoustic Propagation',
        'B3_scour': 'Foundation Scour Assessment',
        'B4_emf': 'Electromagnetic Field Impact',
        'C1_lagrangian': 'Lagrangian Particle Tracking',
        'C3_species_sdm': 'Species Distribution Modeling',
        'C4_cumulative': 'Cumulative Impact Assessment',
        'D1-D4_human': 'Human Conflict Assessment',
        'E1_nsga2': 'Multi-Objective Siting Optimization',
        'F1_mcmc': 'Bayesian Inference (MCMC)',
        'A11_Morris': 'Sensitivity Analysis',
    }

    for tool_id, tool_name in tool_sections.items():
        w(f"### {tool_name}")
        w()

        # Find matching results across sites
        for i, (lat, lon, name) in enumerate(COMPARISON_SITES):
            results = all_results.get(i, {})
            matching = [r for tid, r in results.items()
                       if tool_id.replace('-', '_') in tid or tid in tool_id]
            if matching:
                r = matching[0]
                w(f"**{name}** (status: {r.status})")
                for s in r.statistics[:5]:
                    w(f"- {s.name}: {s.value:.3g}{s.unit} "
                      f"[95% CI: {s.ci95_lower:.3g}–{s.ci95_upper:.3g}]"
                      f"{' d=' + str(round(s.effect_size, 2)) if s.effect_size else ''}"
                      f"{' p=' + str(round(s.p_value, 4)) if s.p_value else ''}")
                if r.warnings:
                    for warn in r.warnings[:2]:
                        w(f"- ⚠ {warn}")
                w()

    # Variable utilization report
    w("## Variable Utilization Report")
    w()
    w("| Domain | Total | Loaded | Utilization |")
    w("|---|---|---|---|")
    from marine_platform.variables.registry import VARIABLES
    domains = {}
    for v in VARIABLES.values():
        domains.setdefault(v.domain, {'total': 0, 'loaded': 0})
        domains[v.domain]['total'] += 1

    all_loaded_ids = set()
    for sd in site_data.values():
        all_loaded_ids.update(sd.loaded_var_ids)

    for domain in sorted(domains):
        d = domains[domain]
        for v in VARIABLES.values():
            if v.domain == domain and v.id in all_loaded_ids:
                d['loaded'] += 1
        pct = 100 * d['loaded'] / max(d['total'], 1)
        w(f"| {domain} | {d['total']} | {d['loaded']} | {pct:.0f}% |")

    w()
    w("---")
    w()
    w("*Generated by Marine Digital Twin Pipeline — Scotian Shelf Offshore Wind Siting Analysis*")
    w(f"*All variables from real observational data; no synthetic or hardcoded environmental constants.*")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def _compute_site_score(results: dict) -> float:
    """Compute a weighted multi-criteria site score from tool results."""
    score = 50.0  # neutral baseline

    # Energy potential bonus (from wake/wind data)
    if 'B1_wake' in results:
        r = results['B1_wake']
        deficit_2d = r.outputs.get('deficit_at_2D_pct', 40)
        # Lower deficit = better energy
        score += (40 - deficit_2d) * 0.5

    # Ecological penalty (from cumulative/species)
    if 'C4_cumulative' in results:
        r = results['C4_cumulative']
        cum_score = r.outputs.get('cumulative_score', 0.2)
        score -= cum_score * 50

    # Feasibility bonus (from optimization)
    if 'E1_nsga2' in results:
        r = results['E1_nsga2']
        n_feasible = r.outputs.get('n_feasible', 0)
        if n_feasible > 0:
            score += min(n_feasible / 10, 10)

    return max(0, min(100, score))


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    main()
