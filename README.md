# No_Show

Authors: Ruben Peters, Ingmar Loohuis
Email: r.peters-7@umcutrecht.nl

## Installation

To install the noshow package use:

```{bash}
pip install -e .
```

## Run pipelines

The no-show code uses DVC pipelines. To run the feature-building and model stages, use:

```{bash}
dvc pull
dvc exp run
```

For more information on data used, check the dataset card [here](data/dataset_card.md)

## Deploying to PositConnect

Deployment of the Api and streamlit dashboard is handled by the `deploy.sh` script. Create a `.env` file (see `.example.env`) and run:

```{bash}
. .env
. deploy.sh
```

Deployment is done through the manifest files.

## Applications

### Prediction Api
The prediction API is a fastapi application that runs once per day and gives predictions for all input appointments given the start date. The API expects the complete history of all appointments of a patient to construct the features, but will only return predictions that are on the `start_date` or later. 

The API also saves the prediction and information of the request to a database. Furthermore it will delete all previous rows of sensitive information (name, birthdate, phone number) and only add the sensitive info for the predictions of that day. This way we only store sensitive info for the day in which the patient needs te be called. All other info will be collected and used to validate the results of the pilot.

To run the API locally run:
```{bash}
python run/app.py
```

### Calling dashboard
The calling dashboard is a Streamlit dashboard that will be used by the person who will call the patients. It will show the top n prediction in 3 working days time and will also include predictions of those patients between 3 days and 10 days. This way we make sure that a patient is not called multiple times per week. The dashboard will also show if the patient was already previously called and a patient should only be called if at least one appointment hasn't been discussed with the patient yet. The result of calling the patient will also be stored in the dashboard and will be used to track who needs to be called, as well as validating the pilot results.

To run the dashboard locally run:
```{bash}
streamlit run run/calling_dash.py
```

### Data flow
The orchestration of the data flows will be handled by Apache Nifi. The Nifi-flow requests new data from the dataplatform, adds the authentication API-Key as header and sends the request to the prediction API.
