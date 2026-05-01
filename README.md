# Alzheimer's Risk Predictor (GENETIC_ML)

AI-powered Alzheimer’s risk predictor using Machine Learning, featuring a Flask backend and an interactive glassmorphism-based frontend for real-time medical risk assessment.

---

## 🚀 Features

- **Machine Learning Integration:** Random Forest model trained on patient health data to predict Alzheimer’s risk  
- **Model Optimization:** Applied feature selection to reduce 32 features to 5 key predictors  
- **Performance Evaluation:** Achieved 94.65% accuracy with 5-fold cross-validation accuracy of 94.94%  
- **Modern User Interface:** Responsive frontend with glassmorphism aesthetics  
- **RESTful API:** Flask backend that processes input data and returns real-time predictions  

---

## 📊 Model Performance

- **Dataset Size:** 2,149 records  
- **Original Features:** 32  
- **Selected Features:** 5  

### Evaluation Metrics
- **Accuracy:** 94.65%  
- **Precision:** 92.72%  
- **Recall:** 92.11%  
- **F1-score:** 92.41%  

### Validation
- Train-Test Split: 80% train, 20% test (stratified)  
- Cross-validation: 5-fold (94.94% average accuracy)  

---

## Project Structure


GENETIC_ML/
│
├── app.py # Flask backend (API + server)
├── alzheimers_pipeline.py # Data preprocessing, training, feature selection
├── evaluate_model.py # Model evaluation (metrics, confusion matrix)
├── static/ # CSS, JS, frontend assets
├── templates/ # HTML templates
├── *.pkl # Trained model & scaler (generated locally)
└── README.md
