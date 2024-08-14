import numpy as np
from numba import njit


def clean_streamflow(series):
    """
    Cleans a streamflow time series by removing invalid values and keeping only years with at least 120 data points.
    
    Args:
        series (pandas.Series): The streamflow time series to be cleaned.
    
    Returns:
        tuple: A tuple containing the cleaned streamflow values and the corresponding dates.
    """
    date, Q = series.index, series.values.astype(float)
    has_value = np.isfinite(Q)
    date, Q = date[has_value], np.abs(Q[has_value])
    year_unique, counts = np.unique(date.year, return_counts=True)
    keep = np.isin(date.year, year_unique[counts >= 120])
    return Q[keep], date[keep]


def exist_ice(date, ice_period):
    """
    Checks if a given date falls within an ice period.
    
    Args:
        date (datetime.datetime): The date to check.
        ice_period (tuple or numpy.ndarray): The ice period, either as a tuple of (start_month, start_day, end_month, end_day) or as a numpy array of months.
    
    Returns:
        bool or numpy.ndarray: True if the date falls within the ice period, False otherwise. If `ice_period` is a numpy array, the return value will be a numpy array of the same shape.
    """
    if (date is None) or (ice_period is None):
        return None

    if isinstance(ice_period, np.ndarray):
        return np.isin(date.month, np.where(ice_period)[0] + 1)

    beg, end = ice_period
    if (end[0] > beg[0]) or ((end[0] == beg[0]) & (end[1] > beg[1])):
        ice = (((date.month > beg[0]) & (date.month < end[0])) |
               ((date.month == beg[0]) & (date.day >= beg[1])) |
               ((date.month == end[0]) & (date.day <= end[1])))
    else:
        ice = (((date.month > beg[0]) | (date.month < end[0])) |
               ((date.month == beg[0]) & (date.day >= beg[1])) |
               ((date.month == end[0]) & (date.day <= end[1])))
    return ice


def moving_average(data, window_size):
  """Calculates the moving average of a list.

  Args:
    data: A list of numbers.
    window_size: The size of the moving window.

  Returns:
    A list of the moving averages.
  """

  if len(data) < window_size:
    raise ValueError("Window size must be less than or equal to the length of the data.")

  moving_averages = []
  for i in range(len(data) - window_size + 1):
    window = data[i: i + window_size]
    average = sum(window) / window_size
    moving_averages.append(average)

  return moving_averages



@njit
def multi_arange(starts, stops):
    """
    Generates a 1D numpy array containing all integers between the given start and stop values for each element in the input arrays.
    
    Args:
        starts (numpy.ndarray): A 1D numpy array of start values.
        stops (numpy.ndarray): A 1D numpy array of stop values, where each stop value corresponds to the start value at the same index.
    
    Returns:
        numpy.ndarray: A 1D numpy array containing all integers between the given start and stop values for each element in the input arrays.
    """
    pos = 0
    cnt = np.sum(stops - starts, dtype=np.int64)
    res = np.zeros((cnt,), dtype=np.int64)
    for i in range(starts.size):
        num = stops[i] - starts[i]
        res[pos:pos + num] = np.arange(starts[i], stops[i])
        pos += num
    return res


def geo2imagexy(x, y):
    """
    Converts geographic coordinates (x, y) to image coordinates (col, row).
    
    Args:
        x (float): The x-coordinate in geographic space.
        y (float): The y-coordinate in geographic space.
    
    Returns:
        Tuple[int, int]: The corresponding column and row indices in image space.
    """
    a = np.array([[0.5, 0.0], [0.0, -0.5]])
    b = np.array([x - -180, y - 90])
    col, row = np.linalg.solve(a, b) - 0.5
    return np.round(col).astype(int), np.round(row).astype(int)


def format_method(method):
    """
    Formats the input method parameter to a list of method names.
    
    Args:
        method (str or list): The input method parameter, which can be a single string or a list of strings.
    
    Returns:
        list: A list of method names.
    """
    if method == 'all':
        method = ['UKIH', 'Local', 'Fixed', 'Slide', 'LH', 'Chapman',
                  'CM', 'Boughton', 'Furey', 'Eckhardt', 'EWMA', 'Willems']
    elif isinstance(method, str):
        method = [method]
    return method

import numpy as np

