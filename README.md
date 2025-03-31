# No-Show Prediction model

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FUMCU-Digital-Health%2FNo_Show%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/UMCU-Digital-Health/No_Show/unit_test.yml)
![GitHub License](https://img.shields.io/github/license/UMCU-Digital-Health/No_Show)


<img src="https://cdn.worldvectorlogo.com/logos/umc-utrecht-1.svg" alt="UMCU Logo" width="400"/>

- Authors: [Ruben Peters](r.peters-7@umcutrecht.nl), Welmoed Tjepkema, Eric Wolters, Ingmar Loohuis
- Contact: datascience@umcutrecht.nl


## Introduction
This repo contains the code for the No-Show prediction model, currently implemented at the UMC Utrecht and developed by the [AI For Health](https://github.com/UMCU-Digital-Health) team.
For more information on implemented AI-tools, see <https://research.umcutrecht.nl/ai-applications-in-use>

## Contributing or using in your organisation
We welcome issues or pull requests! The easiest way to use this repo in your own organisation is to fork the repo. You can then change the data pipelines to fit with your organisation. If you need help, either add an issue or send an e-mail to [AI for Health](datascience@umcutrecht.nl)

## Installation

To install the noshow package use:

```bash
pip install -e .
```

Or better use a package manager like [uv](https://docs.astral.sh/uv/), a modern Python package manager that simplifies dependency management and ensures reproducibility:

```bash
uv sync
```

## Run pipelines

The no-show code uses DVC pipelines. To run the feature-building and model stages, use:

```bash
dvc pull
dvc exp run
```

For more information on data used, check the dataset card [here](data/dataset_card.md)

## Deploying to PositConnect

Deployment of the Api and streamlit dashboard is handled by the `deploy.sh` script. Create a `.env` file with the required variables (see `.example.env` for reference).

```bash
. .env
. deploy.sh
```

Deployment is done through the manifest files.

## Applications

### Prediction Api
The prediction API is a fastapi application that runs every two hours and gives predictions for all input appointments given the start date. The API expects the complete history of all appointments of a patient to construct the features, but will only return predictions that are on the `start_date` or later. 

The API also saves the prediction and information of the request to a database. Furthermore it will delete all previous rows of sensitive information (name, birthdate, phone number) and only add the sensitive info for the predictions of that day. This way we only store sensitive info for the day in which the patient needs te be called. All other info will be collected and used to validate the results.

To run the API locally run:

```bash
python run/app.py
```

### Calling dashboard
The calling dashboard is a Streamlit dashboard that will be used by the person who will call the patients. It will show the prediction in 3 working days sorted by decreasing predicted risk and will also include other appointments of those patients between 3 days and 10 days. This way we make sure that a patient is not called multiple times per week. The dashboard will also show if the patient was already previously called and a patient should only be called if at least one appointment hasn't been discussed with the patient yet. The result of calling the patient will also be stored in the dashboard and will be used to track who needs to be called, as well as validating the outcomes.

To run the dashboard locally run:

```bash
streamlit run run/calling_dash.py
```

### Data flow
The orchestration of the data flows will be handled by Apache Nifi, a powerful data integration tool that automates the movement and transformation of data between systems. The Nifi-flow requests new data from the dataplatform, adds the authentication API-Key as a header, and sends the request to the prediction API. For more information on Apache Nifi, see the [official documentation](https://nifi.apache.org/docs.html).
