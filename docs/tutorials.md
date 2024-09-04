# Tutorials

### ***Installation***

We have developed a Python package named `baseflow` that provides tools for baseflow separation. This package is available on PyPI and can be easily installed using pip:

```python
pip install baseflow
```
To help you get started with the baseflow package, we have created a Colab notebook that demonstrates its usage. 

???+ note

    You may wish to make a copy of the notebook in your own Google Drive.

!!! tip

    Run each cell of the notebook by hitting the play button on the left side of each cell and provide the necessary inputs by following the prompts.

    The notebook is divided into multiple sections and each section contains a set of cells, each of which contains Python code. When you first launch the notebook, the sections are collapsed and you need to expand each section to view and run the code.

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

### ***Example on a Single Station***
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