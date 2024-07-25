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
