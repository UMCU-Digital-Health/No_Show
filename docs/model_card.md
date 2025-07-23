<!-- Adapted from hugging face template: https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/templates/modelcard_template.md -->

# Model Card for No-Show Prediction Model

This model predicts whether a patient will not show up for a scheduled medical appointment based on historical appointment data.

## Model Details

### Model Description

This model uses patient appointment data to predict the likelihood of a no-show. It is intended to help healthcare providers optimize scheduling and reduce missed appointments.

- **Developed by:** R. Peters
- **Model type:** Classification (binary)
- **Language(s) (NLP):** N/A (tabular data)
- **License:** MIT
- **Finetuned from model [optional]:** N/A

### Model Sources [optional]

- **Repository:** [No_Show GitHub Repo](https://github.com/rpeters7/No_Show)
- **Paper [optional]:** TBA

## Uses

### Direct Use

The intended use of this model is to support the call center in prioritizing calls to patients who are at high risk of not attending their appointments. This can help reduce the number of missed appointments and improve patient care.

### Out-of-Scope Use
Not suitable for use in clinical decision-making or for penalizing patients based on their predicted no-show risk. The model should not be used to deny care or access to services based on predictions.

## Bias, Risks, and Limitations

The model may reflect biases present in the historical appointment data, such as socioeconomic or demographic factors. Predictions should be interpreted with caution.

### Recommendations

Users should be aware of potential biases and limitations. Furthermore, users should know that a high-risk prediction does not guarantee a no-show, and the model should be used as a tool to assist in decision-making rather than as a definitive judgment.

## How to Get Started with the Model

To use the No-Show prediction model, you can follow these steps:
1. **Install the package**: Use pip or uv to install the required dependencies.
   ```bash
   pip install -r requirements.txt
   ```
   or
   ```bash
   uv sync
   ```
2. **Run the training pipeline**: Execute the training pipeline to train the model on your data.
   ```bash
   train_no_show --skip-export  # skip the export step if you already have the data
    ```
3. **Make predictions using the API**: Use the trained model to make predictions on new appointment data.
    ```bash
    python run/app.py
    ```

## Training Details

### Training Data

The model was trained on appointment data including features such as age, gender, scheduled date, and previous no-shows. See [dataset card](dataset_card.md) for details.

### Training Procedure 

Standard preprocessing steps were applied, including handling missing values and using cutoffs for certain features.

#### Training Hyperparameters

For the training of the model grid search was used to find the best hyperparameters. The following hyperparameters were used:

- **Model type:** HistGradientBoostingClassifier
- **Hyperparameters:**
    - `max_iter`: 300
    - `learning_rate`: 0.05


## Evaluation

The model was evaluated using a held-out test set on AUC-ROC and calibration metrics. Furthermore the model was evaluated during a pilot and subsequently in a RCT study.
Both the pilot and RCT indicated that the model in combination with calling patients is effective in reducing no-shows.

### Testing Data, Factors & Metrics

#### Testing Data

See [dataset card](dataset_card.md)

#### Metrics

AUC-ROC and calibration metrics were used to assess performance.

### Results

The model achieved an AUC-ROC of 0.77 on the test set and was well-calibrated.

## Environmental Impact [optional]

Since the model is trained and deployed on an on-premise server, the environmental impact is relatively low compared to cloud-based solutions. However, it is important to consider the carbon emissions associated with the hardware used for training and inference.

## Technical Specifications [optional]

### Model Architecture and Objective

The model is a binary classifier trained on tabular data using scikit-learn.

### Compute Infrastructure

Trained on a local machine used for development by the AI for Health team at UMC Utrecht.

#### Hardware

The model can be trained on a standard laptop or desktop with sufficient RAM and CPU power. For larger datasets, a machine with more resources may be required.

#### Software

See the [requirements.txt](https://raw.githubusercontent.com/UMCU-Digital-Health/No_Show/refs/heads/main/requirements.txt) and [pyproject.toml](https://raw.githubusercontent.com/UMCU-Digital-Health/No_Show/refs/heads/main/pyproject.toml) files for the software dependencies required to run the model.

## Glossary [optional]

- **No-show:** A patient who does not attend a scheduled appointment or cancels/reschedules it within 24 hours of the appointment time.

## More Information [optional]

See the repository README for further details.

## Model Card Authors [optional]

* R. Peters

## Model Card Contact

* rpeters7@gmail.com
