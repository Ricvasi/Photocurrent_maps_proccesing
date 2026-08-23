""" Fitting functions and spatial signal processing """

import numpy as np
from scipy.ndimpage import median_filter as scipy_median_filter
from scipy.optimize import curve_fit
from typing import Tuple, List

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
        
        sub = data[np.ix(iy, ix)] #creates the masked data for filtering
        filtered[np.ix_(iy, ix)] = scipy_median_filter(sub, size=size)
        
    return filtered #returns fitered data in absolute coordinates

def fit_photocurrent_peak(x_um:np.ndarray, signal:np.ndarray, p0: List[float],
                          bounds: Tuple[List[float], List[float]]) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """ Fits a Gaussian profile to photocurrent linecuts and calculates FWHM with errors """
    popt, pcov = curve_fit(gaussian, x_um, signal, p0=p0, bounds=bounds)
    perr = np.sqrt(np.diag(pcov))
    
    sigma_fit = popt[3]
    fwhm = 2*np.sqrt(2*np.log(2))*sigma_fit
    fwhm_err = 2*np.sqrt(2*np.log(2))*perr[3]
    
    return popt, perr, fwhm, fwhm_err






