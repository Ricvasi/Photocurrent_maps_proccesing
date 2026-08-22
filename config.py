""" Visualization configuration for for Matplotlib and Latex formatting """

import matplotlib.pyplot as plt

def plot_style() -> None:
    """ Configurates global Matplotlib parameters for publication-ready unified figures """
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman"],

        "figure.figsize": (5.5, 4.5),

        "axes.titlesize": 22,
        "axes.labelsize": 21,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 17,
        
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.top": False,
        "ytick.right": False,    
        "legend.frameon": False,
        
        "axes.linewidth": 1.2,
        "lines.linewidth": 2,
        })