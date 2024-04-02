# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
