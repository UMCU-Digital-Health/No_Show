# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [2.0.4] - 2025-06-11
### Changed
- Columns 'cancelationReason_code', 'cancelationReason_display', and 'cancelationResason_system' in model Appointment are changed respectively to 'mutationReason_code', 'mutationReason_display', and 'mutationReason_system'. 

## [2.0.3] - 2025-06-04

### Changed
- Call_status only displays a telephone icon to the corresponding prediction row in the calling dashboard.

## [2.0.2] - 2025-06-04

### Changed
- Updated the subagendas for Genetics department to remove locations outside of UMCU
- Updated dependencies
- Reran pipeline and retrained model on new export
- Updated the postal code file to include the latest postal codes

## [2.0.1] - 2025-05-27

### Changed
- Updated the database models to reflect result after the database migration

## [2.0.0] - 2025-04-30

Updated major version to 2.0.0 due to breaking changes in the API and database models.

### Changed
- Updated logging for dashboard and API, including better formatting
- Updated code to work on both local SQLite and MSSQL databases, to enable local testing
- Updated database models to use a new PK for predictions
- Updated the API to save moved appointments as a new prediction (instead of overwriting the old one)
- Changed the remove sensitive info script to use the start_date from the api instead of the current timestamp and increased the lookback period to 14 days
- Predict API no longer returns the predictions, but only a message containing the number of predictions
- Updated dependencies

### Added
- Added a local test dataset to use in the API, since the data in the tests folder requires a custom mock config

## [1.6.1] - 2025-04-09

### Changed
- Updated unit tests coverage

## [1.6.0] - 2025-04-08
### Added
- Button in calling dashboard to go to the first patiënt who has not yet been called.
- Warning to first save results in the calling dashboard, to prevent that the call_status remains 'wordt gebeld'. 

### Changed
- Mute_list query to exclude patients who are called today, so that these patients are still visible in the calling dashboard. 

### Removed
- Selectbox for user of calling dashboard to select the call_status. 


## [1.5.7] - 2025-04-15

### Changed
- Updated example .env file
- Updated No-show codes to match recent changes in HiX and moved to config file
- Moved from tomli to build-in tomllib
- Updated requirements


## [1.5.6] - 2025-03-31

### Changed
- Changed 'Bel me niet' from a selectbox option of 'Resultaat gesprek' to a separate checkbox. 

### Added
- Option to show the number of patients who were not called seperatly in the admin dashboard by selecting a checkbox. 


## [1.5.5] - 2025-03-24

### Changed
- Changed data_export.sql and data_prediction.sql to remove appointment codes referring to family conversations. These type of appointments only occured twelve times in the raw data, therefore it is not necessary to train the model again. 

## [1.5.4] - 2025-03-24
### Changed
- Reversed change from clinic_name in ApiPredidiction from clinic back to main agenda.

## [1.5.3] - 2025-03-19
### Added
- Mute patients based on combination patient-clinic, instead of only the last call date of the patient

### Changed
- Changed clinic_name in ApiPrediction to actual clinic name instead of main agenda

### Removed
- Last call date column from ApiPatient table


## [1.5.2] - 2025-02-05

### Added
- Added current username to saved message in calling dashboard

### Changed
- Changed information that fastapi runs once per day to every two hours in README.md

## [1.5.1] - 2024-12-23

### Added
- Error warmings in case no appointments are provided
- Added ssl-certificate fix in deploy script
- Added unit tests for empty predictions

### Changed
- Saving of predictions is now located in helper function
- Updated requirements to solve dependabot alert

## [1.5.0] - 2024-12-10

### Changed
- Upgraded to Python 3.12 and updated all dependencies
- Retrained model on all clinics

### Added
- Added last batch of agandas to config

## [1.4.11] - 2024-12-03

### Changed
- Dashboard now displays a warning when a patient is currently being called, instead of preventing the user from going to the next patient
- Dashboard will give an informative error when a prediction is no longer available, instead of crashing. Furthermore the user can still navigate to the next patient when this occurs
- Patient selection buttons now moved to a separate function
- Refactor render functions to new module

## [1.4.10] - 2024-12-03

### Changed
- Updated agendas to next scale up step and rerun pipelines
- Updated data export script to use data from 2016 instead of 2015 and use the PUB publication.

### Added
- Added a script to export data for model training

## [1.4.9] - 2024-11-18

### Changed
- Updated agendas
- Small fixes to data loading and importing dvclive module

## [1.4.8] - 2024-11-13

### Added
- New clinics added to the queries and config

### Changed
- Updated dependencies

### Removed
- Removed deprecated setup.cfg file

## [1.4.7] - 2024-11-04

### Changed
- Updated manifest files

### Added
- Username now also saved when filling in call response

### Fixed
- Alembic now applies ruff format before linter, to prevent errors when generating migrate scripts

## [1.4.6] - 2024-10-29

### Fixed
- Removed TTL in patient list in calling dashboard and also show patient that were called today to prevent patients from disappearing during calls
- Corrected database column types so databases are identical over different environments

