# Photocurrent_and_phase_maps_processing

Python pipeline for loading, median filtering, and plotting 2D spatial photocurrent ($I_{ph}$) and phase ($\varphi$) maps, featuring background subtraction and Gaussian peak fitting for 1D linecut analysis.


## Representative outputs

## Features

- **2D spatial heatmaps:** Automated scaling ($\mu\text{m}$ coordinates), aspect ratio locking, and dynamic annotation overlays.
- **Signal Processing:** Interactive median filtering for electrical noise spikes removal and linecut background subtraction.
- **Gaussian Peak Fitting:** Curve fitting via `scipy.optimize.curve_fit` with FWHM calculation and custom dual-marker legend handles.
- **Publication Ready:** Automatic high-DPI export (`dpi=600`) with constrained layout formatting perfect for publication-ready figures.

---

## Repository Structure

```text
├── config.py                 # File paths, scan geometry, and plotting configuration
├── main.py                   # Main execution pipeline
├── src/
│   ├── data_loader.py        # Raw data loading and parsing routines
│   ├── interactive_median.py # Spike removal filtering tools
│   ├── plotting.py           # 2D heatmap & annotation rendering
│   └── signal_processing.py  # Gaussian fitting routines & peak plotting
├── data/                     # Sample measurement files
└── media/                    # Figures for documentation

