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

## Deploying to PositConnect

To deploy to PositConnect install rsconnect (`pip install rsconnect-python`) and run (in case of a dash app):
```{bash}
rsconnect deploy dash --server https://rsc.ds.umcutrecht.nl/ --api-key <(user specific key)> --entrypoint run.app:app .
```

## Documentation
Generate the Sphinx documentation as follows:

```
sphinx-build -b html docs docs/_build
```
