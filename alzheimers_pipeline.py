import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.feature_selection import SelectKBest, f_classif

# Create output folder structure
directories = [
    "outputs",
    "outputs/confusion_matrices",
    "outputs/roc_curves",
    "outputs/precision_recall",
    "outputs/feature_importance",
    "outputs/metrics"
]
for d in directories:
    os.makedirs(d, exist_ok=True)


def plot_confusion_matrix(cm, ax, title):
    cax = ax.matshow(cm, cmap='Blues')

    for (i, j), z in np.ndenumerate(cm):
        ax.text(j, i, f'{z}', ha='center', va='center',
                color='black' if z < cm.max()/2 else 'white')

    ax.set_title(title)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Low Risk', 'High Risk'])
    ax.set_yticklabels(['Low Risk', 'High Risk'])


def main():
    print("🔹 Starting Alzheimer's ML Pipeline...")

    # Load dataset
    df = pd.read_csv("alzheimers_disease_data.csv")
    print("✅ Data Loaded:", df.shape)

    # Drop irrelevant columns
    df = df.drop(columns=[col for col in ['PatientID', 'DoctorInCharge'] if col in df.columns])

    # Features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Diagnosis' in numeric_cols:
        numeric_cols.remove('Diagnosis')

    X = df[numeric_cols]
    y = df['Diagnosis']

    # Handle missing values
    imputer = SimpleImputer(strategy='mean')
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    print("\n🔹 Performing Feature Selection...")

    # ------------------------
    # METHOD 1: Random Forest Feature Importance
    # ------------------------
    rf_selector = RandomForestClassifier(random_state=42)
    rf_selector.fit(X, y)
    importances = rf_selector.feature_importances_
    
    top_n = 5
    rf_indices = np.argsort(importances)[::-1][:top_n]
    rf_features = [X.columns[i] for i in rf_indices]

    # ------------------------
    # METHOD 2: SelectKBest (Statistical Method)
    # ------------------------
    selector = SelectKBest(score_func=f_classif, k=5)
    X_new = selector.fit_transform(X, y)
    
    kbest_indices = selector.get_support(indices=True)
    kbest_features = [X.columns[i] for i in kbest_indices]

    # Combine unique selected features
    selected_features = list(set(rf_features + kbest_features))
    print("Selected Features:", selected_features)

    with open("outputs/selected_features.txt", "w") as f:
        f.write("Selected Features:\n")
        for item in selected_features:
            f.write(f"- {item}\n")
    print("Saved: outputs/selected_features.txt")

    # VISUALIZATION
    plt.figure(figsize=(12, 6))
    
    all_indices = np.argsort(importances)[::-1]
    sorted_importances = importances[all_indices]
    sorted_features = [X.columns[i] for i in all_indices]
    
    colors = ['orange' if feat in selected_features else 'skyblue' for feat in sorted_features]
    
    plt.bar(range(len(sorted_features)), sorted_importances, color=colors)
    plt.xticks(range(len(sorted_features)), sorted_features, rotation=90)
    plt.xlabel("Features")
    plt.ylabel("Importance Score")
    plt.title("Feature Selection (Random Forest Importances)")
    plt.tight_layout()
    fs_filepath = "outputs/feature_importance/feature_selection.png"
    plt.savefig(fs_filepath)
    print("Saved:", fs_filepath)
    plt.close()

    # Use selected features instead of full feature set
    X = X[selected_features]

    # Train-test split (FIXED)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scaling
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

    # Models (FIXED)
    models = {
        'Random Forest': RandomForestClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'KNN': KNeighborsClassifier()
    }

    results = []
    curves = {}
    trained_models = {}

    print("\n🔹 Training Models...")

    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_prob)

        cm = confusion_matrix(y_test, y_pred)

        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1 Score': f1,
            'ROC-AUC': roc_auc
        })

        # Curves
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        pr_prec, pr_rec, _ = precision_recall_curve(y_test, y_prob)

        curves[name] = {
            'cm': cm,
            'fpr': fpr,
            'tpr': tpr,
            'pr_prec': pr_prec,
            'pr_rec': pr_rec
        }

    # Results table
    results_df = pd.DataFrame(results).set_index('Model')
    results_df = results_df.sort_values(by=['F1 Score'], ascending=False)

    print("\n📊 MODEL COMPARISON:\n")
    print(results_df)

    metrics_csv_path = "outputs/metrics/model_metrics.csv"
    results_df.to_csv(metrics_csv_path)
    print("Saved:", metrics_csv_path)

    print("\n🏆 BEST MODEL:")
    print(results_df.iloc[0])

    # ========================
    # CONFUSION MATRICES
    # ========================
    for name in models:
        clean_name = name.lower().replace(" ", "_")
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_confusion_matrix(curves[name]['cm'], ax, f"{name}")
        filepath = f"outputs/confusion_matrices/{clean_name}.png"
        plt.savefig(filepath)
        print("Saved:", filepath)
        plt.close()

    # ========================
    # INDIVIDUAL ROC CURVES
    # ========================
    for name in models:
        clean_name = name.lower().replace(" ", "_")
        plt.figure()
        plt.plot(curves[name]['fpr'], curves[name]['tpr'], label=name)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title(f"ROC Curve - {name}")
        plt.legend()
        filepath = f"outputs/roc_curves/roc_{clean_name}.png"
        plt.savefig(filepath)
        print("Saved:", filepath)
        plt.close()

    # ========================
    # COMBINED ROC
    # ========================
    plt.figure()
    for name in models:
        plt.plot(curves[name]['fpr'], curves[name]['tpr'], label=name)

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Combined ROC Curve")
    plt.legend()
    filepath = "outputs/roc_curves/combined_roc.png"
    plt.savefig(filepath)
    print("Saved:", filepath)
    plt.close()

    # ========================
    # PRECISION-RECALL CURVE
    # ========================
    plt.figure()
    for name in models:
        plt.plot(curves[name]['pr_rec'], curves[name]['pr_prec'], label=name)

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    filepath = "outputs/precision_recall/precision_recall.png"
    plt.savefig(filepath)
    print("Saved:", filepath)
    plt.close()

    # ========================
    # METRIC COMPARISON CHARTS
    # ========================
    metrics_mapping = {
        'Accuracy': 'accuracy.png',
        'Precision': 'precision.png',
        'Recall': 'recall.png',
        'F1 Score': 'f1_score.png'
    }
    for metric, filename in metrics_mapping.items():
        filepath = f"outputs/metrics/{filename}"
        plt.figure()
        plt.bar(results_df.index, results_df[metric], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        plt.xlabel("Models")
        plt.ylabel(metric)
        plt.title(f"Model Comparison - {metric}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(filepath)
        print("Saved:", filepath)
        plt.close()

    # ========================
    # FEATURE IMPORTANCE
    # ========================
    rf = trained_models['Random Forest']
    importances = rf.feature_importances_
    indices = np.argsort(importances)

    plt.figure()
    plt.barh(range(len(indices)), importances[indices])
    plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
    plt.xlabel("Relative Importance")
    plt.title("Feature Importance (Random Forest)")
    plt.tight_layout()
    filepath = "outputs/feature_importance/feature_importance.png"
    plt.savefig(filepath)
    print("Saved:", filepath)
    plt.close()

    # ========================
    # SAVE MODEL
    # ========================
    model_path = "outputs/rf_alzheimers_model.pkl"
    scaler_path = "outputs/scaler.pkl"
    pickle.dump(rf, open(model_path, "wb"))
    pickle.dump(scaler, open(scaler_path, "wb"))
    print("Saved:", model_path)
    print("Saved:", scaler_path)

    print("\n✅ All outputs saved in /outputs folder")
    print("Files created:")
    for root, dirs, files in os.walk("outputs"):
        for file in files:
            print(os.path.join(root, file))
    print("🎯 DONE")


if __name__ == "__main__":
    main()