## Dataset Description

- **Repository:** [https://github.com/UMCU-Digital-Health/No_Show](https://github.com/UMCU-Digital-Health/No_Show)
- **Leaderboard:** Current best scores can be found [here](../output/dvclive/metrics.json)
- **Point of Contact:** [Ruben Peters](mailto:r.peters-7@umcutrecht.nl)

### Dataset Summary

The dataset consists of all appointments created between January 2015 and May 2023. It combines data from different Data platform tables, namely Appointment, HealthCareService, Polyklinisch_consult, Patient and Patient_address. It uses HealthCareService specialtycodes to filter on clinic and excludes appointments that are booked.

### Supported Tasks and Leaderboards

- `Classification`: The dataset can be used to train a model for classifying no-shows at the clinics in the UMCU. Success on this task is typically measured by achieving a high AUC score. The performance of the best model can be found in [output/dvclive/metrics.json](../output/dvclive/metrics.json).

### Languages

The dataset is mostly Dutch. However, some columns (that follow FHIR standards) are in English.

## Dataset Structure

### Data Instances

The prediction data is structured as follows:

```{json}
{
  "HCS_ID": "1234",
  "APP_ID": "5678",
  "pseudo_id": "1ch5k",
  "name": "Jan Klaassen",
  "partOf_HealthcareService_value": "A12345",
  "location1_Location_value": "0000007362",
  "specialty_code": "REV",
  "specialty_display": "Revalidatie",
  "appointmentType_code": "ROUTINE",
  "appointmentType_display": "Routine appointment",
  "soort_consult": "Eerste",
  "start": "2023-01-01T09:00:00",
  "end": "2023-01-01T09:30:00",
  "gearriveerd": "2023-01-01T09:02:00",
  "created": "2022-10-01T00:00",
  "minutesDuration": "30",
  "status": "fulfilled",
  "status_code_original": "J",
  "cancelationReason_code": "NULL",
  "cancelationReason_display": "NULL",
  "verwijzer_zorgverlenerrol_identifier_value": "38072",
  "BIRTH_YEAR": "1994",
  "address_postalCodeNumbersNL": "3994"
}
```

Every observation contains all the information of a single appointment. When predicting for a single appointment all the previous appointments of the patient also need to be included as they can be used for feature engineering.

### Data Fields

Below you can find the datafields present in the dataset:

- `example_field`: description of `example_field`
- `HCS_ID`: string with the identifier of the HealthCareService
- `APP_ID`: string with the identifier of the Appointment
- `pseudo_id`: string of the hashed patient id
- `name`: string with the name of the HealthCareService provider
- `partOf_HealthcareService_value`: string with name of the overarching HealthCareService provider
- `location1_Location_value`: string with the location of the HealthCareService, not used since this can differ between clinics
- `specialty_code`: string with the specialty code of the HealthCareService, for this pilot: REV, KAP, SPO, LON
- `specialty_display`: string with the complete name of the specialty of the HealthCareService, for this pilot: Revalidatie, Algemene pediatrie, Sportgeneeskunde, Longgeneeskunde
- `appointmentType_code`: string with the type of the appointment, currently not used because of data leakage
- `appointmentType_display`: string with the name of the appointment type, currently not used because of data leakage
- `soort_consult`: string with consult type, mainly used to filter out phone appointments
- `start`: datetime in isoformat with the start date of the appointment
- `end`: datetime in isoformat with the end date of the appointment
- `gearriveerd`: datetime in isoformat with the date of arrival of the patient
- `created`: datetime in isoformat with the creation date of the appointment
- `minutesDuration`: integer indicating the duration of the appointment in minutes
- `status`: string with the status of the appointment, for example: booked or fulfilled.
- `status_code_original`: string with the status of the appointent.
- `cancelationReason_code`: string with the code of the reason of cancelation
- `cancelationReason_display`: string with the reason of cancelation
- `verwijzer_zorgverlenerrol_identifier_value`: string with the identifier of the healthcare provider who reffered the patient. Currently not used.
- `BIRTH_YEAR`: integer containing the birthyear of the patient
- `address_postalCodeNumbersNL`: integer containing the first 4 digits of the postalcode of the patient

### Data Splits

The dataset is split in a train and test set by using the first 80% as training and the last 20% as test.
During model training stratified group 5-fold cross validation is used on the training data. Using this cross validation technique ensures that a patient can never be both in the train and test fold at the same time. 

The sizes of the splits are as follows:

|                       | train  | test  |
|-----------------------|-------:|------:|
| Total dataset         | 216724 | 54182 |

## Dataset Creation

### Curation Rationale

The dataset is curated by the Data science team of Digital Health for the purpose of training a machine learning model to predict no-show at the outpatient clinics.

### Source Data

All data is extracted from the Data Platform maintained by the UMCU.

#### Initial Data Collection and Normalization

Data is collected using a SQL query which can be found [here](raw/data_export.sql).

#### Who are the source data producers?

The data is collected from HiX, where most of the fields are filled in by humans, this means that datetimes fields can be misleading sometimes and different clinics use different codes. All the data that is used for declaring health care however should be properly filled, like the status of an appointment. 

The data consists of all patients of the participating clinics at the UMC Utrecht. The demographics of the data are therefore the patient groups that frequent the participating clinics. 

### Annotations

The target variable of no-shows should be inferred from the data as follows:
If the appointment was cancelled and the cancellationReasonCode is on of: "M", "C2", "C3", "0000000010", "D1", "N", "E1", than the status is no-show.
Appointments that have status `booked` are in the future and therefore should be predicted. All other observations are `show`.

### Personal and Sensitive Information

The data contains identity categories like the birthyear, postalcode and information on the outpatient clinic where they have their appointment. The outpatient clinic data could be considered sensitive. Individuals can't be directly identified from the dataset, but when linking it to other datasets it might be possible to infer the individuals. Therefore this data is not shared outside the UMC Utrecht or with other departments within the UMCU. 

In an effort to increaze the anonymity of the patients, only the birthyear is used instead of the birth date and the first 4 numbers of the postalcode. Furthermore we use specialization instead of the specific clinic, so it is harder to infer which treatment the patient received.

## Considerations for Using the Data

### Social Impact of Dataset
The dataset could impact society by reducing waiting times for clinic appointments, by recuding the amount of no-shows. The negative effects of this dataset are minimal. It is not possible to deny patients care, the only personal negative effect. 
Please discuss some of the ways you believe the use of this dataset will impact society.

The statement should include both positive outlooks, such as outlining how technologies developed through its use may improve people's lives, and discuss the accompanying risks. These risks may range from making important decisions more opaque to people who are affected by the technology, to reinforcing existing harmful biases (whose specifics should be discussed in the next section), among other considerations.

Also describe in this section if the proposed dataset contains a low-resource or under-represented language. If this is the case or if this task has any impact on underserved communities, please elaborate here.

### Discussion of Biases
While a lot of care has been given to reducing (sensitive) personal data and focus mostly on behavioural data (number of no shows, minutes late for appointment etc.), it might still be possible to infer specific demographic information based on postalcode and age. 

The data has some inherent bias, namely the population consists of only those patients that have appointments at the UMCU. Since the UMCU is a university medical center that has certain specializations the population will not be a good representation of the entire population in the region. 

This data might therefore not scale well to other medical centers and is meant to be used only at the UMCU.

### Other Known Limitations

-

## Additional Information

### Dataset Curators

This dataset is collected by Ruben Peters with the help of Rosemarijn Looije.

### Licensing Information

This dataset has no license, since it's not meant to be shared.

### Citation Information

-

### Contributions

Thanks to [@ingmarloohuis](https://github.com/ingmarloohuis) and [@rubenpeters91](https://github.com/rubenpeters91).