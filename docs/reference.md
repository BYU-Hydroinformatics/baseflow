# Getting Started 

## Data Preparation

In this section, we will guide you through the process of preparing your data for baseflow separation. There are two methods available for data preparation:

### Method 1: Upload Your Own CSV

You can upload your own CSV file containing streamflow data. The CSV file should be formatted as follows:

- **Date**: The first column should contain the date in `YYYY-MM-DD` format.
- **Streamflow**: The second column should contain the streamflow values in cubic feet per second (cfs).

Here is an example of the expected CSV format:

| `Date`      | `Streamflow`                          |
| ----------- | ------------------------------------ |
| `2023-01-01`      | 150      |
| `2023-01-02`| 145.5 |
| `2023-01-03`| 160.2 |
| `...`| `...` |


### Method 2: Use API to Download Data from USGS
Alternatively, you can use the USGS API to download streamflow data for a specific station. This method requires the station ID, which you can find on the USGS website.

We provide an API that allows you to download streamflow data from the USGS (United States Geological Survey) for a specified station and time range.

Parameters:

- **station_id:** The USGS station ID for the desired location.
- **start_date:** The start date for the data in `YYYY-MM-DD` format.
- **end_date:** The end date for the data in `YYYY-MM-DD` format.