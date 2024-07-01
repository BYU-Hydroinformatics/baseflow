import numpy as np
from numba import njit


@njit
def Chapman(Q, b_LH, a, return_exceed=False):
    """Chapman filter (Chapman, 1991)
    Chapman, Tom G. “Comment on ‘Evaluation of Automated Techniques for Base Flow and Recession Analyses’ by R. J. Nathan and T. A. McMahon.” Water Resources Research 27, no. 7 (1991): 1783–84. https://doi.org/10.1029/91WR01007.

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])
    b[0] = b_LH[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = (3 * a - 1) / (3 - a) * b[i] + (1 - a) / (3 - a) * (Q[i + 1] + Q[i])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b
