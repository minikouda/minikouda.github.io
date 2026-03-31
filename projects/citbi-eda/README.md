# Clinically Important Traumatic Brain Injury (ciTBI) — EDA

Exploratory data analysis of pediatric head trauma cases from the PECARN TBI study, identifying risk factors and clinical indicators that distinguish clinically important traumatic brain injury (ciTBI) from minor head injuries.

## Overview

- **Dataset:** PECARN TBI Public Use Dataset (42,412 patients)
- **Target:** ciTBI (clinically important traumatic brain injury)
- **Course:** STAT 214, UC Berkeley

## Key Findings

1. **GCS is the strongest predictor** — altered mental status and low GCS subscores (especially motor) sharply elevate ciTBI risk.
2. **Age-stratified risk profiles** — injury mechanisms and risk factor weights differ between children under 2 and older children.
3. **CT utilization vs. ciTBI** — CT scans are often ordered for patients who turn out not to have ciTBI, highlighting the need for better decision rules.

## Structure

```
code/
  analysis.py       # EDA and visualization scripts
  clean.py          # Data cleaning and preprocessing
  models.py         # Predictive modeling
  lab1.ipynb        # Full analysis notebook
  environment.yaml  # Conda environment

report/
  lab1.pdf          # Final report
  figures/          # Generated figures
```

## Setup

```bash
conda env create -f code/environment.yaml
conda activate tbi-eda
jupyter notebook code/lab1.ipynb
```

> Note: The raw data is not included as it is restricted academic data from the PECARN study.
