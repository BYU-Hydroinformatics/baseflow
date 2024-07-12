import numpy as np
from numba import njit


@njit
def ewma(Q, e, initial_method='Q0', return_exceed=False):
    """exponential weighted moving average (EWMA) filter (Tularam & Ilahee, 2008)
    Tularam, Gurudeo Anand, and Mahbub Ilahee. “Exponential Smoothing Method of Base Flow Separation and Its Impact on Continuous Loss Estimates.” American Journal of Environmental Sciences 4, no. 2 (April 30, 2008): 136–44. https://doi.org/10.3844/ajessp.2008.136.144.
    
    Args:
        Q (np.array): streamflow
        e (float): smoothing parameter
        initial_method (str or float, optional): method to calculate the initial baseflow value.
            Accepted string values are:
            - 'Q0': Use Q[0] as the initial baseflow value.
            - 'min': Use np.min(Q) as the initial baseflow value.
            - 'LH': Calculate the initial baseflow value using the LH method.
            Alternatively, a float value can be provided to directly set the initial baseflow value.
            Default is 'Q0'.
        return_exceed (bool, optional): if True, returns the number of times the
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
        b[i + 1] = (1 - e) * b[i] + e * Q[i + 1]
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
