""" Interactive median filtering method """

import numpy as np
import matplotlib.pyplot as plt

from typing import List, Tuple
from scipy.ndimage import median_filter as scipy_median_filter

from matplotlib.widgets import RectangleSelector, Button, RadioButtons
from matplotlib.patches import Rectangle

def apply_median_region(data:np.ndarray, x:np.ndarray, y:np.ndarray, 
        region:Tuple[float, float, float, float, int])-> np.ndarray:
    
    """ Takes in the whole data and the region you want to filter with the size 
    of the median filtering and returns the filtered data. 
    
    It also takes into account the fact, that the region that is given for filtering 
    is in relative coordinates (0-150 um for example), but the data itself are
    in absolute coordinates (for example x = 21500 um).
    
    The function returns filtered data with the absolute coordinates, as those
    are being proccesed into relative coordinates in a separate parts of code."""
    
    xmin, xmax, ymin, ymax, size = region
    filtered = data.copy()
    xmin += np.min(x)
    xmax += np.min(x)
    ymin += np.min(y)
    ymax += np.min(y)
    
    mask_x = (x >= xmin) & (x <= xmax)
    mask_y = (y >= ymin) & (y <= ymax)
    
    ix = np.where(mask_x)[0]
    iy = np.where(mask_y)[0]
    
    if len(ix) == 0 or len(iy) == 0:
        return filtered
    
    sub = data[np.ix_(iy, ix)]
    filtered[np.ix_(iy, ix)] = scipy_median_filter(sub, size=size)
    
    return filtered


