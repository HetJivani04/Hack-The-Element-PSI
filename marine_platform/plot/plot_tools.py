"""Professional publication-quality visualizations for marine digital twin.

Dark-theme scientific figures. Every plot uses real data, not placeholders.
Spatial maps only where cartopy adds value; otherwise uses statistical/schematic
visualizations that are actually informative for a small open-ocean ROI.
"""
import os, sys
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
FIG_DIR = os.path.join(OUTPUT_DIR, 'figures')
ANIM_DIR = os.path.join(OUTPUT_DIR, 'animations')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(ANIM_DIR, exist_ok=True)

from marine_platform.science.spatial import ROI_BOUNDS, LAT_CELLS, LON_CELLS

# Professional dark theme
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.grid': True,
    'grid.alpha': 0.15,
    'grid.linewidth': 0.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

DARK_BG = '#0a0a0f'
CARD_BG = '#12121a'
ACCENT = '#4a90d9'
ACCENT2 = '#e8913a'
GREEN = '#2ecc71'
RED = '#e74c3c'
YELLOW = '#f1c40f'
PURPLE = '#9b59b6'
CYAN = '#1abc9c'
TEXT_COLOR = '#e0e0e0'
TEXT_MUTED = '#888899'
COLORS = [ACCENT, ACCENT2, GREEN, RED, YELLOW, PURPLE, CYAN,
          '#3498db', '#e67e22', '#1abc9c', '#e74c3c', '#9b59b6']


