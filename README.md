# baseflow
baseflow is a Python package that provides a collection of functions for baseflow separation, which is the process of separating the baseflow component from the total streamflow. 


This project is a copy of the [baseflow repository](https://github.com/xiejx5/baseflow) , which implements various baseflow separation methods described in the paper by Xie et al. (2020): "Evaluation of typical methods for baseflow separation in the contiguous United States" (Journal of Hydrology, 583, 124628. https://doi.org/10.1016/j.jhydrol.2020.124628).

This project is funded by [CIROH](https://ciroh.ua.edu/) and aims to extend the functionality of the original baseflow package by adding new features and improvements. Our goal is to continuously enhance and maintain this package, keeping it up-to-date with the latest developments in baseflow separation techniques.

For detailed usage instructions and examples, please refer to the [documentation](https://baseflow.readthedocs.io/en/latest/) .

## Usage

### Install
```bash 
pip install baseflow
```


## Project Structure
The directory structure of baseflow looks like this:
```
├── separation <- compute baseflow and compare different separation methods  
│    
├── estimate <- estimates recession coefficient & calibration approaches to estimate other parameters    
│    
└── utils <- helper functions
```
