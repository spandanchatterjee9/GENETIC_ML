# Model Evaluation & Metrics Report

This document describes the evaluation metrics, validation curves, and model comparison criteria used to select the production Random Forest classifier for early Alzheimer's detection.

---

## 1. Metrics & Definition Guide

For binary medical classification, outputs are evaluated using positive (High Risk) and negative (Low Risk) class predictions:
- **True Positive (TP)**: Correctly flagged High Risk.
- **True Negative (TN)**: Correctly flagged Low Risk.
- **False Positive (FP)**: Healthy flagged as High Risk (Type I Error).
- **False Negative (FN)**: High Risk patient missed by the model (Type II Error).

### Evaluation Metrics Formulas

1. **Accuracy**:
   The percentage of correct predictions out of all cases:
   $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
2. **Precision**:
   The proportion of predicted positive cases that are actually positive. Measures the cost of false alarms:
   $$\text{Precision} = \frac{TP}{TP + FP}$$
3. **Recall (Sensitivity)**:
   The proportion of actual positive cases that the model successfully flags. In clinical settings, high recall is vital to avoid missing sick patients:
   $$\text{Recall} = \frac{TP}{TP + FN}$$
4. **F1 Score**:
   The harmonic mean of Precision and Recall, providing a balanced metric for uneven class distributions:
   $$\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
5. **ROC-AUC (Area Under Receiver Operating Characteristic Curve)**:
   Measures the model's ability to distinguish between classes across all decision thresholds. An AUC of $1.0$ represents a perfect model, while $0.5$ represents random guessing.

---

## 2. Explanation of Performance Visualizations

### Confusion Matrix
* **Meaning**: A grid layout mapping predicted versus actual diagnostic labels.
- **Visual Files**: `outputs/confusion_matrices/` (includes `random_forest.png`, `knn.png`, `logistic_regression.png`, `decision_tree.png`).
- **Interpretation**: Shows where classification errors occur. In clinical diagnostics, minimizing False Negatives (bottom-left quadrant) is prioritized to ensure patients do not go untreated.

### Receiver Operating Characteristic (ROC) Curve
- **Meaning**: Plots the True Positive Rate (Recall) against the False Positive Rate ($FP / (FP + TN)$) across all classification probability thresholds.
- **Visual Files**: `outputs/roc_curves/combined_roc.png` (and individual model plots).
- **Interpretation**: The closer the curve arches toward the top-left corner, the better the model performs. The combined plot shows the Random Forest curve consistently dominating the other classifiers across all thresholds.

### Precision-Recall Curve
- **Meaning**: Plots Precision (y-axis) against Recall (x-axis) for various probability thresholds.
- **Visual File**: `outputs/precision_recall/precision_recall.png`.
- **Interpretation**: Extremely useful for datasets with target imbalances. A high area under this curve represents both high recall (low false negatives) and high precision (low false positives).

### Feature Importances (Gini Impurity reduction)
- **Meaning**: Ranks how much each clinical parameter contributes to split node Gini impurity reduction.
- **Visual File**: `outputs/feature_importance/feature_importance.png`.
- **Interpretation**: Highlights which clinical parameters are most predictive of Alzheimer's risk. For the Random Forest model:
  1. `MemoryComplaints` and `FunctionalAssessment` are the primary predictive features.
  2. `MMSE` and `ADL` contribute moderate predictive signal.
  3. `BehavioralProblems` provides a smaller, yet statistically significant, signal.

---

## 3. Model Comparison & Selection Analysis

Running the pipeline compiled the following validation metrics:

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **94.65%** | **93.29%** | **91.45%** | **92.36%** | **95.00%** |
| **K-Nearest Neighbors (KNN)** | 91.16% | 88.00% | 86.84% | 87.42% | 92.91% |
| **Decision Tree** | 90.47% | 85.81% | 87.50% | 86.65% | 89.79% |
| **Logistic Regression** | 81.40% | 73.68% | 73.68% | 73.68% | 89.03% |

### Why Random Forest Was Selected
The Random Forest Classifier performed best across all evaluation criteria, notably achieving the highest **F1-Score (92.36%)** and **Recall (91.45%)**.
- **Ensemble Robustness**: By bootstrapping training subsets and building multiple independent decision trees, Random Forest avoids overfitting on individual patient records, generalizing better than standard Decision Trees.
- **Non-Linear Handling**: Biometric indicators like `Age`, `BMI`, and `MMSE` scores have complex, non-linear relationships with Alzheimer's onset. Logistic regression fails to capture these relationships, whereas tree splits partition non-linear spaces effectively.
- **Stability with Outliers**: It is highly stable and less sensitive to outliers in clinical features compared to distance-based algorithms like KNN.

### Strengths & Weaknesses
- **Strengths**: High diagnostic accuracy, robust to overfitting, built-in feature importance scoring, and highly reliable classification output.
- **Weaknesses**: More complex to explain compared to simple decision trees, and has higher compute and memory overhead during serialization (larger pickle footprint).
