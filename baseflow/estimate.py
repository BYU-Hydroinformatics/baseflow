import numpy as np
from numba import njit, prange
from baseflow.utils import moving_average, multi_arange, backward

def param_calibrate(param_range, method, Q, b_LH, a):
    """
    Calibrate the parameters of a method using the given parameter range, flow data (Q), baseflow data (b_LH), and other parameters (a).
    
    This function separates the flow data into recession and non-recession periods, and calculates the Nash-Sutcliffe Efficiency (NSE) for each part. It then combines the NSE values to get the overall loss function, and returns the parameter value that minimizes this loss.
    
    Args:
        param_range (numpy.ndarray): The range of parameter values to test.
        method (callable): The method to use for calculating the baseflow.
        Q (numpy.ndarray): The flow data.
        b_LH (numpy.ndarray): The baseflow data.
        a (float): Additional parameter for the method.
        idx_rec (numpy.ndarray): Boolean array indicating the recession periods.
        idx_oth (numpy.ndarray): Boolean array indicating the non-recession periods.
    
    Returns:
        (float): The optimal parameter value.
    """
        
    idx_rec = recession_period(Q)
    idx_oth = np.full(Q.shape[0], True)
    idx_oth[idx_rec] = False
    return param_calibrate_jit(param_range, method, Q, b_LH, a, idx_rec, idx_oth)

@njit(parallel=True)
def param_calibrate_jit(param_range, method, Q, b_LH, a, idx_rec, idx_oth):
    """
    Calibrate the parameters of a method using the given parameter range, flow data (Q), baseflow data (b_LH), and other parameters (a).
    
    This function separates the flow data into recession and non-recession periods, and calculates the Nash-Sutcliffe Efficiency (NSE) for each part. It then combines the NSE values to get the overall loss function, and returns the parameter value that minimizes this loss.
    
    Args:
        param_range (numpy.ndarray): The range of parameter values to test.
        method (callable): The method to use for calculating the baseflow.
        Q (numpy.ndarray): The flow data.
        b_LH (numpy.ndarray): The baseflow data.
        a (float): Additional parameter for the method.
        idx_rec (numpy.ndarray): Boolean array indicating the recession periods.
        idx_oth (numpy.ndarray): Boolean array indicating the non-recession periods.
    
    Returns:
        (float): The optimal parameter value.
    """
    logQ = np.log1p(Q)
    loss = np.zeros(param_range.shape)
    for i in range(param_range.shape[0]):  # Remove prange for now
        p = param_range[i]
        b_exceed = method(Q, b_LH, a, p, return_exceed=True)
        f_exd, logb = b_exceed[-1] / Q.shape[0], np.log1p(b_exceed[:-1])

        # NSE for recession part
        Q_obs, Q_sim = logQ[idx_rec], logb[idx_rec]
        SS_res = np.sum(np.square(Q_obs - Q_sim))
        SS_tot = np.sum(np.square(Q_obs - np.mean(Q_obs)))
        NSE_rec = (1 - SS_res / (SS_tot + 1e-10)) - 1e-10

        # NSE for other part
        Q_obs, Q_sim = logQ[idx_oth], logb[idx_oth]
        SS_res = np.sum(np.square(Q_obs - Q_sim))
        SS_tot = np.sum(np.square(Q_obs - np.mean(Q_obs)))
        NSE_oth = (1 - SS_res / (SS_tot + 1e-10)) - 1e-10

        loss[i] = 1 - (1 - (1 - NSE_rec) / (1 - NSE_oth)) * (1 - f_exd)
    return param_range[np.argmin(loss)]

@njit(parallel=True)
def param_calibrate_jit_numba(param_range, Q, b_LH, a, idx_rec, idx_oth):
    """
    Calibrate the parameters of a method using the given parameter range, flow data (Q), baseflow data (b_LH), and other parameters (a).
    
    This function separates the flow data into recession and non-recession periods, and calculates the Nash-Sutcliffe Efficiency (NSE) for each part. It then combines the NSE values to get the overall loss function, and returns the parameter value that minimizes this loss.
    
    Args:
        param_range (numpy.ndarray): The range of parameter values to test.
        Q (numpy.ndarray): The flow data.
        b_LH (numpy.ndarray): The baseflow data.
        a (float): Additional parameter for the method.
        idx_rec (numpy.ndarray): Boolean array indicating the recession periods.
        idx_oth (numpy.ndarray): Boolean array indicating the non-recession periods.
    
    Returns:
        (float): The optimal parameter value.
    """
    logQ = np.log1p(Q)
    loss = np.zeros(param_range.shape)
    for i in prange(param_range.shape[0]):
        p = param_range[i]
        b_exceed = method_numba(Q, b_LH, a, p, return_exceed=True)
        f_exd, logb = b_exceed[-1] / Q.shape[0], np.log1p(b_exceed[:-1])

        # NSE for recession part
        Q_obs, Q_sim = logQ[idx_rec], logb[idx_rec]
        SS_res = np.sum(np.square(Q_obs - Q_sim))
        SS_tot = np.sum(np.square(Q_obs - np.mean(Q_obs)))
        NSE_rec = (1 - SS_res / (SS_tot + 1e-10)) - 1e-10

        # NSE for other part
        Q_obs, Q_sim = logQ[idx_oth], logb[idx_oth]
        SS_res = np.sum(np.square(Q_obs - Q_sim))
        SS_tot = np.sum(np.square(Q_obs - np.mean(Q_obs)))
        NSE_oth = (1 - SS_res / (SS_tot + 1e-10)) - 1e-10

        loss[i] = 1 - (1 - (1 - NSE_rec) / (1 - NSE_oth)) * (1 - f_exd)
    return param_range[np.argmin(loss)]

# Example method function that can be used with Numba
@njit
def method_numba(Q, b_LH, a, p, return_exceed=False):
    """
    Applies a method to estimate baseflow from the given flow data (Q) and baseflow data (b_LH), using the provided parameter (p) and additional parameter (a).
    
    Args:
        Q (numpy.ndarray): The flow data.
        b_LH (numpy.ndarray): The baseflow data.
        a (float): An additional parameter for the method.
        p (float): The parameter value to use for the method.
        return_exceed (bool, optional): If True, also returns the exceeded baseflow ratio. Defaults to False.
    
    Returns:
        (numpy.ndarray): The estimated baseflow.
        (float (optional)): The exceeded baseflow ratio, if return_exceed is True.
    """
        # Implement the method logic here
    pass

def recession_period(Q):
    """
    Identifies the recession periods in the given flow data (Q) by calculating the moving average and finding the start and end indices of the recession periods.
    
    Args:
        Q (numpy.ndarray): The flow data.
    
    Returns:
        (numpy.ndarray): A boolean array indicating the recession periods.
    """
    idx_dec = np.zeros(Q.shape[0] - 1, dtype=np.int64)
    Q_ave = moving_average(Q, 3)
    idx_dec[1:-1] = (Q_ave[:-1] - Q_ave[1:]) > 0
    idx_beg = np.where(idx_dec[:-1] - idx_dec[1:] == -1)[0] + 1
    idx_end = np.where(idx_dec[:-1] - idx_dec[1:] == 1)[0] + 1
    idx_keep = (idx_end - idx_beg) >= 10
    idx_beg = idx_beg[idx_keep]
    idx_end = idx_end[idx_keep]
    duration = idx_end - idx_beg
    idx_beg = idx_beg + np.ceil(duration * 0.6).astype(np.int64)
    return multi_arange(idx_beg, idx_end)
