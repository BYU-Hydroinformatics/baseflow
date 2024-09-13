# Tutorials


To help you get started with the baseflow package, we have created a Colab notebook that demonstrates its usage. 

???+ note

    You may wish to make a copy of the notebook in your own Google Drive.

!!! tip

    Run each cell of the notebook by hitting the play button on the left side of each cell and provide the necessary inputs by following the prompts.

    The notebook is divided into multiple sections and each section contains a set of cells, each of which contains Python code. When you first launch the notebook, the sections are collapsed and you need to expand each section to view and run the code.

### ***Getting Started***

**Data Preparation**

In this section, we will guide you through the process of preparing your data for baseflow separation. There are two methods available for data preparation:

**Method 1: Upload Your Own CSV**

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


**Method 2: Use API to Download Data from USGS**

Alternatively, you can use the USGS API to download streamflow data for a specific station. This method requires the station ID, which you can find on the USGS website.

We provide an API that allows you to download streamflow data from the USGS (United States Geological Survey) for a specified station and time range.

Parameters:

- **station_id:** The USGS station ID for the desired location.
- **start_date:** The start date for the data in `YYYY-MM-DD` format.
- **end_date:** The end date for the data in `YYYY-MM-DD` format.

### ***Separation Methods***
Check out the Separation Methods Colab notebook:
<div class="colab-button">
    <a href="https://colab.research.google.com/github/BYU-Hydroinformatics/baseflow-notebooks/blob/main/baseflow_separation_methods.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
    </a>
</div>
 
In this section, we will introduce the different methods available in the baseflow package for performing baseflow separation:

 - Overview of the various algorithms and techniques implemented in the baseflow package.
 - Method Descriptions: Detailed descriptions of each method, including their theoretical background and use cases.
 - Code Examples: Python code snippets demonstrating how to apply each method using the baseflow package.
### ***Utils***
Access the Comparison Colab notebook here:
<div class="colab-button">
    <a href="https://colab.research.google.com/github/BYU-Hydroinformatics/baseflow-notebooks/blob/main/baseflow_utils.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
    </a>
</div>

This utils file in the baseflow package contains several utility functions for processing and analyzing streamflow data. Here's a brief description of what the file does:

 - It provides functions for cleaning and preprocessing streamflow time series data.
 - It includes a function to check if a given date falls within an ice period.
 - There's a function for calculating moving averages of data.
 - The file includes a function for converting geographic coordinates to image coordinates.

Overall, this file serves as **a collection of helper functions** that support various operations related to streamflow analysis, data cleaning, and coordinate transformations in the baseflow package.

### ***Example on a single station***
Single Station Example Colab notebook:
<div class="colab-button">
    <a href="https://colab.research.google.com/github/BYU-Hydroinformatics/baseflow-notebooks/blob/main/baseflow_single_station.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
    </a>
</div>
This section provides a step-by-step example of how to perform baseflow separation on data from a single hydrological station. We will use sample data to demonstrate the process, from loading the data to visualizing the results. 

 - Loading Data: Instructions on how to load streamflow data for a single station.
 - Applying Separation Methods: Applying the separation methods to the loaded data.
 - Visualization: visualizing the baseflow separation results.


### ***Example on multiple stations***
Multiple Stations Example Colab notebook:

<div class="colab-button">
    <a href="https://colab.research.google.com/github/BYU-Hydroinformatics/baseflow-notebooks/blob/main/baseflow_multi_station.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
    </a>
</div>


The multi_station file takes a DataFrame containing flow data for multiple stations, and optionally a DataFrame with station information. The function allows for flexible application of various baseflow separation methods across multiple stations, streamlining the process of analyzing baseflow components in large-scale hydrological studies or regional assessments. This function enhances efficiency by applying the chosen separation method(s) to all stations in a single operation.
