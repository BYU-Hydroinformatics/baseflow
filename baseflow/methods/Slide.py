import numpy as np
from numba import njit, prange
from baseflow.methods.local import hysep_interval


def slide(Q, area):
    """Slide interval graphical method from HYSEP program (Sloto & Crouse, 1996)
    Sloto, R. A., & Crouse, M. Y. (1996). HYSEP: A Computer Program for Streamflow Hydrograph Separation and Analysis (96-4040). Reston, VA: U.S. Geological Survey. https://doi.org/10.3133/wri964040.
    
    Args:
        Q (np.array): streamflow
        area (float): basin area in km^2
    """
    inN = hysep_interval(area)
    return slide_interpolation(Q, inN)


@njit
def slide_interpolation(Q, inN):
    b = np.zeros(Q.shape[0])
    for i in prange(np.int64((inN - 1) / 2), np.int64(Q.shape[0] - (inN - 1) / 2)):
        b[i] = np.min(Q[np.int64(i - (inN - 1) / 2):np.int64(i + (inN + 1) / 2)])
    b[:np.int64((inN - 1) / 2)] = np.min(Q[:np.int64((inN - 1) / 2)])
    b[np.int64(Q.shape[0] - (inN - 1) / 2):] = np.min(Q[np.int64(Q.shape[0] - (inN - 1) / 2):])
    return b
