import numpy as np
from numba import njit

@njit
def boughton(Q, a, C, initial_method='Q0', return_exceed=False):
    """Boughton doulbe-parameter filter (Boughton, 2004)
    Boughton W.C. (1993) - A hydrograph-based model for estimating water yield of ungauged catchments. Institute of Engineers Australia National Conference. Publ. 93/14, pp. 317-324.
    
    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        C (float): calibrated in baseflow.param_estimate
        initial_method (str or float, optional): method to calculate the initial baseflow value.
            Accepted string values are:
            - 'Q0': Use Q[0] as the initial baseflow value.
            - 'min': Use np.min(Q) as the initial baseflow value.
            - 'LH': Calculate the initial baseflow value using the LH method.
            Alternatively, a float value can be provided to directly set the initial baseflow value.
            Default is 'Q0'.
        return_exceed (bool, optional): if True, returns the number of times the
            baseflow exceeds the streamflow.
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    # Set initial value for b based on the specified method
    if isinstance(initial_method, str):
        if initial_method == 'Q0':
            b[0] = Q[0]
        elif initial_method == 'min':
            b[0] = np.min(Q)
        elif initial_method == 'LH':
            b[0] = LH(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    for i in range(Q.shape[0] - 1):
        b[i + 1] = a / (1 + C) * b[i] + C / (1 + C) * Q[i + 1]
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1

    return b

@njit
def lh(Q, beta=0.925):
    """LH digital filter (Lyne & Hollick, 1979)

    Args:
        Q (np.array): streamflow
        beta (float): filter parameter, 0.925 recommended by (Nathan & McMahon, 1990)
    """
    b = np.zeros(Q.shape[0])
    b[0] = Q[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = beta * b[i] + (1 - beta) / 2 * (Q[i] + Q[i + 1])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
    return b
