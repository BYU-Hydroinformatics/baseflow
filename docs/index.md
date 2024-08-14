# 🌟 baseflow

baseflow is a Python package that provides a collection of functions for baseflow separation, which is the process of separating the baseflow component from the total streamflow.

This project is funded by [CIROH](https://ciroh.ua.edu/) and aims to extend the functionality of the original baseflow package by adding new features and improvements. Our goal is to continuously enhance and maintain this package, keeping it up-to-date with the latest developments in baseflow separation techniques.

🔥 **Our [GitHub](https://github.com/BYU-Hydroinformatics/baseflow/tree/merge-my-changes)** 🔥

## 🚀 Project Structure

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

## Computation Process
---
title: Baseflow Separation Process Diagram
---
graph TB
    subgraph "Required-Inputs"
        Input["Streamflow Q\nStation Info"]
    end
    subgraph "Data-Preprocessing"
        Pre1["clean_streamflow"]
        Pre2["exist_ice"]
    end
    subgraph "Recession-Analysis"
        RA["recession_coefficient"]
    end
    subgraph "Baseflow-Separation"
        BS1["single"]
        BS2["separation"]
    end
    subgraph "Separation-Methods"
        SM1["UKIH"]
        SM2["Local"]
        SM3["Fixed"]
        SM4["Slide"]
        SM5["LH"]
        SM6["Chapman"]
        SM7["CM"]
        SM8["Boughton"]
        SM9["Furey"]
        SM10["Eckhardt"]
        SM11["EWMA"]
        SM12["Willems"]
    end
    subgraph "Parameter-Estimation"
        PE1["param_calibrate"]
        PE2["maxmium_BFI"]
    end
    subgraph "Comparison-Evaluation"
        CE1["KGE"]
        CE2["strict_baseflow"]
    end
    subgraph "Output-Results"
        Output["Baseflow\nKGE\nBFI"]
    end

    Input ==> Data-Preprocessing
    Data-Preprocessing ==> Recession-Analysis
    Recession-Analysis ==> Baseflow-Separation
    Baseflow-Separation ==> Separation-Methods
    Separation-Methods ==> Parameter-Estimation
    Parameter-Estimation ==> Comparison-Evaluation
    Comparison-Evaluation ==> Output-Results

    Pre1 --> Pre2
    BS1 --> BS2
    PE1 --> PE2
    CE1 --> CE2

    classDef default fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px;
    classDef input fill:#f9f,stroke:#333,stroke-width:2px;
    classDef output fill:#f9f,stroke:#333,stroke-width:2px;
    class Input,Output input;
    class Data-Preprocessing,Recession-Analysis,Baseflow-Separation,Separation-Methods,Parameter-Estimation,Comparison-Evaluation default;