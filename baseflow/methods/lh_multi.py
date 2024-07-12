import numpy as np
from numba import njit


@njit
def lh_multi(Q, beta=0.925, num_pass=2, return_exceed=False):
    """
    Applies a low-pass filter to the input time series `Q` using the Lyne-Hollick (LH) recursive digital filter.
    
    The filter is applied in multiple passes, with the number of passes controlled by the `num_pass` parameter. The filter uses a smoothing parameter `beta` to control the degree of filtering.

    Spongberg, M. E. “Spectral Analysis of Base Flow Separation with Digital Filters.” Water Resources Research 36, no. 3 (2000): 745–52. https://doi.org/10.1029/1999WR900303.
   
    If `return_exceed` is True, the function will also return the number of times the filtered output `b` exceeds the original input `Q`.
    
    Lyne, V. and Hollick, M. (1979) Stochastic Time-Variable Rainfall-Runoff Modeling. Institute of Engineers Australia National Conference, 89-93. 
    
    Spongberg, M. E. “Spectral Analysis of Base Flow Separation with Digital Filters.” Water Resources Research 36, no. 3 (2000): 745–52. https://doi.org/10.1029/1999WR900303.

    Args:
        Q (numpy.ndarray): The input time series to be filtered.
        beta (float, optional): The smoothing parameter for the LH filter, between 0 and 1. Defaults to 0.925.
        num_pass (int, optional): The number of filter passes to apply. Defaults to 2.
        return_exceed (bool, optional): If True, the function will return the number of times the filtered output exceeds the original input. Defaults to False.
    
    Returns:
        numpy.ndarray: The filtered output time series.
        int (optional): The number of times the filtered output exceeds the original input, if `return_exceed` is True.
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    b[0] = Q[0]

    for n in range(num_pass):
        if n != 0:
            b = np.flip(b, axis=0)
            Q = b.copy()
        
        for i in range(Q.shape[0] - 1):
            b[i + 1] = beta * b[i] + (1 - beta) / 2 * (Q[i] + Q[i + 1])
            if b[i + 1] > Q[i + 1]:
                b[i + 1] = Q[i + 1]
                if return_exceed:
                    b[-1] += 1

    if num_pass % 2 == 0:
        b = np.flip(b, axis=0)

    return b
