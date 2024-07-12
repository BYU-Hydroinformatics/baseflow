import numpy as np
import pandas as pd
from tqdm import tqdm
from numba import njit, prange
from pathlib import Path
from baseflow.comparision import strict_baseflow, KGE
from baseflow.utils import clean_streamflow, exist_ice, geo2imagexy, format_method
from baseflow.param_estimate import recession_coefficient, param_calibrate, maxmium_BFI


def single_station(series, area=None, ice=None, method='all', return_kge=True):
    """
    Perform baseflow separation on a given streamflow time series using various methods.
    
    Args:
        series (pandas.Series): The streamflow time series to perform baseflow separation on.
        area (float, optional): The drainage area of the streamflow station, used for some methods.
        ice (numpy.ndarray or tuple, optional): A boolean array or a tuple of start and end months indicating the ice-affected period.
        method (str or list, optional): The baseflow separation method(s) to use. Can be a single method name or a list of method names.
        return_kge (bool, optional): Whether to return the Kling-Gupta Efficiency (KGE) score for each method.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the baseflow time series for each method.
        pandas.Series: The KGE score for each method (only if `return_kge` is True).
    """
    Q, date = clean_streamflow(series)
    method = format_method(method)

    # convert ice_period ([11, 1], [3, 31]) to bool array
    if not isinstance(ice, np.ndarray) or ice.shape[0] == 12:
        ice = exist_ice(date, ice)
    strict = strict_baseflow(Q, ice)
    if any(m in ['Chapman', 'CM', 'Boughton', 'Furey', 'Eckhardt', 'Willems'] for m in method):
        a = recession_coefficient(Q, strict)

    b_LH = lh(Q)
    b = pd.DataFrame(np.nan, index=date, columns=method)
    for m in method:
        if m == 'UKIH':
            b[m] = ukih(Q, b_LH)

        if m == 'Local':
            b[m] = local(Q, b_LH, area)

        if m == 'Fixed':
            b[m] = fixed(Q, area)

        if m == 'Slide':
            b[m] = slide(Q, area)

        if m == 'LH':
            b[m] = b_LH

        if m == 'Chapman':
            b[m] = chapman(Q, b_LH, a)

        if m == 'CM':
            b[m] = chapman_maxwell(Q, b_LH, a)

        if m == 'Boughton':
            C = param_calibrate(np.arange(0.0001, 0.1, 0.0001), boughton, Q, b_LH, a)
            b[m] = boughton(Q, b_LH, a, C)

        if m == 'Furey':
            A = param_calibrate(np.arange(0.01, 10, 0.01), furey, Q, b_LH, a)
            b[m] = furey(Q, b_LH, a, A)

        if m == 'Eckhardt':
            # BFImax = maxmium_BFI(Q, b_LH, a, date)
            BFImax = param_calibrate(np.arange(0.001, 1, 0.001), eckhardt, Q, b_LH, a)
            b[m] = eckhardt(Q, b_LH, a, BFImax)

        if m == 'EWMA':
            e = param_calibrate(np.arange(0.0001, 0.1, 0.0001), ewma, Q, b_LH, 0)
            b[m] = ewma(Q, b_LH, 0, e)

        if m == 'Willems':
            w = param_calibrate(np.arange(0.001, 1, 0.001), willems, Q, b_LH, a)
            b[m] = willems(Q, b_LH, a, w)

    if return_kge:
        KGEs = pd.Series(KGE(b[strict].values, np.repeat(
            Q[strict], len(method)).reshape(-1, len(method))), index=b.columns)
        return b, KGEs
    else:
        return b, None


