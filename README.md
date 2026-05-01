# Alzheimer's Risk Predictor (GENETIC_ML)

AI-powered Alzheimer’s risk predictor using Machine Learning, featuring a Flask backend and an interactive glassmorphism-based frontend for real-time medical risk assessment.

---

## Features

- **Machine Learning Integration:** Random Forest model trained on patient health data to predict Alzheimer’s risk  
- **Model Optimization:** Applied feature selection to reduce 32 features to 5 key predictors  
- **Performance Evaluation:** Achieved 94.65% accuracy with 5-fold cross-validation accuracy of 94.94%  
- **Modern User Interface:** Responsive frontend with glassmorphism aesthetics  
- **RESTful API:** Flask backend that efficiently processes input data and returns real-time predictions  

---

## Project Structure

- `app.py`: Main Flask server and REST API endpoints  
- `alzheimers_pipeline.py`: Data preprocessing, feature selection, model training, and saving pipeline  
- `evaluate_model.py`: Model evaluation script (accuracy, precision, recall, F1-score, confusion matrix)  
- `static/`: Contains frontend assets (CSS, JavaScript)  
- `templates/`: Contains HTML templates (e.g., `index.html`)  
- `*.pkl`: Serialized Random Forest model and StandardScaler (generated during training, not included in repository)  

---

## Model Performance

- **Dataset Size:** 2,149 records  
- **Original Features:** 32  
- **Selected Features:** 5  

### Evaluation Metrics
- Accuracy: 94.65%  
- Precision: 92.72%  
- Recall: 92.11%  
- F1-score: 92.41%  

### Validation
- Train-Test Split: 80% train, 20% test (stratified)  
- Cross-validation: 5-fold (94.94% average accuracy)  

---

## Setup & Execution

### 1. Installation

It is recommended to use a virtual environment. Install dependencies:

```bash
pip install flask flask-cors pandas scikit-learn numpy
