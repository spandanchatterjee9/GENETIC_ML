import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def compute_metrics():
    print("--- 1. Dataset Details ---")
    df = pd.read_csv("alzheimers_disease_data.csv")
    print(f"Total number of rows (records): {df.shape[0]}")
    
    # Drop irrelevant columns
    df = df.drop(columns=[col for col in ['PatientID', 'DoctorInCharge'] if col in df.columns])
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Diagnosis' in numeric_cols:
        numeric_cols.remove('Diagnosis')
        
    X = df[numeric_cols]
    y = df['Diagnosis']
    
    print(f"Number of original features: {X.shape[1]}")
    print(f"Feature names:\n{list(X.columns)}\n")

    print("--- 2. Validation & Preprocessing ---")
    imputer = SimpleImputer(strategy='mean')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    # Feature selection matching pipeline
    rf_selector = RandomForestClassifier(random_state=42)
    rf_selector.fit(X_imputed, y)
    importances = rf_selector.feature_importances_
    rf_features = [X_imputed.columns[i] for i in np.argsort(importances)[::-1][:5]]

    selector = SelectKBest(score_func=f_classif, k=5)
    selector.fit(X_imputed, y)
    kbest_features = [X_imputed.columns[i] for i in selector.get_support(indices=True)]

    selected_features = list(set(rf_features + kbest_features))
    X_selected = X_imputed[selected_features]
    print(f"Features selected for model: {len(selected_features)} ({selected_features})\n")

    print("Train-test split used: 80% Train, 20% Test (Stratified)\n")
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_selected.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_selected.columns)

    rf = RandomForestClassifier(random_state=42)
    
    # Cross validation on training data
    cv_scores = cross_val_score(rf, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"Cross-validation (5-fold) accuracy scores: {[round(s, 4) for s in cv_scores]}")
    print(f"Mean Cross-validation accuracy: {cv_scores.mean() * 100:.2f}%\n")

    print("--- 3. Model Performance ---")
    rf.fit(X_train_scaled, y_train)
    y_pred = rf.predict(X_test_scaled)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"Final Accuracy:  {acc * 100:.2f}%")
    print(f"Precision:       {prec * 100:.2f}%")
    print(f"Recall:          {rec * 100:.2f}%")
    print(f"F1-score:        {f1 * 100:.2f}%")
    print("Confusion Matrix:")
    print(cm)

if __name__ == "__main__":
    compute_metrics()