def mult_stations(df, df_sta=None, method='all', return_bfi=False, return_kge=False):
    # baseflow separation worker for single station
    def sep_work(s):
        """
        Performs baseflow separation for a single station.
        
        Args:
            s (str): The station ID.
            df (pd.DataFrame): The input data frame containing the time series data.
            df_sta (pd.DataFrame, optional): A data frame containing station metadata, such as area and coordinates.
            method (str or list, optional): The baseflow separation method(s) to use. Defaults to 'all'.
            return_bfi (bool, optional): Whether to return the baseflow index (BFI) for each method.
            return_kge (bool, optional): Whether to return the Kling-Gupta efficiency (KGE) for each method.
        
        Returns:
            dict: A dictionary of baseflow time series, where the keys are the method names.
            pd.DataFrame: A data frame of BFI values for each method and station, if `return_bfi` is True.
            pd.DataFrame: A data frame of KGE values for each method and station, if `return_kge` is True.
        """
        try:
            # read area, longitude, latitude from df_sta
            area, ice = None, None
            to_num = lambda col: (pd.to_numeric(df_sta.loc[s, col], errors='coerce')
                                  if (df_sta is not None) and (col in df_sta.columns) else np.nan)
            if np.isfinite(to_num('area')):
                area = to_num('area')
            if np.isfinite(to_num('lon')):
                c, r = geo2imagexy(to_num('lon'), to_num('lat'))
                ice = ~thawed[:, r, c]
                ice = ([11, 1], [3, 31]) if ice.all() else ice
            # separate baseflow for station S
            b, KGEs = single(df[s], ice=ice, area=area, method=method, return_kge=return_kge)
            # write into already created dataframe
            for m in method:
                dfs[m].loc[b.index, s] = b[m]
            if return_bfi:
                df_bfi.loc[s] = b.sum() / df.loc[b.index, s].abs().sum()
            if return_kge:
                df_kge.loc[s] = KGEs
        except BaseException:
            pass

    # convert index to datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # thawed months from https://doi.org/10.5194/essd-9-133-2017
    with np.load(Path(__file__).parent / 'thawed.npz') as f:
        thawed = f['thawed']

    # create df to store baseflow
    method = format_method(method)
    dfs = {m: pd.DataFrame(np.nan, index=df.index, columns=df.columns, dtype=float)
           for m in method}

    # create df to store BFI and KGE
    if return_bfi:
        df_bfi = pd.DataFrame(np.nan, index=df.columns, columns=method, dtype=float)
    if return_kge:
        df_kge = pd.DataFrame(np.nan, index=df.columns, columns=method, dtype=float)

    # run separation for each column
    for s in tqdm(df.columns, total=df.shape[1]):
        sep_work(s)

    # return result
    if return_bfi and return_kge:
        return dfs, df_bfi, df_kge
    if return_bfi and not return_kge:
        return dfs, df_bfi
    if not return_bfi and return_kge:
        return dfs, df_kge
    return dfs

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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
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

def chapman_maxwell(Q, a, initial_method='Q0' , return_exceed=False):
    """CM filter (Chapman & Maxwell, 1996)
    Chapman, T. G., Maxwell, A. I. (1996) - Baseflow separation - comparison of numerical methods with tracer experiments, in Hydrol. and Water Resour. Symp., Institution of Engineers Australia, Hobart. pp. 539-545.
    
    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        initial_method (str or float, optional): method to calculate the initial baseflow value.
            Accepted string values are:
            - 'Q0': Use Q[0] as the initial baseflow value.
            - 'min': Use np.min(Q) as the initial baseflow value.
            - 'LH': Calculate the initial baseflow value using the LH method.
            Alternatively, a float value can be oythoprovided to directly set the initial baseflow value.
            Default is 'Q0'.
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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    for i in range(Q.shape[0] - 1):
        b[i + 1] = a / (2 - a) * b[i] + (1 - a) / (2 - a) * Q[i + 1]
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b

def chapman(Q, a, initial_method='Q0', return_exceed=False):
    """Chapman filter (Chapman, 1991)
    Chapman, Tom G. "Comment on 'Evaluation of Automated Techniques for Base Flow and Recession Analyses' by R. J. Nathan and T. A. McMahon." Water Resources Research 27, no. 7 (1991): 1783–84. https://doi.org/10.1029/91WR01007.

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    for i in range(Q.shape[0] - 1):
        b[i + 1] = (3 * a - 1) / (3 - a) * b[i] + (1 - a) / (3 - a) * (Q[i + 1] + Q[i])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b