### Added
- Added Alembic for database migrations
- Added a timestamp for call response, so we can track when patients were called


## [1.4.5] - 2024-10-21

### Fixed
- Removed 'sociale pediatrie' from subagendas
- Set mute period to 2 months
- Updated requirements to solve dependabot alert
- Fix the arrived column rename in the dataplatform

## [1.4.4] - 2024-10-21

### Changed
- Added SQL query for RCT export and notebook to export total dataset and small initial analysis

## [1.4.3] - 2024-10-17

### Fixed
- Show predictions for the right treatment group in de monitoring tab of the admin dash
- Fixed x-axis alignment of the monitoring tab graph

### Changed
- Updated KPIs in the KPI tab of the admin dash

## [1.4.2] - 2024-10-14

### Changed
- Removed three subagendas from filtering for Allergologie
- Kind-KNO is a separate agenda (not part of Poli Rood)

## [1.4.1] - 2024-10-10

### Fixed
- Calling dash now both shows main agenda name and TeleQ name to prevent confusion when TeleQ name does not clearly indicate for which clinic the appointment is

### Changed
- clinic phone number is still stored in the database, but no longer shown in the calling dash, since any rescheduling needs to be done through TeleQ

## [1.4.0] - 2024-10-08

### Fixed
- Updated pydantic model to allow empty string for postal code and update birthDate validator

### Added
- Added agenda codes for first scale-up phase

### Changed
- Moved queries to separate folder
- Removed old pilot query and data
- Retrained and deployed model

## [1.3.2] - 2024-10-07

### Fixed
- Postal code is no longer required when using the API, empty postal codes will result in the appointment being dropped later during feature building

## [1.3.1] - 2024-10-03

### Changed
- Use Pydantic for data validation in API
- Updated unit tests to also use pydantic models

## [1.3.0] - 2024-09-25

### Fixed
- admin dashboard now also shows clinics outside of RCT
- moved sql filters to config
- authentication now fails when X_API_KEY environment variable is not set

### Changed
- clinic_name used in dashboard now refers to TeleQ name
- updated requirements


## [1.2.14] - 2024-09-09

### Added
- patient_id to sql_query
- patient id to sensitive info table as hix_number
- showed patient id in dashboard

## [1.2.13] - 2024-08-30

### Fixed
- Fixed issue where 'VELD' afspraken appeared in call list
## [1.2.12] - 2024-08-07

### Changed
- Updated requirements
- Added a format to data-loading functions to prevent pandas warnings

### Fixed
- Fixed dependency issue in fastapi preventing exceptions from being raised, resulting in internal server error for every possible exception

## [1.2.11] - 2024-08-01

### Added
- Added a small agenda "Spieren voor Spieren" outside of the RCT
- Added unit test for adding agendas outside RCT

### Changed
- Changed treatment group to 2 for agendas outside RCT
- Removed unnecessary subagendas for Longziekten and Poli-blauw

## [1.2.10] - 2024-07-24

### Fixed
- Fixed a bug where when the full name of a patient is None, the predict endpoint crashes

## [1.2.9] - 2024-07-16

### Added
- Added Cardiology to the data and retrained model

### Changed
- Updated the dataset card and the test-data to better reflect a possible dataset
- Updated links to the postalcode file URL
- Removed hart functie agenda, too many appointments for this phase, TODO: add at a later stage
- Updated deploy script

## [1.2.8] - 2024-07-17

### Added
- Added an option to select the clinic in the admin dashboard

### Changed
- Updated requirements to solve dependabot alert

## [1.2.7] - 2024-07-09

### Added
- Added a dashboard for monitoring and KPIs during the implementation of the No Show project

## [1.2.6] - 2024-07-03

### Added
- Added a search field to search for patients by their phone number, in case they call back

### Changed
- Sensitive info is now only removed after 7 days, so dashboard users can go back to a previous day, in case a patient calls back
- The button 'start calling' now only appears when a patient has not been called, if a patient has been called (or was unavailable) the patient info is shown, but a warning will be displayed to inform the user that the patient was already called.
- The pilot results notebook has been renamed and updated to show information about the current status of the implementation

## [1.2.5] - 2024-07-02

### Added
- Added package version to about menu in dashboard

### Changed
- Only allow users to move to another page if status is not 'Wordt gebeld', forcing them to log the result
- Changed button text to 'Opslaan', making it clear that it needs to be pressed before anything is saved
- Updated requirements, fixing a dependabot warning about urllib3

## [1.2.4] - 2024-07-01

### Fixed
- Casting of threshold_date in patient list query

## [1.2.3] - 2024-06-24

### Changed
- Retrained model on new export containing Cardiology and RF&S
- Redeployed API to test
- Disabled mute period for RCT and added config to DVC

### Fixed
- Fixed query to also include cardiology

## [1.2.2] - 2024-06-20
- Added Cardiology and RF&S to queries

## [1.2.1] - 2024-06-13

