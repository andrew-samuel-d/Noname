import os
import json
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from xgboost import XGBClassifier


# =====================================================
# FEATURES
# =====================================================

FEATURE_ORDER = [
    "business_age_years",
    "monthly_upi_volume",
    "monthly_bank_volume",
    "monthly_cash_volume",
    "gst_filing_regularity",
    "gst_turnover",
    "bounce_frequency",
    "avg_monthly_balance",
    "income_stability",
    "seasonality_score",
    "loan_default_history"
]


# =====================================================
# LOAD DATASET
# =====================================================

df = pd.read_csv(
    "data/synthetic_msme_data.csv"
)

print("Dataset loaded successfully")
print("Total records:", len(df))


# =====================================================
# FEATURES + TARGET
# =====================================================

X = df[FEATURE_ORDER]

y = df["score_label"]


# =====================================================
# TRAIN / TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records :", len(X_test))


# =====================================================
# BASELINE
# =====================================================

majority_class = y_train.mode()[0]

baseline_predictions = [
    majority_class
] * len(y_test)

baseline_accuracy = accuracy_score(
    y_test,
    baseline_predictions
)


# =====================================================
# XGBOOST MODEL
# =====================================================

model = XGBClassifier(
    n_estimators=120,
    max_depth=4,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_lambda=2.0,
    reg_alpha=0.1,
    min_child_weight=2,
    random_state=42,
    eval_metric="logloss"
)


# =====================================================
# TRAIN MODEL
# =====================================================

print("\nTraining XGBoost model...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# =====================================================
# TRAIN ACCURACY
# =====================================================

train_pred = model.predict(
    X_train
)

train_accuracy = accuracy_score(
    y_train,
    train_pred
)


# =====================================================
# TEST PREDICTIONS
# =====================================================

y_pred = model.predict(
    X_test
)

y_probability = model.predict_proba(
    X_test
)[:, 1]


# =====================================================
# TEST METRICS
# =====================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

auc = roc_auc_score(
    y_test,
    y_probability
)


# =====================================================
# TRAIN VS TEST GAP
# =====================================================

train_test_gap = (
    train_accuracy - accuracy
)


# =====================================================
# 5-FOLD CROSS VALIDATION
# =====================================================

print("\nRunning 5-Fold Cross Validation...")

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="accuracy"
)

cv_mean = cv_scores.mean()

cv_std = cv_scores.std()


# =====================================================
# BASELINE IMPROVEMENT
# =====================================================

improvement = (
    accuracy - baseline_accuracy
)

improvement_percentage_points = (
    improvement * 100
)


# =====================================================
# PRINT RESULTS
# =====================================================

print("\n======================================")
print("       XGBOOST MODEL EVALUATION")
print("======================================")

print(
    f"Baseline Accuracy : "
    f"{baseline_accuracy:.4f}"
)

print(
    f"Train Accuracy    : "
    f"{train_accuracy:.4f}"
)

print(
    f"Test Accuracy     : "
    f"{accuracy:.4f}"
)

print(
    f"Precision         : "
    f"{precision:.4f}"
)

print(
    f"Recall            : "
    f"{recall:.4f}"
)

print(
    f"F1 Score          : "
    f"{f1:.4f}"
)

print(
    f"AUC               : "
    f"{auc:.4f}"
)

print("--------------------------------------")

print(
    f"5-Fold CV Mean    : "
    f"{cv_mean:.4f}"
)

print(
    f"5-Fold CV Std     : "
    f"{cv_std:.4f}"
)

print("--------------------------------------")

print(
    f"Train-Test Gap    : "
    f"{train_test_gap:.4f}"
)

print(
    f"Improvement       : "
    f"{improvement_percentage_points:.2f} "
    f"percentage points"
)

print("======================================")


# =====================================================
# CLASSIFICATION REPORT
# =====================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# =====================================================
# CONFUSION MATRIX
# =====================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)


# =====================================================
# CREATE MODEL DIRECTORY
# =====================================================

os.makedirs(
    "model",
    exist_ok=True
)


# =====================================================
# CONFUSION MATRIX GRAPH
# =====================================================

plt.figure(
    figsize=(6, 5)
)

plt.imshow(cm)

plt.title(
    "XGBoost Confusion Matrix"
)

plt.xlabel(
    "Predicted Class"
)

plt.ylabel(
    "Actual Class"
)

plt.xticks(
    [0, 1],
    [
        "Negative (0)",
        "Positive (1)"
    ]
)

plt.yticks(
    [0, 1],
    [
        "Negative (0)",
        "Positive (1)"
    ]
)

for i in range(2):

    for j in range(2):

        plt.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center"
        )

plt.tight_layout()

plt.savefig(
    "model/confusion_matrix.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# =====================================================
# FEATURE IMPORTANCE
# =====================================================

importance = model.feature_importances_

feature_importance = pd.DataFrame({

    "feature": FEATURE_ORDER,

    "importance": importance

})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")

print(
    feature_importance
)


# =====================================================
# FEATURE IMPORTANCE GRAPH
# =====================================================

plt.figure(
    figsize=(10, 6)
)

plt.barh(
    feature_importance["feature"],
    feature_importance["importance"]
)

plt.xlabel(
    "Importance"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "XGBoost Feature Importance"
)

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "model/feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# =====================================================
# SAVE MODEL
# =====================================================

model.save_model(
    "model/xgb_model.json"
)

# Save feature importance JSON for API consumption
feature_importance_list = [
    {
        "feature": row["feature"],
        "importance": round(float(row["importance"]), 4)
    }
    for _, row in feature_importance.iterrows()
]

with open(
    "model/feature_importance.json",
    "w"
) as f:
    json.dump(
        feature_importance_list,
        f,
        indent=4
    )


# =====================================================
# SAVE ALL METRICS
# =====================================================

metrics = {

    "baseline_accuracy":
        round(
            float(baseline_accuracy),
            4
        ),

    "train_accuracy":
        round(
            float(train_accuracy),
            4
        ),

    "test_accuracy":
        round(
            float(accuracy),
            4
        ),

    "accuracy":
        round(
            float(accuracy),
            4
        ),

    "precision":
        round(
            float(precision),
            4
        ),

    "recall":
        round(
            float(recall),
            4
        ),

    "f1_score":
        round(
            float(f1),
            4
        ),

    "auc":
        round(
            float(auc),
            4
        ),

    "cross_validation_mean":
        round(
            float(cv_mean),
            4
        ),

    "cross_validation_std":
        round(
            float(cv_std),
            4
        ),

    "train_test_gap":
        round(
            float(train_test_gap),
            4
        ),

    "improvement_percentage_points":
        round(
            float(improvement_percentage_points),
            2
        )
}


with open(
    "model/metrics.json",
    "w"
) as f:

    json.dump(
        metrics,
        f,
        indent=4
    )


# =====================================================
# FINAL OUTPUT
# =====================================================

print("\n======================================")
print("Files created:")
print("model/xgb_model.json")
print("model/metrics.json")
print("model/confusion_matrix.png")
print("model/feature_importance.png")
print("======================================")
