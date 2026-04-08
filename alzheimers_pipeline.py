
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
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
    ax.set_xticklabels(['Low Risk (0)', 'High Risk (1)'])
    ax.set_yticklabels(['Low Risk (0)', 'High Risk (1)'])

def main():
    print("🔹 Starting Alzheimer's Disease Prediction Pipeline...")

    # Load Data
    try:
        df = pd.read_csv('alzheimers_disease_data.csv')
        print(f"Data loaded successfully! Shape: {df.shape}")
    except FileNotFoundError:
        print("Dataset not found!")
        return

    # Preprocessing
    df = df.drop(columns=[col for col in ['PatientID', 'DoctorInCharge'] if col in df.columns])

    feature_cols = ['Age', 'BMI', 'SystolicBP', 'CholesterolTotal',
                    'MemoryComplaints', 'Confusion', 'Forgetfulness']

    X = df[feature_cols]
    y = df['Diagnosis']

    imputer = SimpleImputer(strategy='mean')
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

    # Models
    models = {
        'Random Forest': RandomForestClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(),
        'KNN': KNeighborsClassifier()
    }

    results = []
    trained_models = {}
    curves = {}

    print("\n🔹 Training Models...")

    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

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

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        pr_prec, pr_rec, _ = precision_recall_curve(y_test, y_prob)

        curves[name] = {
            'cm': cm, 'fpr': fpr, 'tpr': tpr,
            'pr_prec': pr_prec, 'pr_rec': pr_rec
        }

    results_df = pd.DataFrame(results).set_index('Model')
    results_df = results_df.sort_values(by=['F1 Score', 'Recall'], ascending=False)

    print("\n🔹 MODEL COMPARISON")
    print(results_df)

    results_df.to_csv("model_comparison.csv")
    print("✅ Saved model_comparison.csv")

    # Confusion Matrices
    for name in models:
        fig, ax = plt.subplots()
        plot_confusion_matrix(curves[name]['cm'], ax, name)
        plt.savefig(f"confusion_{name}.png")
        plt.close()

    # ROC Curves
    for name in models:
        plt.plot(curves[name]['fpr'], curves[name]['tpr'], label=name)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.legend()
        plt.savefig(f"roc_{name}.png")
        plt.close()

    # Combined ROC
    for name in models:
        plt.plot(curves[name]['fpr'], curves[name]['tpr'], label=name)
    plt.legend()
    plt.savefig("combined_roc.png")
    plt.close()

    # Precision Recall
    for name in models:
        plt.plot(curves[name]['pr_rec'], curves[name]['pr_prec'], label=name)
    plt.legend()
    plt.savefig("precision_recall.png")
    plt.close()

    # Feature Importance
    rf = trained_models['Random Forest']
    importances = rf.feature_importances_
    indices = np.argsort(importances)

    plt.barh(range(len(indices)), importances[indices])
    plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
    plt.savefig("feature_importance.png")
    plt.close()

    # Save Model + Scaler
    pickle.dump(rf, open("rf_alzheimers_model.pkl", "wb"))
    pickle.dump(scaler, open("scaler.pkl", "wb"))

    print("\n✅ Model & Scaler saved!")
    print("🎯 DONE")

if __name__ == "__main__":
    main()

