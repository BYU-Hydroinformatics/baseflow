import numpy as np
from numba import njit


@njit
def EWMA(Q, b_LH, a, e, return_exceed=False):
    """exponential weighted moving average (EWMA) filter (Tularam & Ilahee, 2008)
    Tularam, Gurudeo Anand, and Mahbub Ilahee. “Exponential Smoothing Method of Base Flow Separation and Its Impact on Continuous Loss Estimates.” American Journal of Environmental Sciences 4, no. 2 (April 30, 2008): 136–44. https://doi.org/10.3844/ajessp.2008.136.144.
    
    Args:
        Q (np.array): streamflow
        e (float): smoothing parameter
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])
    b[0] = b_LH[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = (1 - e) * b[i] + e * Q[i + 1]
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b