### Changed
- Moved clinic phone numbers and feature enineering settings to a config file
- Removed setting to get top-n patients in dashboard, simply show all patients
- Retrained model and redeployed dashboard and api
- Temporarily removed RF&S clinic appointments

### Fixed
- Removed wrong subagendas from queries
- No longer write dvclive info when running unit tests
- Load default config values if config file is absent (for unit tests)

## [1.2.0] - 2024-06-12

### Changed
- Updated export and rerun pipelines
- Rerun notebook and applied formatting
- Updated dependencies to fix dependabot security alerts
- Redeployed API and Streamlit dash and updated manifest files

### Fixed
- Fixed queries and code to handle missing location info since HiX6.3
- Updated No-Show codes to only use the new 'N' code (HiX 6.3)

## [1.1.1] - 2024-06-03

### Changed
- Added RCT to api
- Create notebook to train model and create fixed bins

## [1.1.0] - 2024-05-27

### Changed
- Added RCT to create control and treatment arm
- Made sure only treatment arm is called


## [1.0.13] - 2024-04-12

### Changed
- Small improvements to model strategy notebook

## [1.0.12] - 2024-04-08

### Changed
- API can now create treatment and control groups to test effectiveness of calling in a RCT

## [1.0.11] - 2024-04-03

### Changed
- Added don't call me list

## [1.0.10] - 2024-03-26

### Changed
- Dashboard now allows for the muting of patient for a prefined period

## [1.0.10] - 2024-04-02

### Changed
- Added notebook for model strategy selection (including clinic or not)
- Updating requirements (solves orjson dependabot alert)
- Added comment to warn about new HiX 6.3 no-show codes

### Fixes
- Updated pandas replace function to solve deprecation warning

## [1.0.9] - 2024-03-21

### Changed
- Experimented with portability and performance over time of different models, see notebook: model_experiments.ipynb
- Updated prev_minutes_early to cutoff at cutoff value instead of 0
- Updated visualisations

## [1.0.8] - 2024-03-21

### Changed
- Dashboard now logs when a call has started to prevent duplicate calls
- Updated queries to match HiX 6.3 codes

### Fixed
- Bug where switching to new date didn't reset pred_idx
- Bug where None values in call_number occured

## [1.0.7] - 2024-03-11

### Changed
- phone number that was used to call patient is now stored

## [1.0.6] - 2024-02-07

### Changed
- Bumped Python, DVC, DVCLive and fastapi versions

## [1.0.5] - 2023-11-27

### Changed
- Updated evaluation notebooks
- Start using nbstripout for removing notebook output

## [1.0.4] - 2023-11-21

### Changed
- Updated pyarrow dependency because of a security risk (this repo is not affected)

## [1.0.3] - 2023-10-09

### Changed
- Remove max patients limit, since the previous upper limit of 50 was not enough.
- Updated queries to match pilot
- Added notebooks for evaluating the pilot
- Updated linter to ruff

## [1.0.2] - 2023-10-05

### Fixed
- Removed 'Hartgroepen 1 t/m 5' from pilot

## [1.0.1] - 2023-09-29

### Fixed
- When predicting with a given start-date, predictions are only made on appointments with status 'booked'. This prevents appointments with status 'cancelled'/'proposed'/'waiting_list' from showing up in the dashboard. 

## [1.0.0] - 2023-09-26
This is the first full release of the no-show project. This release will be used during the pilot-phase and
shared as an open-source repo.

### Changed
- Dashboard displays unknown patient fields as "Onbekend" instead of "None"
- Updated the dataset card
- Updated README
- Updated all package dependencies
- Retrained classifier
- Added a LICENSE

### Fixed
- Filtered out wrong location for outpatient clinics

## [0.1.3] - 2023-09-19

### Changed
- Predictions in the dashboard are now sorted by date
- The top-n returned predictions are now based on top-n unique patients, not individual appointments
- Added clinic name and clinic phone number to api
- Dashboard now shows clinic name and the patient index
- Dashboard now displays the timestamp of the last API request per patient per day
- Dashboard now has the option to show Appointment IDs and pseudonymized patient IDs for debug purposes
- Added a Get Help link to send support e-mail and added a page icon

### Fixed
- Dashboard no longer crashes when trying to display non-existing sensitive patient info. It now shows a message, while still displaying the (anonymized) appointments.
- API now sets appointments that are removed or rescheduled to inactive, so they don't show up in the dashboard
- Patients are removed from the dashboard if all their appointments have status inactive
- Set the column type of the prediction id to varchar, to prevent integer overflow
- Going to a diffent day in the dashboard will reset the patient index, preventing a out of bounds exception

## [0.1.2] - 2023-09-18

### Changed
- API version is now based on package version from pyproject.toml instead of having a seperate value in setup.cfg

### Fixed
- Calculating the day in x working days now works as expected. Previously it was calculated by adding x days and skipping the weekend, but this results in never calling for appointments on Monday-Wednesday. Now working days are calculated correctly (e.g. 3 working days from Thursday is Tuesday).