def interactive_median_filter(data: np.ndarray, x: np.ndarray, 
        y: np.ndarray) -> np.ndarray:
    """
    Interactive local median filtering of a spatial map.

    The workflow is working as follows
    --------
    1. The function will print a figure from the given data upon calling.
    2. You can then select a rectangular region with the mouse that needs filtering.
    3. You the select the median-filter size.
    4. Press Apply, that will actually perform the median filtering.
    5. Repeat the process for additional regions and different median-filter sizes.
    6. Use Undo if you want to revert the filtering of the last region.
       Use Reset if you want to start all over again.
       Use Original if you want to see, how the figure looked at the beggining and
       use Filtered to return back to the filtered figure.
    7. Press OK to finish.
    """

    """ This part focuses on loading initial data and setting up the initial parameters """
    original = data.copy() #this will keep the original data to get back to

    regions = [] #list of applied regions, each region contains (xmin, xmax, ymin, ymax, filter_size)

    region_patches = [] #Graphical rectangles corresponding to applied regions

    selected_rectangle = None #Currently selected rectangle region

    selection_patch = None #Graphical representation of currently selected rectangle

    selected_size = 5 #Currently selected filter size

    showing_original = False #Is true when the original data are showing


    """ This part focuses on creating an initial figure """

    fig = plt.figure(figsize=(11, 8))

    # Main plotting area - needed to create space for the buttons
    ax = fig.add_axes([
        0.08,   # left
        0.20,   # bottom
        0.88,   # width
        0.74    # height
    ])

    # Relative coordinates used for the regions selection
    x_relative = x - np.min(x)
    y_relative = y - np.min(y)

    image = ax.imshow(
        original,
        extent=[
            x_relative.min(),
            x_relative.max(),
            y_relative.min(),
            y_relative.max()
        ],
        origin="lower",
        aspect="auto",
        cmap="inferno"
    )

    ax.set_xlabel("x [µm]")
    ax.set_ylabel("y [µm]")

    ax.set_title("Interactive local median filtering tool")


    def calculate_filtered_data():
        """
        This function recalculates the complete filtered dataset
        starting from the original data and applying all currently stored regions.
        """
        
        filtered = original.copy()

        for region in regions:
            filtered = apply_median_region(
                filtered,
                x,
                y,
                region
            )

        return filtered

    def update_image():
        """
        This recalculates and displays the currently filtered image.
        """

        nonlocal showing_original

        filtered = calculate_filtered_data() #recalculates for all current regions

        if not showing_original: #this will update only if we are currently showing filtered figure
            image.set_data(filtered)

        fig.canvas.draw_idle() #and draws all the filtered regions

    def on_select(eclick, erelease):
        """
        This function converts the clicks on the figure to the actuall stored 
        coordinates for filtering regions.
        """
        nonlocal selected_rectangle
        nonlocal selection_patch

        #mouse clicks check
        if (
            eclick.xdata is None
            or eclick.ydata is None
            or erelease.xdata is None
            or erelease.ydata is None
        ):
            return

        #Now for the coordinate loading
        xmin = min(eclick.xdata, erelease.xdata)
        xmax = max(eclick.xdata, erelease.xdata)
        ymin = min(eclick.ydata, erelease.ydata)
        ymax = max(eclick.ydata, erelease.ydata)

        selected_rectangle = (xmin, xmax, ymin, ymax)

        # Remove previous temporary selection
        if selection_patch is not None:
            selection_patch.remove()

        # Draw new temporary selection to see what was filtered
        selection_patch = Rectangle(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            fill=False,
            linewidth=2
        )

        ax.add_patch(selection_patch)

        print("\nSelected rectangle:")
        print(f"x: {xmin:.2f} → {xmax:.2f}")
        print(f"y: {ymin:.2f} → {ymax:.2f}")

        fig.canvas.draw_idle()

    def select_size(label):
        """
        This selects the filtering size using buttons, that will be introduced 
        later in the code.
        """

        nonlocal selected_size

        selected_size = int(label)

        print(f"Selected filter size: "
            f"{selected_size}")

    def apply_region(event):
        """
        This will add the selected region to the median filtering region 
        and allow for filtering to happen after the apply button clicks.
        """

        nonlocal selected_rectangle
        nonlocal selection_patch

        if selected_rectangle is None:
            print("No rectangle selected.")
            return

        xmin, xmax, ymin, ymax = selected_rectangle

        #Create a complete region tuple
        region = (xmin, xmax, ymin, ymax, selected_size)

        #Store the region to agreed to by pressing apply
        regions.append(region)

        #Create a permanent visual rectangle
        patch = Rectangle(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            fill=False,
            linewidth=2
        )

        ax.add_patch(patch)

        region_patches.append(patch)

        print("\nApplied region:")
        print(f"x: {xmin:.2f} → {xmax:.2f}")
        print(f"y: {ymin:.2f} → {ymax:.2f}")
        print(f"Median filter size: "
            f"{selected_size}")

        # Remove temporary selection
        if selection_patch is not None:
            selection_patch.remove()
            selection_patch = None

        selected_rectangle = None

        #Making sure we are showing filtered data
        showing_original = False

        update_image()

    def undo(event):
        """
        This function deletes the filtering of the last region and returns
        to the original data by clicking undo button.
        """

        nonlocal showing_original

        if len(regions) == 0:
            print("Nothing to undo.")
            return

        #Remove the last region
        removed_region = regions.pop()

        #Remove corresponding visual rectangle
        patch = region_patches.pop()
        patch.remove()

        print("\nRemoved region:")
        print(removed_region)

        showing_original = False

        update_image()

    def reset(event):
        """
        This functions deletes all the filtered regions and returns the figure
        to is original stat by clicking the reset button.
        """

        nonlocal selected_rectangle
        nonlocal selection_patch
        nonlocal showing_original

        #Remove all applied regions
        regions.clear()

        #Remove all graphical region patches
        for patch in region_patches:
            patch.remove()

        region_patches.clear()

        # Remove temporary selection
        if selection_patch is not None:
            selection_patch.remove()
            selection_patch = None

        selected_rectangle = None

        showing_original = False

        #Restore original image
        image.set_data(original)

        fig.canvas.draw_idle()

        print("\nAll filtering reset.")

    def show_original(event):
        """
        This function shows an original unfiltered figure as a comparison
        to the already filtered one without deleting the filtered regions
        by clicking the original button.
        """

        nonlocal showing_original

        showing_original = True

        image.set_data(original)

        fig.canvas.draw_idle()

        print("\nShowing original data.")

    def show_filtered(event):
        """
        This function will return the figure back to the filtered version after
        the original button was clicked.
        """

        nonlocal showing_original

        showing_original = False

        filtered = calculate_filtered_data()

        image.set_data(filtered)

        fig.canvas.draw_idle()

        print("\nShowing filtered data.")

    def clear_selection(event):
        """
        This will clear the current selected region by pressing the clear button.
        """

        nonlocal selected_rectangle
        nonlocal selection_patch

        if selection_patch is not None:
            selection_patch.remove()
            selection_patch = None

        selected_rectangle = None

        fig.canvas.draw_idle()

        print("\nCurrent selection cleared.")

    def print_regions(event):
        """
        This will print out the filtered regions by pressing the regions button.
        """
        if len(regions) == 0:
            print("\nNo regions have been applied.")
            return

        print("\nApplied regions:")
        for i, region in enumerate(regions,start=1):
            xmin, xmax, ymin, ymax, size = region
            print(
                f"{i}: "
                f"x={xmin:.2f}–{xmax:.2f}, "
                f"y={ymin:.2f}–{ymax:.2f}, "
                f"size={size}"
            )

    def finish(event):

        """
        This will finish the interactive window.

        The final filtered data is calculated one last time
        and stored in a variable accessible outside the GUI.
        """

        nonlocal final_data

        final_data = calculate_filtered_data()

        print("\nInteractive filtering finished.")

        plt.close(fig)

    final_data = original.copy()


    fig.selector = RectangleSelector(
        ax,
        on_select,
        useblit=True,
        button=[1],
        minspanx=1,
        minspany=1,
        spancoords="data",
        interactive=True
    )


    #filter size buttons
    radio_ax = fig.add_axes([0.12, 0.06, 0.30, 0.09])

    fig.radio_buttons = RadioButtons(radio_ax,("1", "3", "5", "7", "9", "11"),
        active=2,)

    fig.radio_buttons.on_clicked(select_size)

    #apply button
    apply_ax = fig.add_axes([0.45, 0.07, 0.09, 0.05])

    fig.apply_button = Button(apply_ax, "Apply")

    fig.apply_button.on_clicked(apply_region)

    #clear selection button
    clear_ax = fig.add_axes([0.55, 0.07, 0.09, 0.05])

    fig.clear_button = Button(clear_ax, "Clear")

    fig.clear_button.on_clicked(clear_selection)

    #undo button
    undo_ax = fig.add_axes([0.65, 0.07, 0.09, 0.05])

    fig.undo_button = Button(undo_ax, "Undo")

    fig.undo_button.on_clicked(undo)

    #reset button
    reset_ax = fig.add_axes([0.75, 0.07, 0.09, 0.05])

    fig.reset_button = Button(reset_ax, "Reset")

    fig.reset_button.on_clicked(reset)

    #original button
    original_ax = fig.add_axes([0.12, 0.005, 0.10, 0.05])

    fig.original_button = Button(original_ax, "Original")

    fig.original_button.on_clicked(show_original)

    #filtered button
    filtered_ax = fig.add_axes([0.23, 0.005, 0.10, 0.05])

    fig.filtered_button = Button(filtered_ax, "Filtered")

    fig.filtered_button.on_clicked(show_filtered)

    #region info button
    info_ax = fig.add_axes([0.34, 0.005, 0.10, 0.05])

    fig.info_button = Button(info_ax, "Regions")

    fig.info_button.on_clicked(print_regions)

    #OK button
    ok_ax = fig.add_axes([0.82, 0.005, 0.12, 0.05])

    fig.ok_button = Button(ok_ax, "OK")

    fig.ok_button.on_clicked(finish)
    
    #start the interactive window
    plt.show(block=True)

    #Return final result
    return final_data
        