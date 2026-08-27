""" Plotting the spatial photocurrent and phase maps and 1D linecuts """

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def generate_automatic_ticks(max_value: float, nticks: int) -> np.ndarray:
    """ Generates evenly spaced axis tick locations on both axes. """
    raw_step = max_value / (nticks-1)
    nice_steps = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 5, 7, 8, 10, 15, 20, 30, 40, 50, 
                           60, 70, 80, 90, 100])
    step = nice_steps[np.argmin(np.abs(nice_steps - raw_step))]
    ticks = np.arange(0, max_value + step, step)
    if len(ticks) > nticks:
        idx = np.linspace(0, len(ticks) - 1, nticks).astype(int)
        ticks = ticks[idx]
    return ticks

def build_output_filename(meta:Dict[str, Any], plot_type: str, extra: str="")->str:
    """ Generates standardized output filenames using extracted metadata. """
    parts = [meta["date & time"], meta["wavelength"], meta["power"], meta["polarity"], 
             meta["frequency"], plot_type]
    if extra: 
        parts.append(extra)
    filtered_parts = [p for p in parts if p]
    return "_".join(filtered_parts) + ".pdf"

def plot_spatial_map(data: np.ndarray, scale_x: float, scale_y: float,
                     is_photocurrent: bool = True, 
                     annotations: Optional[List[Tuple[float, float, str, float, float]]] = None,
                     output_path: str = None) -> None:
    """
    Plots the spatial heatmap with micron scale axes with optional annotations.
    """
    plt.figure()
    im = plt.imshow(data, cmap="inferno", origin="lower", aspect = data.shape[0] / data.shape[1])#, vmin = 0, vmax=12)
    
    label = r"$I_{ph}$ [pA]" if is_photocurrent else r"$\varphi$ [°]"
    cbar = plt.colorbar(im, label=label, pad = 0.03, fraction = 0.04, aspect = 30)
    cbar.locator = MaxNLocator(nbins=5)
    cbar.update_ticks()
    
    plt.xlabel(r"$x$ [$\mu$m]")
    plt.ylabel(r"$y$ [$\mu$m]")
    
    ax=plt.gca()
    total_microns_x = data.shape[1]*scale_x
    total_microns_y = data.shape[0]*scale_y
    
    ticks_um_x = generate_automatic_ticks(total_microns_x, nticks=5)
    ticks_px_x = ticks_um_x/scale_x
    ax.set_xticks(ticks_px_x)
    ax.set_xticklabels([f"{int(v)}" if v>= 10 else f"{v:.1f}" for v in ticks_um_x])
    
    ticks_um_y = generate_automatic_ticks(total_microns_y, nticks=5)
    ticks_px_y = ticks_um_y/scale_y
    ax.set_yticks(ticks_px_y)
    ax.set_yticklabels([f"{int(v)}" if v>= 10 else f"{v:.0f}" for v in ticks_um_y])
    
    ax.set_xlim(-0.5, data.shape[1]-0.5)
    ax.set_ylim(-0.5, data.shape[0]-0.5)
    plt.tight_layout() #not needed if layout="constraint" is present
    
    # Dynamic annotations (Circles + Arrows)
    if annotations:
        for x_um, y_um, text_label, offset_x, offset_y in annotations:
            px_x = x_um / scale_x
            px_y = y_um / scale_y
            ax.annotate(
                text_label,
                xy=(px_x, px_y),
                xytext=(offset_x, offset_y),
                textcoords="offset points",
                color="white",
                fontsize=18,
                ha="center",
                va="center_baseline",
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="white", lw=1.5),
                bbox=dict(boxstyle="circle,pad=0.25", fc="black", alpha=0.5, ec="none")
            )
    
    if output_path:
        plt.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.show()
    
    
def plot_linecuts(x_um: np.ndarray, linecuts_data: List[Dict[str, Any]], 
    is_photocurrent: bool = True, output_path: Optional[str] = None) -> None:
    """Plots 1D linecut profiles across specified pixel rows."""
    plt.figure()
    for item in linecuts_data:
        #item consists of: {"y_slice": array, "label": str, "color": str}
        plt.plot(x_um, item["y_slice"], color=item["color"], label=item["label"])
        
    ylabel = r"$I_{ph}$ [pA]" if is_photocurrent else r"$\varphi$ [°]"
    plt.ylabel(ylabel)
    plt.xlabel(r"$x$ [$\mu$m]")
    plt.legend(loc="best", frameon=False)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.show()
    
    
