# Getting started

Welcome to the documentation for the No-Show prediction model. This project aims to prevent no-shows by calling high-risk patients before their appointments.

## Overview
On this page, you will find information on how to install and use the No-Show prediction model.
For information on the dataset used for training the model, please refer to the [Dataset Card](dataset_card.md).

The idea of a no-show prediction model was first implemented at the Erasmus MC, this project is based on their approach and features.

## Install the No-Show package

To install the No-Show package, first clone the repository and install the package using a package manager like pip or uv.

clone the repository:

```bash
git clone https://github.com/UMCU-Digital-Health/No_Show.git
cd No_Show
```

Then, install the package:

```bash
pip install -r requirements.txt
```

or using [uv](https://astral.sh/uv/):

```bash
uv sync
```

## Run pipelines

To run the entire pipeline from data export to model training, you can use the `train_no_show` command (or `python src/noshow/train_pipeline.py`):

```bash
train_no_show --skip-export  # skip the export step if you already have the data
```

For more information on data used, check the dataset card [here](dataset_card.md)

## Run the API

To run the prediction API, which creates predictions for appointments, you can use the following command:

```bash
python run/app.py
```

## Run the Calling Dashboard
The calling dashboard is a Streamlit application that allows users to view predictions and manage patient calls. To run the dashboard locally, use the following command:

```bash
streamlit run run/calling_dash.py
```

## Run the Admin dashboard
The admin dashboard is a Streamlit application that allows users to check the performance of the application and call results. To run the dashboard locally, use the following command:

```bash
streamlit run run/admin_dash.py
```
