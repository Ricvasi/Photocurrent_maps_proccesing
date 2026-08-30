# Photocurrent and phase maps processing

Python pipeline for loading, median filtering, and plotting 2D spatial photocurrent ($I_{ph}$) and phase ($\varphi$) maps, featuring background subtraction and Gaussian peak fitting for 1D linecut analysis.


## Representative outputs

### Photocurrent map with annotation, 1D hotspot linecut and isolated hotspot peak Gaussian fit
<img width="400" height="300" alt="Photocurrent_map_with_annotation" src="https://github.com/user-attachments/assets/ed1150bc-903e-4ea0-a423-65c82f097ad0" />
<img width="400" height="300" alt="1D_linecut_of_photocurrent_hotspot" src="https://github.com/user-attachments/assets/dbf6f9a8-d2e9-4bcc-ab3c-9bb3a194b0f6" />
<img width="400" height="300" alt="isolated_hotspot_peak_gauss_peak" src="https://github.com/user-attachments/assets/75384517-adb6-4162-be58-1727f347a15c" />

### Phase map without and with median filtering
<img width="400" height="300" alt="Phase_map" src="https://github.com/user-attachments/assets/02980c23-615e-409b-b261-49cb5b31a531" />
<img width="400" height="300" alt="Phase_map_median_filtered" src="https://github.com/user-attachments/assets/00d2ad86-078d-4bb8-b95c-82537621554c" />

---

## Features

- **2D spatial heatmaps:** Automated scaling ($\mu\text{m}$ coordinates), aspect ratio locking, and dynamic annotation overlays.
- **Signal Processing:** Interactive median filtering for electrical noise spikes removal and linecut background subtraction.
- **Gaussian Peak Fitting:** Curve fitting via `scipy.optimize.curve_fit` with FWHM calculation and custom dual-marker legend handles.
- **Publication Ready:** Automatic high-DPI export (`dpi=600`) with constrained layout formatting perfect for publication-ready figures.

---
## Code structure 




---
## Repository structure

```text
├── config.py                 # File paths, scan geometry, and plotting configuration
├── main.py                   # Main execution pipeline
├── src/
│   ├── data_loader.py        # Raw data loading and parsing routines
│   ├── interactive_median.py # Electrical spike removal filtering tools
│   ├── plotting.py           # 2D heatmap and annotation rendering
│   └── signal_processing.py  # Gaussian fitting routines and peak plotting
├── data/                     # Sample measurement files
└── figures/                    # Representative figures of each major code feature

