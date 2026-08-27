""" Fitting functions and spatial signal processing """

import numpy as np
from scipy.ndimage import median_filter as scipy_median_filter
from scipy.optimize import curve_fit
from typing import Tuple, List
from matplotlib.legend_handler import HandlerTuple
import matplotlib.lines as mlines
import matplotlib.pyplot as plt

def gauss(x:np.ndarray, i0: float, a:float, x0: float, sigma: float) -> np.ndarray:
    """ 1D Gaussian profile function for photocurrent hotspot size analysis """
    return i0 + a*np.exp(-((x-x0)**2)/(2*sigma**2))

def local_median_filter(data: np.ndarray, x:np.ndarray, y:np.ndarray, 
                        regions:List[Tuple[float, float, float, float, int]])-> np.ndarray:
    """ Applies region-specific median filtering to spatially resolved data 
    to account the electrical noise locally"""
    filtered = data.copy()
    
    """ This is to adress the fact, that the x,y array are not relative
    positions ([0, ..., 250]), but rather an absolute values of positions of 
    movable XY stand ([2100, ...., 2250]).
    
    However, when applying the median filtering after seeing the plot, the coordinates 
    of the figure are relative (this is calculated in another code section) 
    and the defined regions are therefore more practical to be in those relative coordinates.
    
    This is accounted for by the following for loop.
    """
    for xmin, xmax, ymin, ymax, size in regions:
        if xmin != np.min(x) and xmax != np.max(x):
            xmin += np.min(x)   #For example: xmin = 15 (from region), np.min(x) = 21500
            xmax += np.min(x)
        if ymin != np.min(y) and ymax != np.max(y):
            ymin += np.min(y)
            ymax += np.min(y)
        
        mask_x = (x >= xmin) & (x <= xmax)
        mask_y = (y >= ymin) & (y <= ymax)
        ix, iy = np.where(mask_x)[0], np.where(mask_y)[0]
        
        if len(ix) == 0 or len(iy) == 0:
            continue
        
        sub = data[np.ix_(iy, ix)] #creates the masked data for filtering
        filtered[np.ix_(iy, ix)] = scipy_median_filter(sub, size=size)
        
    return filtered #returns fitered data in absolute coordinates

def fit_photocurrent_peak(x_um:np.ndarray, signal:np.ndarray, p0: List[float],
                          bounds: Tuple[List[float], List[float]]) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """ Fits a Gaussian profile to photocurrent linecuts and calculates FWHM with errors """
    popt, pcov = curve_fit(gauss, x_um, signal, p0=p0, bounds=bounds)
    perr = np.sqrt(np.diag(pcov))
    
    sigma_fit = popt[3]
    fwhm = 2*np.sqrt(2*np.log(2))*sigma_fit
    fwhm_err = 2*np.sqrt(2*np.log(2))*perr[3]
    
    return popt, perr, fwhm, fwhm_err

def plot_peak_fits(x_data: np.ndarray, peaks_dict: List[Dict[str, Any]],
    fwhm: Optional[float] = None, fwhm_err: Optional[float] = None, 
    output_path: Optional[str] = None) -> None:
    """
    Plots isolated peaks alongside their Gaussian fit curves.
    """
    plt.figure()
    handles = []
    labels = []

    for item in peaks_dict:
        #Plot raw data scatter points on the axes
        #Use item["x_masked"] if provided, otherwise fall back to x_data
        x_pts = item.get("x_masked", x_data)
        dot, = plt.plot(
            x_pts, 
            item["peak_raw"], 
            color=item["color_dot"], 
            marker="o", 
            linestyle="None"
        )
        
        #Plot smooth Gaussian fit line on the axes
        fit_line, = plt.plot(
            item["x_dense"], 
            item["fit_curve"], 
            color=item["color_line"], 
            linestyle="--"
        )
        
        #plot the fwhm annotation (uncomment if needed)
        if fwhm is not None and fwhm_err is not None:
            plt.annotate(
                rf"FWHM = {fwhm:.2f} $\pm$ {fwhm_err:.2f} $\mu$m", 
                xy=(90, 3),
                xytext=(-110, -50),                        
                textcoords="offset points",
                )
        
        #Combine both markers into a single legend entry
        handles.append((dot, fit_line))
        labels.append(item["label"])

    plt.ylabel(r"$I_{ph}$ [pA]")
    plt.xlabel(r"$x$ [$\mu$m]")
    
    leg = plt.legend(
        handles,
        labels,
        handler_map={tuple: HandlerTuple(ndivide=None)},
        frameon=False,
        loc="upper right"
    )
    
    # Slight legend text offset alignment
    for text in leg.get_texts():
        text.set_position((0, 3))

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.show()




