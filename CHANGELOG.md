# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.3] - 2023-09-19

### Changed
- Predictions in the dashboard are now sorted by date
- The top-n returned predictions are now based on top-n unique patients, not individual appointments
- Added clinic name and clinic number to api

## [1.1.2] - 2023-09-18

### Changed
- API version is now based on package version from pyproject.toml instead of having a seperate value in setup.cfg

### Fixed
- Calculating the day in x working days now works as expected. Previously it was calculated by adding x days and skipping the weekend, but this results in never calling for appointments on Monday-Wednesday. Now working days are calculated correctly (e.g. 3 working days from Thursday is Tuesday).
