"""Main script to run the data processing and visualization """

import os
import numpy as np
from config import plot_style
from src.data_loader import load_scan_file
from src.plotting import plot_spatial_map, plot_linecuts, build_output_filename
from src.interactive_median_filter import interactive_median_filter

def main():
    plot_style() #figure styling

    #setup paths
    data_dir = "/home/ricvasi/Desktop/MATFYZ/bakalárka/new_contacts/20251127vasilega_9_14device"
    output_dir = "/home/ricvasi/Desktop/MATFYZ/bakalárka/whole_of_code_finalized_version/test"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = "27.11.2025_12.30_D5GR2_26p0uW_10e9A_355nm_P60V_longscan_lockin_R.txt"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}. Please ensure sample data is placed in data/raw/")
        return

    #load data
    npdata, scan_info, meta = load_scan_file(filepath)
    
    #-------------------------------------------------
    #Interactive median filtering (uncomment to use)
    #npdata = interactive_median_filter(npdata, scan_info["x_vec"], scan_info["y_vec"])
    
    #-------------------------------------------------
    #Spatial map plot
    enable_spatial_plot = False
    if enable_spatial_plot:
        #annotations format: [(x_um, y_um, "Label", offset_x, offset_y)]
        #uncommect to use:
        annotations = None#[(153, 210, "A", -35, -35)]
        
        plot_type = "photocurrent" if meta["is_r"] else "phase"
        #use extra to put additional info (linecuts, filtered, etc.)
        out_name = build_output_filename(meta, plot_type, extra="annot")
        out_path = os.path.join(output_dir, out_name)
        
        plot_spatial_map(
            data = npdata, 
            scale_x = scan_info["scale_x"],
            scale_y = scan_info["scale_y"],
            is_photocurrent = meta["is_r"],
            annotations = annotations,
            output_path = out_path
            )
    
    #--------------------------------------------------------
    #Linecut analysis
    enable_linecuts = False
    if enable_linecuts:
        x_um = np.arange(npdata.shape[1])*scan_info["scale_x"]
        
        #select pixel rows for linecuts
        y_idx1, y_idx2 = 35, 36
        linecuts_payload = [
            {"y_slice": npdata[y_idx1], "label": f"Point A", "color": "#d31f11"},
            {"y_slice": npdata[y_idx2], "label": f"Ref", "color": "#f47a00"},
        ]
        
        out_name_linecut = build_output_filename(meta, "linecut", extra=f"y{y_idx1}_{y_idx2}")
        out_path_linecut = os.path.join(output_dir, out_name_linecut)

        plot_linecuts(
            x_um=x_um,
            linecuts_data=linecuts_payload,
            is_photocurrent=meta["is_r"],
            output_path=out_path_linecut
        )
    
    #-----------------------------------------------------------
    #Gaussian peak fitting and fwhm extraction
    enable_gauss_fit = False 
    if enable_gauss_fit:
        from src.signal_processing import fit_photocurrent_peak
        from src.signal_processing import plot_peak_fits

        x_um = np.arange(npdata.shape[1]) * scan_info["scale_x"]
        
        #Isolate peak by subtracting adjacent row (background subtraction)
        y_idx = 36
        peak_isolated = npdata[y_idx] - npdata[y_idx + 1]

        #Define spatial mask around hotspot (e.g., between 75 um and 115 um)
        mask = (x_um >= 75) & (x_um <= 115)
        x_masked = x_um[mask]
        peak_masked = peak_isolated[mask]

        #Fit Gaussian: initial guess [i0, A, x0, sigma] & bounds
        p0 = [0.0, 4.4, 94.0, 1.5]
        bounds = ([-0.1, 0.0, 93.0, 0.5], [0.1, 4.7, 96.0, 5.0])

        popt, perr, fwhm, fwhm_err = fit_photocurrent_peak(
            x_um=x_masked, 
            signal=peak_masked, 
            p0=p0, 
            bounds=bounds
        )

        print(f"Fit Results:")
        print(f"  Center (x0) = {popt[2]:.2f} ± {perr[2]:.2f} µm")
        print(f"  FWHM        = {fwhm:.2f} ± {fwhm_err:.2f} µm")

        #Generate fine evaluation grid for smooth plotting
        x_dense = np.linspace(75, 115, 1000)
        from src.signal_processing import gauss
        fit_curve = gauss(x_dense, *popt)

        peaks_payload = [{
            "x_masked": x_masked,
            "x_dense": x_dense,
            "peak_raw": peak_masked,
            "fit_curve": fit_curve,
            "label": r"$+60$ V, point A",
            "color_dot": "#d31f11",
            "color_line": "#f47a00"
        }]

        out_name_fit = build_output_filename(meta, "gauss_fit", extra=f"row{y_idx}")
        out_path_fit = os.path.join(output_dir, out_name_fit)

        plot_peak_fits(
            x_data=x_masked,
            peaks_dict=peaks_payload,
            output_path=out_path_fit
        )
        
if __name__ == "__main__":
    main()