def eckhardt(Q, a, BFImax, initial_method='Q0', return_exceed=False):
    """Eckhardt filter (Eckhardt, 2005)
    Eckhardt, K. “How to Construct Recursive Digital Filters for Baseflow Separation.” Hydrological Processes 19, no. 2 (2005): 507–15. https://doi.org/10.1002/hyp.5675.

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        BFImax (float): maximum value of baseflow index (BFI)
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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    for i in range(Q.shape[0] - 1):
        b[i + 1] = ((1 - BFImax) * a * b[i] + (1 - a) * BFImax * Q[i + 1]) / (1 - a * BFImax)
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b

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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
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

def fixed(Q, area=None):
    """Fixed interval graphical method from HYSEP program (Sloto & Crouse, 1996)
    Sloto, R. A., & Crouse, M. Y. (1996). HYSEP: A Computer Program for Streamflow Hydrograph Separation and Analysis (96-4040). Reston, VA: U.S. Geological Survey. https://doi.org/10.3133/wri964040.
    
    Args:
        Q (np.array): streamflow
        area (float): basin area in km^2
    """
    inN = hysep_interval(area)
    return fixed_interpolation(Q, inN)


@njit
def fixed_interpolation(Q, inN):
    b = np.zeros(Q.shape[0])
    n = Q.shape[0] // inN
    for i in prange(n):
        b[inN * i:inN * (i + 1)] = np.min(Q[inN * i:inN * (i + 1)])
    if n * inN != Q.shape[0]:
        b[n * inN:] = np.min(Q[n * inN:])
    return b

def furey(Q, a, A, initial_method='Q0', return_exceed=False):
    """Furey digital filter (Furey & Gupta, 2001, 2003)
    Furey, Peter R., and Vijay K. Gupta. “A Physically Based Filter for Separating Base Flow from Streamflow Time Series.” Water Resources Research 37, no. 11 (2001): 2709–22. https://doi.org/10.1029/2001WR000243.

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        A (float): calibrated in baseflow.param_estimate
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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    for i in range(Q.shape[0] - 1):
        b[i + 1] = (a - A * (1 - a)) * b[i] + A * (1 - a) * Q[i]
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b

import numpy as np

def hyd_run(streamflow, k=0.9, passes=4):
    """
    Separates baseflow from a streamflow hydrograph using a digital filter method.

    Args:
        streamflow (numpy.ndarray): A numpy array of streamflow values in chronological order.
        k (float, optional): A filter coefficient between 0 and 1 (typically 0.9). Defaults to 0.9.
        passes (int, optional): Number of times the filter passes through the data (typically 4). Defaults to 4.

    Returns:
        numpy.ndarray: A numpy array of baseflow values.

    Example:
        >>> import numpy as np
        >>> streamflow = np.array([10, 15, 20, 18, 12])
        >>> baseflow = hyd_run(streamflow)
        >>> print(baseflow)
        [10.         10.90909091 13.27272727 15.18181818 14.36363636]
    """
    # Convert to numpy array and handle NaN values
    Q = np.array(streamflow)
    Q = Q[~np.isnan(Q)]

    # Initialize baseflow list
    baseflow = np.zeros_like(Q)
    baseflow[0] = Q[0]  # Set first baseflow value to first streamflow value

    for p in range(1, passes + 1):
        # Forward and backward pass
        if p % 2 == 1:
            start, end, step = 0, len(Q), 1
        else:
            start, end, step = len(Q) - 1, -1, -1

        for i in range(start + step, end, step):
            tmp = k * baseflow[i - step] + (1 - k) * (Q[i] + Q[i - step]) / 2
            baseflow[i] = min(tmp, Q[i])

    return baseflow

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

