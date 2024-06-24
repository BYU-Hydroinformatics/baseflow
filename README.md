<div align="center">

# 🌟 baseflow

</div>
baseflow is a Python package that provides a collection of functions for baseflow separation, which is the process of separating the baseflow component from the total streamflow. 


This project is a copy of the [baseflow repository](https://github.com/xiejx5/baseflow) , which implements various baseflow separation methods described in the paper by Xie et al. (2020): "Evaluation of typical methods for baseflow separation in the contiguous United States" (Journal of Hydrology, 583, 124628. https://doi.org/10.1016/j.jhydrol.2020.124628).

This project is funded by [CIROH](https://ciroh.ua.edu/) and aims to extend the functionality of the original baseflow package by adding new features and improvements. Our goal is to continuously enhance and maintain this package, keeping it up-to-date with the latest developments in baseflow separation techniques.

For detailed usage instructions and examples, please refer to the [📖 documentation](https://baseflow.readthedocs.io/en/latest/)  🔥.

<br>



## ⚡&nbsp;&nbsp;Usage

### Install
```bash
pip install baseflow
```
<br>


### Example
```python
import baseflow
import pandas as pd

df = pd.read_csv(baseflow.example, index_col=0)
df_sta = pd.DataFrame(data=[[30, -28.4, 659], [-109.4, 33, 1611]],
                      index=df.columns, columns=['lon', 'lat', 'area'])
dfs, df_kge = baseflow.separation(df, df_sta, return_kge=True)
print(f'Best Method:\n{df_kge.idxmax(axis=1)}')
```
<br>



## 🚀 Project Structure
The directory structure of baseflow looks like this:
```
├── methods <- implements for 12 baseflow separation methods  
│    
├── separation <- compute baseflow and compare different separation methods  
│    
├── param_estimate <- estimates recession coefficient & backward and calibration approaches to estimate other parameters   
│  
├── comparison <- an evaluation criterion to compare different
methods (KGE) & compute strict baseflow  
│    
└── utils <- helper functions
```
<br>
