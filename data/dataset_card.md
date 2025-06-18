## Dataset Description

- **Repository:** [https://github.com/UMCU-Digital-Health/No_Show](https://github.com/UMCU-Digital-Health/No_Show)
- **Leaderboard:** Current best model has an AUC of 0.76
- **Point of Contact:** [Ruben Peters](mailto:r.peters-7@umcutrecht.nl)

Based on the dataset card template from huggingface, which can be found [here](https://github.com/huggingface/datasets/blob/main/templates/README_guide.md#table-of-contents).

### Dataset Summary

The dataset consists of all appointments created between January 2015 and June 2024. It combines data from different Data platform tables, namely Appointment, HealthCareService, Polyklinisch_consult, Patient and Patient_address. It uses HealthCareService specialtycodes to filter on clinic and excludes appointments that are booked.

### Supported Tasks and Leaderboards

- `Classification`: The dataset can be used to train a model for classifying no-shows at the clinics in the UMCU. Success on this task is typically measured by achieving a high AUC score. The performance of the best model is currently around 0.76.

### Languages

The dataset is mostly Dutch. However, some columns (that follow FHIR standards) are in English.

## Dataset Structure

### Data Instances

The input data for the prediction is structured as follows:

```{json}
{
  "APP_ID": "5678",
  "pseudo_id": "1ch5k",
  "hoofdagenda": "Revalidatie en Sport",
  "specialty_code": "REV",
  "soort_consult": "Controle fysiek",
  "afspraak_code": "CG63",
  "start": "1717232400000",
  "end": "1717234200000",
  "gearriveerd": "1717232590000",
  "created": "1713366900000",
  "minutesDuration": "30",
  "status": "finished",
  "status_code_original": "J",
  "mutationReason_code": null,
  "mutationReason_display": null,
  "BIRTH_YEAR": "1994",
  "address_postalCodeNumbersNL": "3994",
  "name": "Q5",
  "description": "receptie op Q5",
  "name_text": "C. Kent",
  "name_given1_callMe": "Clark",
  "telecom1_value": "0683726384",
  "telecom2_value": "112",
  "telecom3_value": null,
  "birthDate: "679418100000"
  }
```

Every observation contains all the information of a single appointment. When predicting for a single appointment all the previous appointments of the patient also need to be included as they can be used for feature engineering. The last 6 fields are considered sensitive and are only stored for the purspose of calling and overwritten when a new prediction is made.

### Data Fields

Below you can find the datafields present in the dataset. The datafields are the result of running the query on the dataplatform, most of the fields are the names from the columns in the data platform, some are changed in the query (like `HCS_ID`):

- `APP_ID`: string with the identifier of the Appointment, for example `"1573125974"`
- `pseudo_id`: string of the hashed patient id, for example `"JE994ND3Y30XN"`
- `hoofdagenda`: string with the name of the main HiXagenda, for example `"Cardiologie"`
- `specialty_code`: string with the specialty code of the HealthCareService, for example: `"REV"`, `"KAP"`, `"SPO"`, `"LON"`
- `soort_consult`: string with consult type, mainly used to filter out phone appointments, for example: `"Telefonisch"`, `"Controle fysiek"`
- `afspraakcode`: string with the code for `soort_consult`, for example: `"GT91"`
- `start`: UNIX timestamp in ms with the start date of the appointment, for example: `1717232400000`
- `end`: UNIX timestamp in ms with the end date of the appointment, for example: `1717234200000`
- `gearriveerd`: UNIX timestamp in ms with the date of arrival of the patient, for example: `1717232590000`
- `created`: UNIX timestamp in ms with the creation date of the appointment, for example: `1713366900000`
- `minutesDuration`: integer indicating the duration of the appointment in minutes, for example: `30`
- `status`: string with the status of the appointment, for example: `"planned"` or `"finished"`.
- `status_code_original`: string with the status of the appointent, for example: `"J"` or `"N"`
- `mutationReason_code`: string with the code of the reason of mutation, for example `null` or `"N"`
- `mutationReason_display`: string with the reason of mutation, for example: `"No Show"` or `null`
- `BIRTH_YEAR`: integer containing the birthyear of the patient, for example `1991`
- `address_postalCodeNumbersNL`: integer containing the first 4 digits of the postalcode of the patient, for example `3994`
- `name`: Code of the outpatient clinic reception. The first letter usually represents the area in the UMCU, for example: `"Receptie 10A"` *only used during prediction* 
- `description`: Description of the outpatient clinic reception, for example `"receptie van cardiologie"` *only used during prediction*
- `name_text`: The name of the patient, for example `"John H. Doe"` *only used during prediction*
- `name_given1_callMe`: The first name of the patient, for example `"John"` *only used during prediction*
- `telecom1_value`: The mobile phone number of the patient (if known), for example: `"06-73496410"` *only used during prediction*
- `telecom2_value`: The home phone number of the patient (if known), for example: `"0481-643995"` *only used during prediction*
- `telecom3_value`: The other phone number of the patient (if known), for example: `null` *only used during prediction*
- `birthDate`: UNIX timestamp in ms of the birthdate of the patient, needed for validation when calling, for example `679418100000` *only used during prediction*

### Data Splits

The dataset is split in a train and test set by using the first 80% as training and the last 20% as test.
During model training stratified group 5-fold cross validation is used on the training data. Using this cross validation technique ensures that a patient can never be both in the train and test fold at the same time. 

The sizes of the splits are as follows:

|                       | train  | test  |
|-----------------------|-------:|------:|
| Total dataset         | 298142 | 74536 |

## Dataset Creation

### Curation Rationale

The dataset is curated by the Data science team of Digital Health for the purpose of training a machine learning model to predict no-show at the outpatient clinics.

### Source Data

All data is extracted from the Data Platform maintained by the UMCU.

#### Initial Data Collection and Normalization

Data is collected using a SQL query which can be found [here](raw/data_export.sql).
The postal codes are exported from [here](https://download.geonames.org/export/zip/NL.zip).

#### Who are the source data producers?

The data is collected from HiX, where most of the fields are filled in by humans, this means that datetimes fields can be misleading sometimes and different clinics use different codes. All the data that is used for declaring health care however should be properly filled, like the status of an appointment. 

The data consists of all patients of the participating clinics at the UMC Utrecht. The demographics of the data are therefore the patient groups that frequent the participating clinics. 

### Annotations

The target variable of no-shows should be inferred from the data as follows:
If the appointment was cancelled and the mutationReason_code is `"N"` than the status is no-show. All other observations are `show`.

Appointments that have status `planned` or `in-progress` and are excluded from the train data. When predicting all appointments should have status `planned`, except for the historic predictions of the patients.

### Personal and Sensitive Information

The data contains identity categories like the birthyear, postalcode and information on the outpatient clinic where they have their appointment. The outpatient clinic data could be considered sensitive. Individuals can't be directly identified from the dataset, but when linking it to other datasets it might be possible to infer the individuals. Therefore this data is not shared outside the UMC Utrecht or with other departments within the UMCU. 

In an effort to increase the anonymity of the patients, only the birthyear is used instead of the birth date and the first 4 numbers of the postalcode. Another reason for only using the first 4 numbers of the postal code is to reduce bias in the model. Furthermore we use specialization instead of the specific clinic, so it is harder to infer which treatment the patient received. Finally to prevent identification on the patient identifier number, we hash the patient id with a salt.

The data is not shared within or outside the UMCU and can only be accessed by the development team working on the no-show project.

The prediction data does contain sensitive info, like the name and phone number of the patient. This is only used to call the patient and those data is removed after each day.

## Considerations for Using the Data

### Social Impact of Dataset
The dataset could impact society by reducing waiting times for clinic appointments, by recuding the amount of no-shows. The negative effects of this dataset are minimal. It is not possible to deny patients care, the only personal negative effect. 
Please discuss some of the ways you believe the use of this dataset will impact society.

The statement should include both positive outlooks, such as outlining how technologies developed through its use may improve people's lives, and discuss the accompanying risks. These risks may range from making important decisions more opaque to people who are affected by the technology, to reinforcing existing harmful biases (whose specifics should be discussed in the next section), among other considerations.

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