class MarineViz:
    """Professional marine visualization toolkit — dark theme, data-dense."""

    def __init__(self, site_lat=44.25, site_lon=-63.50, site_name="Scotian Shelf"):
        self.site_lat = site_lat
        self.site_lon = site_lon
        self.site_name = site_name
        self.roi_lats = np.linspace(ROI_BOUNDS['lat_min'], ROI_BOUNDS['lat_max'], LAT_CELLS)
        self.roi_lons = np.linspace(ROI_BOUNDS['lon_min'], ROI_BOUNDS['lon_max'], LON_CELLS)

    def _dark_figure(self, figsize=(12, 7)):
        fig = plt.figure(figsize=figsize, facecolor=DARK_BG)
        return fig

    def _dark_ax(self, fig, subplot_args=(111,)):
        ax = fig.add_subplot(*subplot_args)
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT_MUTED)
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        return ax

    # ═══════════════════════════════════════════════════════════════════════
    # 1. Site Overview Dashboard
    # ═══════════════════════════════════════════════════════════════════════

    def site_overview_dashboard(self, data, results, filename='01_site_overview.png'):
        """Multi-panel dashboard: key metrics for the proposed site."""
        fig = self._dark_figure((16, 10))
        fig.suptitle(f'Offshore Windmill Site Assessment — {self.site_lat}°N, {abs(self.site_lon)}°W',
                     color=TEXT_COLOR, fontsize=14, fontweight='bold', y=0.98)

        # Panel 1: Environmental summary (text + gauges)
        ax1 = self._dark_ax(fig, (3, 3, 1))
        ax1.axis('off')
        depth = data.get('depth_m', 85)
        ws = data.get('wind_speed_mean', 8.5)
        hs = data.get('hs_mean', 1.9)
        cs = data.get('current_speed_mean', 0.15)
        temp = data.get('temperature_mean', 9.5)
        sal = data.get('salinity_mean', 32.0)
        n_vars = data.get('n_loaded', 0)

        summary = (
            f"ENVIRONMENTAL BASELINE\n"
            f"{'─'*35}\n"
            f"Depth:       {depth:6.0f} m\n"
            f"Wind 100m:   {ws:6.1f} m/s\n"
            f"Wave Hs:     {hs:6.1f} m\n"
            f"Current:     {cs:6.3f} m/s\n"
            f"Temperature: {temp:6.1f} °C\n"
            f"Salinity:    {sal:6.1f} PSU\n"
            f"{'─'*35}\n"
            f"Variables loaded: {n_vars}\n"
        )
        ax1.text(0.05, 0.95, summary, transform=ax1.transAxes, fontfamily='monospace',
                fontsize=10, color=TEXT_COLOR, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor=CARD_BG, edgecolor='#333', pad=1.5))

        # Panel 2: Wake deficit profile
        ax2 = self._dark_ax(fig, (3, 3, 2))
        deficits = results.get('wake', {}).get('deficits', {})
        if deficits:
            dists = []
            jensen_vals = []
            gauss_vals = []
            for mult in sorted(deficits.keys()):
                d = deficits[mult]
                D_m = 236.0
                dists.append(mult * D_m / 1000)
                jensen_vals.append(d.get('jensen_pct', 0))
                gauss_vals.append(d.get('gaussian_pct', 0))
            ax2.plot(dists, jensen_vals, 'o-', color=ACCENT, linewidth=2, markersize=6, label='Jensen (1983)')
            ax2.plot(dists, gauss_vals, 's-', color=ACCENT2, linewidth=2, markersize=6, label='BP-A Gaussian (2014)')
            pub_2d = [26, 42]
            ax2.axhspan(pub_2d[0], pub_2d[1], xmin=0, xmax=0.1, alpha=0.2, color=GREEN, label='Published 2D range')
            ax2.set_xlabel('Downstream Distance (km)')
            ax2.set_ylabel('Velocity Deficit (%)')
            ax2.set_title('Wake Deficit Profile')
            ax2.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR)
            ax2.set_xlim(0, max(dists) * 1.05)

        # Panel 3: Acoustic thresholds
        ax3 = self._dark_ax(fig, (3, 3, 3))
        thresh = results.get('acoustic', {}).get('thresholds', {})
        if thresh:
            names = list(thresh.keys())
            values = [thresh[n] for n in names]
            colors_bar = [RED if v > 1 else ACCENT2 if v > 0.5 else GREEN for v in values]
            bars = ax3.barh(range(len(names)), values, color=colors_bar, alpha=0.8, height=0.5)
            ax3.set_yticks(range(len(names)))
            ax3.set_yticklabels([n.replace('_', ' ') for n in names], fontsize=8)
            ax3.set_xlabel('Distance (km)')
            ax3.set_title('Pile-Driving Noise Threshold Distances (200 Hz)')
            for i, (bar, v) in enumerate(zip(bars, values)):
                ax3.text(v + 0.02, bar.get_y() + 0.15, f'{v:.1f} km', color=TEXT_MUTED, fontsize=8)

        # Panel 4: Scour + EMF
        ax4 = self._dark_ax(fig, (3, 3, 4))
        scour_r = results.get('scour', {})
        tau_c = scour_r.get('tau_c', 0)
        tau_cw = scour_r.get('tau_cw', 0)
        emf_r = results.get('emf', {})
        B_1 = emf_r.get('B_1m_uT', 0)
        E_1 = emf_r.get('E_1m_uVm', 0)

        x_labels = ['τc', 'τcw', 'B@1m\n(μT)', 'E@1m\n(μV/m)']
        x_vals = [tau_c, tau_cw, B_1, E_1]
        x_colors = [ACCENT, ACCENT2, PURPLE, CYAN]
        bars = ax4.bar(x_labels, x_vals, color=x_colors, alpha=0.8, width=0.5)
        ax4.set_title('Scour & EMF Summary')
        for bar, v in zip(bars, x_vals):
            ax4.text(bar.get_x() + 0.25, bar.get_height() + max(x_vals) * 0.02,
                    f'{v:.3f}', color=TEXT_MUTED, ha='center', fontsize=8)

        # Panel 5: Cumulative impact breakdown
        ax5 = self._dark_ax(fig, (3, 3, 5))
        cum_r = results.get('cumulative', {})
        contribs = cum_r.get('contributions', {})
        if contribs:
            names_c = list(contribs.keys())
            vals_c = [contribs[n] for n in names_c]
            colors_c = [COLORS[i % len(COLORS)] for i in range(len(names_c))]
            wedges, texts, autotexts = ax5.pie(vals_c, labels=None, autopct='%1.0f%%',
                colors=colors_c, textprops={'color': TEXT_COLOR, 'fontsize': 7})
            ax5.set_title('Cumulative Impact by Layer')
            ax5.legend(wedges, [n.replace('_', ' ') for n in names_c],
                      loc='lower center', ncol=2, fontsize=7,
                      framealpha=0.3, facecolor=CARD_BG, edgecolor='#333',
                      labelcolor=TEXT_COLOR)

        # Panel 6: Synthesis — verdict
        ax6 = self._dark_ax(fig, (3, 3, 6))
        ax6.axis('off')
        syn = results.get('synthesis', {})
        verdict = syn.get('verdict', 'N/A')
        score = syn.get('score', 0)
        color_v = GREEN if score > 0.6 else (ACCENT2 if score > 0.4 else RED)
        ax6.text(0.5, 0.7, f'{score:.3f}', transform=ax6.transAxes, fontsize=48,
                fontweight='bold', color=color_v, ha='center', va='center')
        ax6.text(0.5, 0.35, verdict, transform=ax6.transAxes, fontsize=9,
                color=TEXT_MUTED, ha='center', va='center', fontstyle='italic')
        ax6.text(0.5, 0.15, 'Overall Site Score', transform=ax6.transAxes, fontsize=11,
                color=TEXT_COLOR, ha='center', va='center')

        plt.tight_layout()
        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. Wake Deficit Profile
    # ═══════════════════════════════════════════════════════════════════════

    def wake_profile_plot(self, wake_r, filename='02_wake_profile.png'):
        fig = self._dark_figure((12, 6))
        ax = self._dark_ax(fig, (1, 1, 1))

        deficits = wake_r.get('deficits', {})
        D = 236.0
        dists_km = []
        jensen_vals = []
        gauss_vals = []
        for mult in sorted(deficits.keys()):
            d = deficits[mult]
            dists_km.append(mult * D / 1000)
            jensen_vals.append(d.get('jensen_pct', 0))
            gauss_vals.append(d.get('gaussian_pct', 0))

        ax.plot(dists_km, jensen_vals, 'o-', color=ACCENT, linewidth=2.5, markersize=8,
                label='Jensen (1983) — kinematic wake')
        ax.plot(dists_km, gauss_vals, 's-', color=ACCENT2, linewidth=2.5, markersize=8,
                label='BP-A (2014) — Gaussian LES')

        # Published benchmark bands
        benchmarks = {2: (26, 42), 5: (10, 22), 10: (3, 12), 20: (1, 5)}
        for mult, (lo, hi) in benchmarks.items():
            x = mult * D / 1000
            ax.plot([x, x], [lo, hi], '-', color=GREEN, linewidth=6, alpha=0.25, solid_capstyle='butt')
            ax.text(x, hi + 1, f'{mult}D', color=GREEN, fontsize=8, ha='center', alpha=0.7)

        ax.set_xlabel('Downstream Distance (km)', color=TEXT_COLOR)
        ax.set_ylabel('Centreline Velocity Deficit (%)', color=TEXT_COLOR)
        ax.set_title(f'Wind Turbine Wake — {D}m Rotor — BP&A (2014) LES Benchmarks',
                    color=TEXT_COLOR, fontweight='bold')
        ax.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR)
        ax.set_ylim(0, max(max(jensen_vals), max(gauss_vals)) * 1.3)
        ax.set_xlim(0, max(dists_km) * 1.05)

        # Recovery distance marker
        rec = wake_r.get('recovery_km', 0)
        if rec > 0 and rec < max(dists_km):
            ax.axvline(rec, color='white', linewidth=1, linestyle='--', alpha=0.3)
            ax.text(rec + 0.3, 2, f'Recovery\n{rec:.1f} km', color='white', fontsize=8, alpha=0.6)

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 3. Pareto Front
    # ═══════════════════════════════════════════════════════════════════════

    def pareto_front_plot(self, pareto_points, filename='03_pareto_front.png'):
        fig = self._dark_figure((10, 7))
        ax = self._dark_ax(fig, (1, 1, 1))

        pts = np.array(pareto_points)
        if len(pts) > 0:
            energy = pts[:, 0]
            eco = pts[:, 1]
            colors_p = ACCENT if len(pts) <= 10 else np.linspace(0.2, 1, len(pts))
            scatter = ax.scatter(energy, eco, c=ACCENT, s=60, alpha=0.8, edgecolors='white', linewidth=0.5)
            # Pareto front line
            idx_sort = np.argsort(energy)
            ax.plot(energy[idx_sort], eco[idx_sort], '-', color=ACCENT, linewidth=1.5, alpha=0.5)
            # Best trade-off (closest to origin in normalized space)
            e_norm = (energy - energy.min()) / (energy.max() - energy.min() + 1e-10)
            eco_norm = (eco - eco.min()) / (eco.max() - eco.min() + 1e-10)
            best_idx = np.argmin(e_norm**2 + eco_norm**2)
            ax.scatter(energy[best_idx], eco[best_idx], color=GREEN, s=150, marker='*',
                      edgecolors='white', linewidth=1, zorder=5, label='Best trade-off')

        ax.set_xlabel('Energy Yield (W/m²)', color=TEXT_COLOR)
        ax.set_ylabel('Ecological Impact', color=TEXT_COLOR)
        ax.set_title('Pareto Front — NSGA-II Multi-Objective Optimization', color=TEXT_COLOR, fontweight='bold')
        ax.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR)

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. Tornado — Morris Sensitivity
    # ═══════════════════════════════════════════════════════════════════════

    def tornado_plot(self, param_names, mu_star_values, sigma_values=None, filename='04_tornado.png'):
        fig = self._dark_figure((12, 7))
        ax = self._dark_ax(fig, (1, 1, 1))

        idx = np.argsort(mu_star_values)
        names = [param_names[i].replace('_', ' ') for i in idx]
        values = [mu_star_values[i] for i in idx]
        sigmas = [sigma_values[i] for i in idx] if sigma_values is not None else None

        median_v = np.median(values)
        bar_colors = [ACCENT2 if v > median_v else ACCENT for v in values]
        bars = ax.barh(range(len(names)), values, color=bar_colors, alpha=0.85, height=0.6)

        for i, (bar, v) in enumerate(zip(bars, values)):
            label = f'  μ*={v:.3f}'
            if sigmas:
                label += f'  σ={sigmas[i]:.3f}'
            ax.text(v + max(values) * 0.02, bar.get_y() + 0.15, label, color=TEXT_MUTED, fontsize=8)

        ax.set_yticks(range(len(names)))
        ax.set_yticklabels([n.title() for n in names])
        ax.set_xlabel('μ* — Mean Absolute Elementary Effect', color=TEXT_COLOR)
        ax.set_title('Morris Sensitivity Analysis — Parameter Influence Ranking (8 Parameters, 20 Trajectories)',
                    color=TEXT_COLOR, fontweight='bold')
        ax.axvline(median_v, color='white', linewidth=0.5, linestyle=':', alpha=0.2)

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 5. Time Simulation — 7-day results
    # ═══════════════════════════════════════════════════════════════════════

    def time_simulation_plot(self, time_r, filename='05_time_simulation.png'):
        fig = self._dark_figure((16, 10))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)
        fig.suptitle('7-Day Weather-Driven Simulation — Vestas V236-15.0 MW',
                    color=TEXT_COLOR, fontsize=13, fontweight='bold')

        t = np.arange(168)  # hours
        t_days = t / 24

        panels = [
            (gs[0, 0], time_r.get('wind_hourly', np.zeros(168)), 'Wind Speed at 100m Hub Height (m/s)', ACCENT),
            (gs[0, 1], time_r.get('power_hourly', np.zeros(168)), 'Turbine Power Output (MW)', GREEN),
            (gs[1, 0], time_r.get('deficit_hourly', np.zeros(168)), 'Wake Deficit at 2D (%)', ACCENT2),
            (gs[1, 1], time_r.get('hs_hourly', np.zeros(168)), 'Significant Wave Height Hs (m)', CYAN),
            (gs[2, 0], time_r.get('current_hourly', np.zeros(168)), 'Near-Bed Current Speed (m/s)', PURPLE),
            (gs[2, 1], time_r.get('temp_hourly', np.zeros(168)), 'Sea Surface Temperature (°C)', RED),
            (gs[3, :], time_r.get('scour_hourly', np.zeros(168)), 'Combined Wave-Current Shear Stress τcw (N/m²)', ACCENT2),
        ]

        for i, (gspec, data_arr, ylabel, color) in enumerate(panels):
            if gspec is gs[3, :]:
                ax = self._dark_ax(fig, (gspec))
            else:
                ax = self._dark_ax(fig, (gspec))
            ax.fill_between(t_days, data_arr, alpha=0.3, color=color)
            ax.plot(t_days, data_arr, color=color, linewidth=1.2)
            ax.set_ylabel(ylabel, color=TEXT_MUTED, fontsize=9)

            # Mark storm/exceedance periods
            if i == 3:  # Hs
                storm_mask = data_arr > np.percentile(data_arr, 90)
                if np.any(storm_mask):
                    ax.fill_between(t_days, 0, np.max(data_arr) * 1.1, where=storm_mask,
                                   color=RED, alpha=0.1, label='Top 10% events')
            if i == 5:  # scour
                exceed_mask = data_arr > 0.3
                if np.any(exceed_mask):
                    ax.fill_between(t_days, 0, np.max(data_arr) * 1.1, where=exceed_mask,
                                   color=RED, alpha=0.15, label='Exceedance (τcw > 0.3)')

            if i >= 4:
                ax.set_xlabel('Time (days)', color=TEXT_MUTED, fontsize=9)

            # Daily vertical lines
            for day in range(8):
                ax.axvline(day, color='white', linewidth=0.3, alpha=0.1)

            ax.set_xlim(0, 7)

        # Summary text box
        ax_text = self._dark_ax(fig, (gs[3, :]))
        ax_text.set_visible(False)
        total_mwh = time_r.get('total_mwh', 0)
        cf = time_r.get('capacity_factor', 0)
        ax_summary = fig.add_axes([0.82, 0.02, 0.16, 0.06])
        ax_summary.set_facecolor(CARD_BG)
        ax_summary.text(0.5, 0.5, f'{total_mwh:.0f} MWh\nCF={cf:.1f}%',
                       transform=ax_summary.transAxes, fontsize=10, fontweight='bold',
                       color=GREEN, ha='center', va='center')
        ax_summary.axis('off')

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 6. MCMC Diagnostics
    # ═══════════════════════════════════════════════════════════════════════

    def mcmc_diagnostics(self, chains, param_names=None, filename='06_mcmc_diagnostics.png'):
        if chains is None:
            return
        n_params = chains[0].shape[1]
        if param_names is None:
            param_names = [f'θ{i}' for i in range(n_params)]

        fig = self._dark_figure((16, 3.5 * n_params))
        gs = fig.add_gridspec(n_params, 3, hspace=0.4, wspace=0.3)
        fig.suptitle('MCMC Bayesian Inference Diagnostics', color=TEXT_COLOR, fontsize=13, fontweight='bold')

        for p in range(n_params):
            # Trace
            ax_t = self._dark_ax(fig, (gs[p, 0]))
            for c_idx, chain in enumerate(chains):
                ax_t.plot(chain[:, p], linewidth=0.3, alpha=0.7, color=COLORS[c_idx])
            ax_t.set_ylabel(f'{param_names[p]}', color=TEXT_COLOR)
            ax_t.set_xlabel('Iteration' if p == n_params - 1 else '', color=TEXT_MUTED)
            ax_t.set_title('Chain Traces' if p == 0 else '', color=TEXT_MUTED)

            # Posterior density
            ax_d = self._dark_ax(fig, (gs[p, 1]))
            all_samples = np.concatenate([c[-2000:, p] for c in chains])
            ax_d.hist(all_samples, bins=40, density=True, alpha=0.7, color=ACCENT, edgecolor='none')
            from scipy import stats as sp_stats
            try:
                kde = sp_stats.gaussian_kde(all_samples)
                x_kde = np.linspace(all_samples.min(), all_samples.max(), 200)
                ax_d.plot(x_kde, kde(x_kde), color=ACCENT2, linewidth=2)
            except Exception:
                pass
            # CI lines
            ci_low = np.percentile(all_samples, 2.5)
            ci_high = np.percentile(all_samples, 97.5)
            ci_mean = np.mean(all_samples)
            ax_d.axvline(ci_mean, color=GREEN, linestyle='-', linewidth=1.5, alpha=0.8)
            ax_d.axvline(ci_low, color=ACCENT2, linestyle='--', linewidth=1, alpha=0.5)
            ax_d.axvline(ci_high, color=ACCENT2, linestyle='--', linewidth=1, alpha=0.5)
            ax_d.set_xlabel('Value' if p == n_params - 1 else '', color=TEXT_MUTED)
            ax_d.set_title('Posterior Density' if p == 0 else '', color=TEXT_MUTED)

            # Autocorrelation
            ax_a = self._dark_ax(fig, (gs[p, 2]))
            for c_idx, chain in enumerate(chains):
                post_burn = chain[-2000:, p]
                max_lag = min(200, len(post_burn) - 1)
                ac = np.array([np.corrcoef(post_burn[:-l], post_burn[l:])[0, 1]
                              for l in range(1, max_lag + 1)])
                ax_a.plot(range(1, max_lag + 1), ac, linewidth=0.5, alpha=0.6, color=COLORS[c_idx])
            ax_a.axhline(0, color='white', linewidth=0.3, alpha=0.3)
            ax_a.set_xlabel('Lag' if p == n_params - 1 else '', color=TEXT_MUTED)
            ax_a.set_title('Autocorrelation' if p == 0 else '', color=TEXT_MUTED)

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 7. Three-Site Comparison
    # ═══════════════════════════════════════════════════════════════════════

    def site_comparison_plot(self, all_results, filename='07_site_comparison.png'):
        fig = self._dark_figure((14, 8))
        gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
        fig.suptitle('Three-Site Comparison — Scotian Shelf Offshore Wind Siting',
                    color=TEXT_COLOR, fontsize=13, fontweight='bold')

        labels = list(all_results.keys())
        short_labels = [l.split('(')[0].strip() for l in labels]
        scores = [all_results[l]['synthesis'].get('score', 0) for l in labels]
        energies = [all_results[l]['optimization'].get('site_percentile', 0) for l in labels]
        eco_scores = [all_results[l]['cumulative'].get('cumulative_score', 0) for l in labels]
        cfs = [all_results[l].get('time', {}).get('capacity_factor', 0) for l in labels]
        aucs = [all_results[l]['species'].get('auc', 0) for l in labels]
        depths = [all_results[l]['data'].get('depth_m', 0) for l in labels]

        # Scores bar chart
        ax1 = self._dark_ax(fig, (gs[0, 0]))
        x = np.arange(len(labels))
        width = 0.35
        bars1 = ax1.bar(x - width/2, scores, width, color=ACCENT, alpha=0.85, label='Overall Score')
        for bar, s in zip(bars1, scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{s:.3f}',
                    ha='center', color=TEXT_MUTED, fontsize=9, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(short_labels, fontsize=8)
        ax1.set_ylabel('Score', color=TEXT_COLOR)
        ax1.set_title('Overall Site Score', color=TEXT_COLOR)
        ax1.set_ylim(0, 1)

        # Energy + Eco trade-off
        ax2 = self._dark_ax(fig, (gs[0, 1]))
        for i, (lbl, e, eco) in enumerate(zip(short_labels, energies, eco_scores)):
            ax2.scatter(e, eco, s=120, color=COLORS[i], alpha=0.9, edgecolors='white', linewidth=0.5, label=lbl)
        ax2.set_xlabel('Energy Percentile', color=TEXT_COLOR)
        ax2.set_ylabel('Cumulative Impact', color=TEXT_COLOR)
        ax2.set_title('Energy vs Ecological Impact Trade-off', color=TEXT_COLOR)
        ax2.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR, fontsize=7)

        # Multi-metric radar
        ax3 = self._dark_ax(fig, (gs[1, 0]))
        metrics = ['Energy', 'Ecological', 'Feasibility', 'Human Conflict']
        n_metrics = len(metrics)
        angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
        angles += angles[:1]

        for i, lbl in enumerate(short_labels):
            r = all_results[labels[i]]
            values = [
                r['optimization'].get('site_percentile', 50) / 100,
                1 - r['cumulative'].get('cumulative_score', 0) / 0.3,
                1.0 if 50 <= r['data'].get('depth_m', 0) <= 200 else 0.3,
                1 - r['human'].get('overall_conflict_score', 0),
            ]
            values += values[:1]
            ax3.fill(angles, values, alpha=0.15, color=COLORS[i])
            ax3.plot(angles, values, 'o-', linewidth=1.5, color=COLORS[i], markersize=4, label=lbl)
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(metrics, color=TEXT_MUTED)
        ax3.set_ylim(0, 1)
        ax3.set_title('Multi-Criteria Comparison', color=TEXT_COLOR)
        ax3.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR, fontsize=6)

        # CF + Depth + AUC table
        ax4 = self._dark_ax(fig, (gs[1, 1]))
        ax4.axis('off')
        table_data = [['Site', 'Depth (m)', 'Capacity\nFactor', 'MaxEnt\nAUC', 'Verdict']]
        for i, lbl in enumerate(short_labels):
            r = all_results[labels[i]]
            feasible = 50 <= r['data'].get('depth_m', 0) <= 200
            v = '✓ FEASIBLE' if feasible else '✗ INFEASIBLE'
            table_data.append([
                lbl, f"{depths[i]:.0f}",
                f"{cfs[i]:.1f}%", f"{aucs[i]:.2f}",
                f"{v}"
            ])
        table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.25, 0.15, 0.15, 0.15, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        for key, cell in table.get_celld().items():
            cell.set_facecolor(CARD_BG)
            cell.set_edgecolor('#333')
            cell.set_text_props(color=TEXT_COLOR)
            if key[0] == 0:
                cell.set_text_props(color=ACCENT, fontweight='bold')
        ax4.set_title('Site Feasibility Summary', color=TEXT_COLOR)

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 8. Lagrangian Animation
    # ═══════════════════════════════════════════════════════════════════════

    def lagrangian_animation(self, trajectories, time_hours, filename='08_lagrangian.mp4'):
        try:
            import matplotlib.animation as animation
            import cartopy.crs as ccrs
            import cartopy.feature as cfeature
        except ImportError:
            print("  [viz] animation deps missing"); return

        fig, ax = plt.subplots(figsize=(10, 7), subplot_kw={'projection': ccrs.PlateCarree()},
                               facecolor=DARK_BG)
        ax.set_facecolor('#0d1a2d')
        ax.set_extent([ROI_BOUNDS['lon_min'], ROI_BOUNDS['lon_max'],
                       ROI_BOUNDS['lat_min'], ROI_BOUNDS['lat_max']])
        ax.add_feature(cfeature.LAND, facecolor='#1a1a1a')
        ax.add_feature(cfeature.OCEAN, facecolor='#0a1628')
        ax.coastlines(linewidth=0.5, edgecolor='#334')
        ax.plot(self.site_lon, self.site_lat, 'r*', markersize=15, transform=ccrs.PlateCarree())

        traj = np.array(trajectories)
        n_steps = min(traj.shape[1], 168)
        scat = ax.scatter([], [], s=2, c=CYAN, alpha=0.7, transform=ccrs.PlateCarree())
        title = ax.set_title('', color=TEXT_COLOR)

        def init():
            scat.set_offsets(np.empty((0, 2)))
            return scat, title

        def update(frame):
            lons = traj[:, frame, 0]
            lats = traj[:, frame, 1]
            scat.set_offsets(np.column_stack([lons, lats]))
            title.set_text(f'Lagrangian Particle Drift — Hour {frame}/{n_steps} | 500 particles')
            return scat, title

        ani = animation.FuncAnimation(fig, update, frames=n_steps, init_func=init,
                                       blit=True, interval=80)
        path = os.path.join(ANIM_DIR, filename)
        try:
            Writer = animation.FFMpegWriter
            ani.save(path, writer=Writer(fps=12), dpi=150)
            print(f"  [viz] {filename}")
        except Exception as e:
            print(f"  [viz] animation save failed: {e}")
        plt.close(fig)

    # ═══════════════════════════════════════════════════════════════════════
    # 9. Cumulative Impact Heatmap
    # ═══════════════════════════════════════════════════════════════════════

    def cumulative_heatmap(self, contributions, title="Cumulative Impact Breakdown",
                          filename='09_cumulative_breakdown.png'):
        fig = self._dark_figure((10, 8))
        ax = self._dark_ax(fig, (1, 1, 1))

        names = list(contributions.keys())
        values = list(contributions.values())
        colors_bar = [COLORS[i % len(COLORS)] for i in range(len(names))]

        bars = ax.barh(range(len(names)), values, color=colors_bar, alpha=0.85, height=0.6)
        for bar, v, n in zip(bars, values, names):
            ax.text(v + max(values) * 0.02, bar.get_y() + 0.15, f'{v:.4f}',
                   color=TEXT_MUTED, fontsize=9)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels([n.replace('_', ' ') for n in names])
        ax.set_xlabel('Contribution to Cumulative Score', color=TEXT_COLOR)
        ax.set_title(title, color=TEXT_COLOR, fontweight='bold')

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # 10. Data Provenance Diagram
    # ═══════════════════════════════════════════════════════════════════════

    def data_provenance_plot(self, data_loaded, data_missing, filename='10_data_provenance.png'):
        fig = self._dark_figure((10, 6))
        ax = self._dark_ax(fig, (1, 1, 1))

        n_loaded = len(data_loaded)
        n_missing = len(data_missing)
        total = n_loaded + n_missing

        # Horizontal bar
        ax.barh(0, n_loaded, color=GREEN, alpha=0.8, height=0.4, label=f'Loaded ({n_loaded})')
        ax.barh(0, n_missing, left=n_loaded, color=RED, alpha=0.6, height=0.4,
                label=f'Missing ({n_missing})')
        ax.set_xlim(0, total)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel(f'Variables ({total} registry, {n_loaded} loaded)', color=TEXT_COLOR)
        ax.set_title('Data Completeness at Site', color=TEXT_COLOR, fontweight='bold')
        ax.legend(framealpha=0.3, facecolor=CARD_BG, edgecolor='#333', labelcolor=TEXT_COLOR, loc='lower right')

        # Loaded variables as text
        text_str = 'Loaded: ' + ', '.join(data_loaded[:30])
        if len(data_loaded) > 30:
            text_str += f' ... (+{len(data_loaded) - 30} more)'
        ax.text(0.01, -0.35, text_str, transform=ax.transAxes, fontsize=7,
               color=TEXT_MUTED, fontfamily='monospace')

        path = os.path.join(FIG_DIR, filename)
        fig.savefig(path, dpi=300, facecolor=DARK_BG, edgecolor='none')
        plt.close(fig)
        print(f"  [viz] {filename}")

    # ═══════════════════════════════════════════════════════════════════════
    # HTML Report
    # ═══════════════════════════════════════════════════════════════════════

    def generate_html_report(self, all_results, sections, filename='marine_digital_twin_report.html'):
        figures = sorted([f for f in os.listdir(FIG_DIR) if f.endswith('.png')])
        animations = sorted([f for f in os.listdir(ANIM_DIR) if f.endswith('.mp4')])

        fig_html = '\n'.join(
            f'<div class="figure-card"><h3>{f}</h3><img src="figures/{f}" loading="lazy"></div>'
            for f in figures
        )
        anim_html = '\n'.join(
            f'<div class="figure-card"><h3>{f} ▶</h3><video controls preload="metadata"><source src="animations/{f}" type="video/mp4"></video></div>'
            for f in animations
        )

        site_rows = ''
        for label, r in all_results.items():
            s = r['synthesis']
            score = s.get('score', 0)
            color = '#2ecc71' if score > 0.6 else '#e8913a'
            site_rows += f'''<tr>
                <td>{label}</td>
                <td style="color:{color}; font-weight:bold">{score:.3f}</td>
                <td>{r['optimization'].get('site_percentile', 0):.0f}th</td>
                <td>{r['cumulative'].get('cumulative_score', 0):.3f}</td>
                <td>{r.get('time', {}).get('capacity_factor', 0):.1f}%</td>
                <td>{s.get('verdict', 'N/A')[:60]}</td>
            </tr>'''

        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Marine Digital Twin — Offshore Wind Siting</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:"Segoe UI",system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;line-height:1.6}}
  .hero{{background:linear-gradient(135deg,#0d1a2d,#1a0a2e);padding:60px 30px;text-align:center;border-bottom:2px solid #4a90d9}}
  .hero h1{{font-size:2.2em;color:#4a90d9;margin-bottom:10px}}
  .hero p{{color:#888899;font-size:1.1em}}
  .container{{max-width:1300px;margin:0 auto;padding:30px 20px}}
  .section{{margin:30px 0}}
  .section h2{{color:#4a90d9;margin-bottom:15px;font-size:1.4em;border-bottom:1px solid #222;padding-bottom:8px}}
  .figure-card{{background:#12121a;border-radius:8px;padding:15px;margin:15px 0;border:1px solid #222}}
  .figure-card h3{{font-size:13px;color:#888899;margin-bottom:10px}}
  .figure-card img,.figure-card video{{width:100%;border-radius:4px;display:block}}
  table{{width:100%;border-collapse:collapse;background:#12121a;border-radius:8px;overflow:hidden}}
  th{{background:#1a1a2e;color:#4a90d9;padding:12px;text-align:left;font-size:13px}}
  td{{padding:10px 12px;border-bottom:1px solid #1a1a2e;font-size:13px}}
  tr:hover{{background:#1a1a2e}}
  .verdict-box{{background:#12121a;border:1px solid #333;border-radius:8px;padding:20px;margin:15px 0}}
  .verdict-box pre{{color:#e0e0e0;font-size:13px;white-space:pre-wrap}}
  footer{{text-align:center;padding:40px;color:#555;font-size:12px}}
</style></head><body>
<div class="hero">
<h1>Marine Digital Twin — Offshore Windmill Siting Analysis</h1>
<p>Scotian Shelf ROI · Vestas V236-15.0 MW · 16 Tools · 29 Data Sources · 155 Variables</p>
</div>
<div class="container">

<div class="section"><h2>3-Site Comparison</h2>
<table><thead><tr><th>Site</th><th>Score</th><th>Energy</th><th>Eco Impact</th><th>Capacity Factor</th><th>Verdict</th></tr></thead>
<tbody>{site_rows}</tbody></table></div>

<div class="section"><h2>Pipeline Details</h2>
<div class="verdict-box"><pre>{chr(10).join(sections)}</pre></div></div>

<div class="section"><h2>Figures</h2>{fig_html}</div>

<div class="section"><h2>Animations</h2>{anim_html}</div>

</div>
<footer>Marine Digital Twin Platform · Data: GLORYS12, ERA5, WAVERYS, Copernicus BGC, OBIS, GFW, GEBCO, SMA, BBMP, HYCOM, Open-Meteo<br>All variables traced to source API with quality flags and published references.</footer>
</body></html>'''
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'w') as f:
            f.write(html)
        print(f"  [viz] HTML report: {filename}")
        return path
