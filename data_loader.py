"Extracting filename metadata and extracting the data from the files"

import os
from typing import Dict, Any, Tuple
import numpy as np
import re

def filename_metadata(filepath: str) -> Dict[str, str]:
    """ Extracts experimental parameters (wavelength, laser power, bias, date, 
    laser motor position, chopper freq/laser trigger freq) from the filename 
    
    Example filename:
        "11.11.2011_8.45_D5GR2_112p0uW_10e9A_405nm_P60V_295Hz_longscan_lockin_R.txt"
    """ 
    filename = os.path.basename(filepath)
    
    date = re.search(r"\d{2}\.\d{2}\.\d{4}\_\d+\.\d{2}", filename)
    wavelength = re.search(r"\d{3}nm", filename)
    power = re.search(r"\d+[p.]?\d*[u|m|]?W", filename)
    polarity = re.search(r"[P|M]\d+V", filename)
    frequency = re.search(r"\d+Hz", filename)
    
    
    return {
        "date & time" : date.group(0) if date else None,
        "wavelength" :  wavelength.group(0) if wavelength else None,
        "power" :       power.group(0) if power else None,
        "polarity" :    polarity.group(0) if polarity else None,
        "frequency" :   frequency.group(0) if frequency else None,
        "is_phase" :    "lockin_phase" in filename,
        "is_r" :        "lockin_R" in filename,
        }

def load_scan_file(filepath: str, amplifier_gain: float = 1e9) -> Tuple[np.ndarray, Dict[str, Any]]:
    """ Loads scan data file and parses coordinates, metadata and numerical matrix
    
    Returns:
        npdata: 2D Numpy array of spatial measurement points
        scan_info: dictionary containing physical dimensions and scale factors
    """
    
    with open(filepath, "r") as f:
        raw_data = f.read()
        
    """ Now the raw_data are going to be sliced into separate section, as per the nature
    of the measurement files"""
    sections = raw_data.split("-------------------------------------------------------------------")
    coordinates = sections[1]
    data_section = sections[-1].strip()
    
    data=[]
    for line in data_section.splitlines():
        try:
            data.append(list(map(float, line.split())))
        except ValueError:
            continue
    
    npdata = np.array(data)
    
    x_start = float(coordinates[15:24])
    y_start = float(coordinates[42:50])
    x_end = float(coordinates[67:75])
    y_end = float(coordinates[92:100])
    x_pixels = float(coordinates[114:118])
    y_pixels = float(coordinates[128:132])
    
    scale_x = (x_end - x_start)/x_pixels
    scale_y = (y_end - y_start)/y_pixels
    
    if "lockin_R" in filepath:
        npdata = (npdata/amplifier_gain)*1e12 #converts to picoampers (pA) from amp gained data
        
    scan_info = {
        "x_start": x_start, "x_end": x_end, "x_pixels": x_pixels,
        "y_start": y_start, "y_end": y_end, "y_pixels": y_pixels,
        "scale_x": scale_x, "scale_y": scale_y,
        }
    return npdata, scan_info