def lh(Q, beta=0.925, return_exceed=False):
    """LH digital filter (Lyne & Hollick, 1979)
    Lyne, V. and Hollick, M. (1979) Stochastic Time-Variable Rainfall-Runoff Modeling. Institute of Engineers Australia National Conference, 89-93.
    
    Args:
        Q (np.array): streamflow
        beta (float): filter parameter, 0.925 recommended by (Nathan & McMahon, 1990)
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    # first pass
    b[0] = Q[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = beta * b[i] + (1 - beta) / 2 * (Q[i] + Q[i + 1])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1

    # second pass
    b1 = np.copy(b)
    for i in range(Q.shape[0] - 2, -1, -1):
        b[i] = beta * b[i + 1] + (1 - beta) / 2 * (b1[i + 1] + b1[i])
        if b[i] > b1[i]:
            b[i] = b1[i]
            if return_exceed:
                b[-1] += 1
    return b

def local(Q, b_LH, area=None, return_exceed=False):
    """Local minimum graphical method from HYSEP program (Sloto & Crouse, 1996)

    Args:
        Q (np.array): streamflow
        area (float): basin area in km^2
    """
    idx_turn = local_turn(Q, hysep_interval(area))
    if idx_turn.shape[0] < 3:
        raise IndexError('Less than 3 turning points found')
    b = linear_interpolation(Q, idx_turn, return_exceed=return_exceed)
    b[:idx_turn[0]] = b_LH[:idx_turn[0]]
    b[idx_turn[-1] + 1:] = b_LH[idx_turn[-1] + 1:]
    return b


def hysep_interval(area):
    # The duration of surface runoff is calculated from the empirical relation:
    # N=A^0.2, (1) where N is the number of days after which surface runoff ceases,
    # and A is the drainage area in square miles (Linsley and others, 1982, p. 210).
    # The interval 2N* used for hydrograph separations is the odd integer between
    # 3 and 11 nearest to 2N (Pettyjohn and Henning, 1979, p. 31).
    if area is None:
        N = 5
    else:
        N = np.power(0.3861022 * area, 0.2)
    inN = np.ceil(2 * N)
    if np.mod(inN, 2) == 0:
        inN = np.ceil(2 * N) - 1
    inN = np.int64(min(max(inN, 3), 11))
    return inN


@njit
def local_turn(Q, inN):
    idx_turn = np.zeros(Q.shape[0], dtype=np.int64)
    for i in prange(np.int64((inN - 1) / 2), np.int64(Q.shape[0] - (inN - 1) / 2)):
        if Q[i] == np.min(Q[np.int64(i - (inN - 1) / 2):np.int64(i + (inN + 1) / 2)]):
            idx_turn[i] = i
    return idx_turn[idx_turn != 0]

def slide(Q, area):
    """Slide interval graphical method from HYSEP program (Sloto & Crouse, 1996)
    Sloto, R. A., & Crouse, M. Y. (1996). HYSEP: A Computer Program for Streamflow Hydrograph Separation and Analysis (96-4040). Reston, VA: U.S. Geological Survey. https://doi.org/10.3133/wri964040.
    
    Args:
        Q (np.array): streamflow
        area (float): basin area in km^2
    """
    inN = hysep_interval(area)
    return slide_interpolation(Q, inN)

def slide_interpolation(Q, inN):
    b = np.zeros(Q.shape[0])
    for i in prange(np.int64((inN - 1) / 2), np.int64(Q.shape[0] - (inN - 1) / 2)):
        b[i] = np.min(Q[np.int64(i - (inN - 1) / 2):np.int64(i + (inN + 1) / 2)])
    b[:np.int64((inN - 1) / 2)] = np.min(Q[:np.int64((inN - 1) / 2)])
    b[np.int64(Q.shape[0] - (inN - 1) / 2):] = np.min(Q[np.int64(Q.shape[0] - (inN - 1) / 2):])
    return b

def ukih(Q, b_LH, return_exceed=False):
    """graphical method developed by UK Institute of Hydrology (UKIH, 1980)
    Aksoy, Hafzullah, Ilker Kurt, and Ebru Eris. “Filtered Smoothed Minima Baseflow Separation Method.” Journal of Hydrology 372, no. 1 (June 15, 2009): 94–101. https://doi.org/10.1016/j.jhydrol.2009.03.037.

    Args:
        Q (np.array): streamflow
        return_exceed (bool, optional): if True, returns the number of times the
            baseflow exceeds the streamflow.
    """
    N = 5
    block_end = Q.shape[0] // N * N
    idx_min = np.argmin(Q[:block_end].reshape(-1, N), axis=1)
    idx_min = idx_min + np.arange(0, block_end, N)
    idx_turn = ukih_turn(Q, idx_min)
    if idx_turn.shape[0] < 3:
        raise IndexError('Less than 3 turning points found')
    b = linear_interpolation(Q, idx_turn, return_exceed=return_exceed)
    b[:idx_turn[0]] = b_LH[:idx_turn[0]]
    b[idx_turn[-1] + 1:] = b_LH[idx_turn[-1] + 1:]
    return b


@njit
def ukih_turn(Q, idx_min):
    idx_turn = np.zeros(idx_min.shape[0], dtype=np.int64)
    for i in prange(idx_min.shape[0] - 2):
        if ((0.9 * Q[idx_min[i + 1]] < Q[idx_min[i]]) &
                (0.9 * Q[idx_min[i + 1]] < Q[idx_min[i + 2]])):
            idx_turn[i] = idx_min[i + 1]
    return idx_turn[idx_turn != 0]


@njit
def linear_interpolation(Q, idx_turn, return_exceed=False):
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    n = 0
    for i in range(idx_turn[0], idx_turn[-1] + 1):
        if i == idx_turn[n + 1]:
            n += 1
            b[i] = Q[i]
        else:
            b[i] = Q[idx_turn[n]] + (Q[idx_turn[n + 1]] - Q[idx_turn[n]]) / \
                (idx_turn[n + 1] - idx_turn[n]) * (i - idx_turn[n])
        if b[i] > Q[i]:
            b[i] = Q[i]
            if return_exceed:
                b[-1] += 1
    return b

def what(streamflow, BFImax, alpha):
    """
    Separates baseflow and quickflow from a streamflow time series using the WHAT method.

    Args:
        streamflow (numpy.ndarray): A numpy array of streamflow values.
        BFImax (float): The maximum baseflow index (BFI) value.
        alpha (float): A filter parameter.

    Returns:
        tuple: A tuple containing two numpy arrays: baseflow and quickflow.

    Example:
        >>> import numpy as np
        >>> streamflow = np.array([10, 15, 20, 18, 12])
        >>> baseflow, quickflow = what(streamflow, 0.8, 0.98)
        >>> print(baseflow)
        [ 9.8         12.74        15.68        16.544       15.3712    ]
        >>> print(quickflow)
        [ 0.2          2.26         4.32         1.456       -3.3712    ]
    """
    baseflow = np.zeros_like(streamflow)

    for t in range(1, len(streamflow)):
        baseflow[t] = ((1 - BFImax) * alpha * baseflow[t-1] + (1 - alpha) * BFImax * streamflow[t]) / (1 - alpha * BFImax)

    quickflow = streamflow - baseflow

    return baseflow

def willems(Q, a, w, initial_method='Q0', return_exceed=False):
    """digital filter (Willems, 2009)

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        w (float): case-speciﬁc average proportion of the quick ﬂow
                   in the streamflow, calibrated in baseflow.param_estimate
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
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    v = (1 - w) * (1 - a) / (2 * w)
    for i in range(Q.shape[0] - 1):
        b[i + 1] = (a - v) / (1 + v) * b[i] + v / (1 + v) * (Q[i] + Q[i + 1])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b
