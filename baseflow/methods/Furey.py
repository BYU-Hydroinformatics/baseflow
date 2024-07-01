import numpy as np
from numba import njit


@njit
def Furey(Q, b_LH, a, A, return_exceed=False):
    """Furey digital filter (Furey & Gupta, 2001, 2003)
    Furey, Peter R., and Vijay K. Gupta. “A Physically Based Filter for Separating Base Flow from Streamflow Time Series.” Water Resources Research 37, no. 11 (2001): 2709–22. https://doi.org/10.1029/2001WR000243.

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        A (float): calibrated in baseflow.param_estimate
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])
    b[0] = b_LH[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = (a - A * (1 - a)) * b[i] + A * (1 - a) * Q[i]
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b