def kge(simulations, evaluation):
    """Original Kling-Gupta Efficiency (KGE) and its three components
    (r, α, β) as per `Gupta et al., 2009
    <https://doi.org/10.1016/j.jhydrol.2009.08.003>`_.
    Note, all four values KGE, r, α, β are returned, in this order.
    :Calculation Details:
        .. math::
           E_{\\text{KGE}} = 1 - \\sqrt{[r - 1]^2 + [\\alpha - 1]^2
           + [\\beta - 1]^2}
        .. math::
           r = \\frac{\\text{cov}(e, s)}{\\sigma({e}) \\cdot \\sigma(s)}
        .. math::
           \\alpha = \\frac{\\sigma(s)}{\\sigma(e)}
        .. math::
           \\beta = \\frac{\\mu(s)}{\\mu(e)}
        where *e* is the *evaluation* series, *s* is (one of) the
        *simulations* series, *cov* is the covariance, *σ* is the
        standard deviation, and *μ* is the arithmetic mean.
    """
    # calculate error in timing and dynamics r
    # (Pearson's correlation coefficient)
    sim_mean = np.mean(simulations, axis=0, dtype=np.float64)
    obs_mean = np.mean(evaluation, axis=0, dtype=np.float64)

    r_num = np.sum((simulations - sim_mean) * (evaluation - obs_mean),
                   axis=0, dtype=np.float64)
    r_den = np.sqrt(np.sum((simulations - sim_mean) ** 2,
                           axis=0, dtype=np.float64)
                    * np.sum((evaluation - obs_mean) ** 2,
                             axis=0, dtype=np.float64))
    r = r_num / (r_den + 1e-10)
    # calculate error in spread of flow alpha
    alpha = np.std(simulations, axis=0) / (np.std(evaluation, axis=0) + 1e-10)
    # calculate error in volume beta (bias of mean discharge)
    beta = (np.sum(simulations, axis=0, dtype=np.float64)
            / (np.sum(evaluation, axis=0, dtype=np.float64) + 1e-10))
    # calculate the Kling-Gupta Efficiency KGE
    kge_ = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

    return kge_

@njit
def backward(Q, b_LH, a):
    """
    Calculates the baseflow time series `b` from the discharge time series `Q` and the baseflow time series `b_LH` using a backward recursive approach.
    
    The function iterates through the discharge time series in reverse order, calculating the baseflow at each time step based on the baseflow at the next time step and the recession coefficient `a`. If the calculated baseflow exceeds the discharge at the current time step, the baseflow is set to the discharge.
    
    Args:
        Q (numpy.ndarray): The discharge time series.
        b_LH (numpy.ndarray): The baseflow time series.
        a (float): The recession coefficient.
    
    Returns:
        numpy.ndarray: The baseflow time series.
    """
    b = np.zeros(Q.shape[0])
    b[-1] = b_LH[-1]
    for i in range(Q.shape[0] - 1, 0, -1):
        b[i - 1] = b[i] / a
        if b[i] == 0:
            b[i - 1] = Q[i - 1]
        if b[i - 1] > Q[i - 1]:
            b[i - 1] = Q[i - 1]
    return b


import numpy as np
import matplotlib.pyplot as plt

def flow_duration_curve(Q, plot=True):
    """
    Calculate the Flow Duration Curve (FDC) and optionally plot it.

    Parameters:
    Q (numpy array): Streamflow data as a numpy array.
    plot (bool): Whether to plot the FDC, default is True.

    Returns:
    percentiles (numpy array): The percentiles corresponding to streamflow.
    flow_values (numpy array): The sorted streamflow values.
    """
    # Sort the streamflow data in descending order
    sorted_flows = np.sort(Q)[::-1]
    
    # Calculate the percentiles
    ranks = np.arange(1, len(sorted_flows) + 1)
    percentiles = 100 * (ranks / (len(sorted_flows) + 1))
    
    # Plot the FDC if requested
    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(percentiles, sorted_flows, marker='o', linestyle='-')
        plt.xlabel('Percentile (%)')
        plt.ylabel('Flow')
        plt.title('Flow Duration Curve')
        plt.grid(True)
        plt.show()
    
    return percentiles, sorted_flows

# Example usage
Q = np.array([10, 20, 15, 5, 25, 30, 10])
percentiles, flow_values = flow_duration_curve(Q)

print("Percentiles:", percentiles)
print("Flow values:", flow_values)
