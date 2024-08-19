import numpy as np
from numba import njit, prange
from baseflow.utils import moving_average, multi_arange, backward

def param_calibrate(param_range, method, Q, b_LH, a):
    idx_rec = recession_period(Q)
    idx_oth = np.full(Q.shape[0], True)
    idx_oth[idx_rec] = False
    return param_calibrate_jit(param_range, method, Q, b_LH, a, idx_rec, idx_oth)

def param_calibrate_jit(param_range, method, Q, b_LH, a, idx_rec, idx_oth):
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
    # Implement the method logic here
    pass

def recession_period(Q):
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
