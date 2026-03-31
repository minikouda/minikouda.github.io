"""
PECARN TBI Prediction Models

This module implements three classification models for predicting
whether a CT scan should be recommended for pediatric patients with
minor head trauma:

1. Kuppermann Clinical Decision Rule (CDR) from Kuppermann et al. 2009
2. Logistic Regression with class imbalance handling
3. Random Forest Classifier
"""

import pandas as pd
import numpy as np
from typing import Dict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, confusion_matrix
)
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class KuppermannCDR:
    """
    Kuppermann Clinical Decision Rule for pediatric TBI.

    Based on Kuppermann et al., Lancet 2009.
    Implements age-stratified prediction rules for children with minor head trauma.

    CT scan is recommended (high risk) if ANY predictor is present.

    For children <2 years:
        1. Altered mental status
        2. Non-frontal scalp haematoma
        3. Loss of consciousness ≥5 seconds
        4. Severe injury mechanism
        5. Palpable skull fracture
        6. Not acting normally per parent

    For children ≥2 years:
        1. Altered mental status
        2. Loss of consciousness
        3. History of vomiting
        4. Severe injury mechanism
        5. Clinical signs of basilar skull fracture
        6. Severe headache
    """

    def __init__(self):
        self.name = "Kuppermann Clinical Decision Rule"
        self.age_threshold_months = 24  # 2 years

    def predict_single(self, row: pd.Series) -> int:
        """
        Predict CT recommendation for a single patient.

        Uses parent/summary columns available in the cleaned dataset:
        AMS, LOCSeparate, LocLen, Vomit, HA_verb, SFxBas, SFxPalp,
        severe_mechanism, ActNorm, Hema.

        Parameters
        ----------
        row : pd.Series
            Patient data

        Returns
        -------
        int
            1 if CT recommended (high risk), 0 if not (very low risk)
        """
        age_months = row.get('AgeInMonth')

        # Handle missing age
        if pd.isna(age_months):
            return 1  # Conservative: recommend CT if age unknown

        # Apply age-specific rules
        # LOCSeparate: 1 = yes (definite), 2 = suspected/unclear, 0 = no
        loc_any = row.get('LOCSeparate') in (1, 2)   # any / suspected LOC
        loc_def = row.get('LOCSeparate') == 1         # definite LOC only

        if age_months < self.age_threshold_months:
            # ── Children <2 years ──────────────────────────────────────────
            # Kuppermann et al. 2009, Table 3 (derivation cohort, <2 yr)
            # CT recommended if ANY of:
            #   1. Altered mental status
            #   2. Non-frontal scalp haematoma  → SFxNonFront (NOT generic Hema)
            #   3. Loss of consciousness ≥5 seconds
            #   4. Severe injury mechanism
            #   5. Palpable skull fracture
            #   6. Not acting normally per parent

            # Predictor 3: LOC ≥5 s.
            # LocLen = duration in seconds. If LOC occurred but duration is
            # unknown (NaN), we conservatively count it as meeting the ≥5 s
            # threshold rather than silently missing a true positive.
            loc_len = row.get('LocLen')
            loc_ge5s = loc_any and (pd.isna(loc_len) or loc_len == 4)

            act_norm = row.get('ActNorm')
            not_acting_normally = (pd.isna(act_norm)) or (act_norm == 0)

            predictors = [
                row.get('ams_any') == 1,              # 1. Altered mental status
                row.get('SFxNonFront', 0) >= 1,      # 2. Non-frontal scalp haematoma
                loc_ge5s,                          # 3. LOC ≥5 seconds
                row.get('severe_mechanism') == 1, # 4. Severe injury mechanism
                row.get('SFxPalp') in (1, 2),     # 5. Palpable skull fracture
                not_acting_normally,               # 6. Not acting normally per parent
            ]
        else:
            # ── Children ≥2 years ──────────────────────────────────────────
            # Kuppermann et al. 2009, Table 4 (derivation cohort, ≥2 yr)
            # CT recommended if ANY of:
            #   1. Altered mental status
            #   2. Loss of consciousness (any)
            #   3. History of vomiting
            #   4. Severe injury mechanism
            #   5. Signs of basilar skull fracture
            #   6. Severe headache
            predictors = [
                row.get('ams_any') == 1,              # 1. Altered mental status
                loc_def,                           # 2. Loss of consciousness (definite)
                row.get('Vomit') == 1,             # 3. History of vomiting
                row.get('severe_mechanism') == 1, # 4. Severe injury mechanism
                row.get('SFxBas') == 1,            # 5. Basilar skull fracture signs
                row.get('HASeverity') == 1,           # 6. Severe headache
            ]

        # Recommend CT if ANY predictor is present
        return int(any(predictors))

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fit method for compatibility with sklearn interface.

        CDR is a rule-based model and doesn't require training.
        """
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict CT recommendations for multiple patients.

        Parameters
        ----------
        X : pd.DataFrame
            Patient data

        Returns
        -------
        np.ndarray
            Binary predictions (1 = recommend CT, 0 = very low risk)
        """
        rows = [self.predict_single(X.iloc[i]) for i in range(len(X))]
        predictions = np.asarray(rows)
        return predictions

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Return probability-like scores for compatibility.

        For CDR, this returns hard 0/1 predictions as probabilities.
        """
        preds = self.predict(X)
        # Return as probability matrix [P(class=0), P(class=1)]
        return np.column_stack([1 - preds, preds])


class LogisticRegressionModel:
    """
    Logistic Regression model with class imbalance handling.

    Features:
    - L2 regularization (Ridge)
    - Class weights to handle imbalance
    - Feature selection based on domain knowledge
    - Missing value imputation
    """

    def __init__(self, C=1.0, class_weight=None, random_state=42):
        """
        Initialize logistic regression model.

        Parameters
        ----------
        C : float, default=1.0
            Inverse of regularization strength
        class_weight : str or dict, default=None
            Weights associated with classes. Defaults to {0: 1, 1: 500}
            to penalize FN 500x more than FP.
        random_state : int, default=42
            Random seed for reproducibility
        """
        if class_weight is None:
            class_weight = {0: 1, 1: 500}
        self.model = LogisticRegression(
            C=C,
            class_weight=class_weight,
            random_state=random_state,
            max_iter=1000,
            solver='lbfgs'
        )
        self.imputer = SimpleImputer(strategy='median')
        self.scaler = StandardScaler()
        self.feature_names = None

    def select_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Select clinically relevant features based on domain knowledge.

        Features selected based on Kuppermann et al. and EDA findings:
        - Age
        - GCS score
        - Clinical signs (AMS, LOC, vomiting, etc.)
        - Injury mechanism
        - Physical exam findings
        """
        feature_list = [
            'AgeInMonth',
            'GCSTotal',
            # AMS composite (derived) and sub-indicators
            'ams_any', 'AMS', 'AMSAgitated', 'AMSSleep', 'AMSSlow', 'AMSRepeat',
            # Loss of consciousness
            'LOCSeparate', 'LocLen',
            # Vomiting
            'Vomit',
            # Headache
            'HA_verb', 'HASeverity',
            # Skull fracture signs
            'SFxPalp', 'SFxBas', 'SFxBasHem', 'SFxBasOto',
            # Hematoma and fontanelle (critical <2 yr)
            'Hema', 'FontBulg',
            # Acting normally per parent
            'ActNorm',
            # Neurological deficit
            'NeuroD',
            # Injury mechanism
            'severe_mechanism', 'InjuryMech', 'High_impact_InjSev',
            # Other
            'Amnesia_verb', 'Seiz',
        ]

        available_features = [f for f in feature_list if f in X.columns]
        self.feature_names = available_features

        return X[available_features]

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the logistic regression model."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.fit_transform(X_selected)
        X_scaled = self.scaler.fit_transform(X_imputed)
        self.model.fit(X_scaled, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.transform(X_selected)
        X_scaled = self.scaler.transform(X_imputed)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.transform(X_selected)
        X_scaled = self.scaler.transform(X_imputed)
        return self.model.predict_proba(X_scaled)

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance (coefficients)."""
        if self.feature_names is None:
            raise ValueError("Model must be fitted first")

        coefficients = self.model.coef_[0]
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Coefficient': coefficients,
            'AbsCoefficient': np.abs(coefficients)
        }).sort_values('AbsCoefficient', ascending=False)

        return importance_df


class AgeStratifiedLR:
    """
    Two separate Logistic Regression models, one per PECARN age stratum:
      - <2 years (infant): physical exam features dominate
      - >=2 years (older child): verbal-report features included

    Motivated by Finding 2: feature predictive meaning changes with age,
    and a single LR has low sensitivity for the <2yr stratum.
    """

    def __init__(self, C=1.0, class_weight=None, random_state=42):
        if class_weight is None:
            class_weight = {0: 1, 1: 120}
        self.age_threshold = 24
        self.model_lt2 = LogisticRegressionModel(
            C=C, class_weight=class_weight, random_state=random_state
        )
        self.model_ge2 = LogisticRegressionModel(
            C=C, class_weight=class_weight, random_state=random_state
        )

    def _split(self, X: pd.DataFrame):
        mask_lt2 = X['AgeInMonth'] < self.age_threshold
        return mask_lt2, ~mask_lt2

    def fit(self, X: pd.DataFrame, y: pd.Series):
        mask_lt2, mask_ge2 = self._split(X)
        self.model_lt2.fit(X[mask_lt2], y[mask_lt2])
        self.model_ge2.fit(X[mask_ge2], y[mask_ge2])
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        mask_lt2, mask_ge2 = self._split(X)
        proba = np.zeros((len(X), 2))
        if mask_lt2.sum() > 0:
            proba[mask_lt2.values] = self.model_lt2.predict_proba(X[mask_lt2])
        if mask_ge2.sum() > 0:
            proba[mask_ge2.values] = self.model_ge2.predict_proba(X[mask_ge2])
        return proba

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(X)[:, 1]
        return (proba > 0.5).astype(int)

    def get_feature_importance(self, stratum: str = 'ge2') -> pd.DataFrame:
        model = self.model_ge2 if stratum == 'ge2' else self.model_lt2
        return model.get_feature_importance()


class RandomForestModel:
    """
    Random Forest classifier for TBI prediction.

    Features:
    - Handles missing values naturally
    - Captures non-linear relationships
    - Feature importance for interpretability
    - Class imbalance handling
    """

    def __init__(self, n_estimators=100, max_depth=10,
                 class_weight=None, random_state=42):
        """
        Initialize random forest model.

        Parameters
        ----------
        n_estimators : int, default=100
            Number of trees
        max_depth : int, default=10
            Maximum depth of trees (prevent overfitting)
        class_weight : str or dict, default=None
            Weights associated with classes. Defaults to {0: 1, 1: 50}
        random_state : int, default=42
            Random seed
        """
        if class_weight is None:
            class_weight = {0: 1, 1: 120}
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight=class_weight,
            random_state=random_state,
            min_samples_split=100,  # Prevent overfitting on small ciTBI class
            min_samples_leaf=50,
            n_jobs=-1
        )
        self.imputer = SimpleImputer(strategy='median')
        self.feature_names = None

    def select_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Select clinically relevant features."""
        feature_list = [
            'AgeInMonth',
            'GCSTotal',
            # AMS composite and sub-indicators
            'ams_any', 'AMS', 'AMSAgitated', 'AMSSleep', 'AMSSlow', 'AMSRepeat',
            # Loss of consciousness
            'LOCSeparate', 'LocLen',
            # Vomiting
            'Vomit',
            # Headache
            'HA_verb', 'HASeverity',
            # Skull fracture signs
            'SFxPalp', 'SFxBas', 'SFxBasHem', 'SFxBasOto',
            # Hematoma and fontanelle (critical <2 yr)
            'Hema', 'FontBulg',
            # Acting normally per parent
            'ActNorm',
            # Neurological deficit
            'NeuroD',
            # Injury mechanism
            'severe_mechanism', 'InjuryMech', 'High_impact_InjSev',
            # Other
            'Amnesia_verb', 'Seiz',
        ]

        available_features = [f for f in feature_list if f in X.columns]
        self.feature_names = available_features
        return X[available_features]

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the random forest model."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.fit_transform(X_selected)
        self.model.fit(X_imputed, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.transform(X_selected)
        return self.model.predict(X_imputed)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        X_selected = self.select_features(X)
        X_imputed = self.imputer.transform(X_selected)
        return self.model.predict_proba(X_imputed)

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from random forest."""
        if self.feature_names is None:
            raise ValueError("Model must be fitted first")

        importance = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)

        return importance_df


def _compute_metrics(y_true: pd.Series, y_pred: np.ndarray,
                     y_proba: np.ndarray) -> Dict:
    """Compute classification metrics from predictions."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    auroc = roc_auc_score(y_true, y_proba)
    auprc = average_precision_score(y_true, y_proba)
    return {
        'Sensitivity': sensitivity,
        'Specificity': specificity,
        'PPV': ppv,
        'NPV': npv,
        'AUROC': auroc,
        'AUPRC': auprc,
        'TP': tp,
        'TN': tn,
        'FP': fp,
        'FN': fn,
        'N': int(tp + tn + fp + fn),
    }


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series,
                   model_name: str = "Model",
                   age_threshold_months: int = 24) -> pd.DataFrame:
    """
    Evaluate a model's performance, split by age group.

    Parameters
    ----------
    model : fitted model
        Model with predict_proba() method
    X_test : pd.DataFrame
        Test features (must contain AgeInMonth column)
    y_test : pd.Series
        Test labels
    model_name : str
        Name of the model for reporting
    age_threshold_months : int
        Age cutoff in months (default 24 = 2 years)

    Returns
    -------
    pd.DataFrame
        Performance metrics for Overall, <2 years, and ≥2 years groups
    """
    y_proba = model.predict_proba(X_test)[:, 1]
    # Find the highest threshold that still achieves ≥95% sensitivity.
    # This is the clinically appropriate operating point for a screening rule.
    target_sensitivity = 0.95
    best_threshold = 0.0
    y_test_arr = np.asarray(y_test)
    for t in np.linspace(0.0, 1.0, 1000):
        preds_t = (y_proba > t).astype(int)
        tp_t = int(((preds_t == 1) & (y_test_arr == 1)).sum())
        fn_t = int(((preds_t == 0) & (y_test_arr == 1)).sum())
        if (tp_t + fn_t) > 0 and tp_t / (tp_t + fn_t) >= target_sensitivity:
            best_threshold = t
    threshold = best_threshold
    y_pred = (y_proba > threshold).astype(int)

    age = X_test['AgeInMonth']
    mask_lt2 = age < age_threshold_months
    mask_ge2 = age >= age_threshold_months

    rows = []
    for label, mask in [
        ('Overall', pd.Series([True] * len(y_test), index=y_test.index)),
        ('<2 years', mask_lt2),
        ('≥2 years', mask_ge2),
    ]:
        idx = mask[mask].index
        metrics = _compute_metrics(
            y_test.loc[idx],
            y_pred[X_test.index.get_indexer(idx)],
            y_proba[X_test.index.get_indexer(idx)],
        )
        rows.append({'Model': model_name, 'AgeGroup': label, **metrics})

    return pd.DataFrame(rows)


def compare_models(models_dict: Dict, X_train: pd.DataFrame,
                   y_train: pd.Series, X_test: pd.DataFrame,
                   y_test: pd.Series) -> pd.DataFrame:
    """
    Train and compare multiple models.

    Parameters
    ----------
    models_dict : dict
        Dictionary of {model_name: model_object}
    X_train, y_train : pd.DataFrame, pd.Series
        Training data
    X_test, y_test : pd.DataFrame, pd.Series
        Test data

    Returns
    -------
    pd.DataFrame
        Comparison of model performances
    """
    results = []

    for name, model in models_dict.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        print(f"Evaluating {name}...")
        metrics_df = evaluate_model(model, X_test, y_test, model_name=name)
        results.append(metrics_df)

    comparison_df = pd.concat(results, ignore_index=True)
    return comparison_df


def main() -> None:
    from pathlib import Path
    from sklearn.model_selection import train_test_split
    from clean import read_data, clean_data

    code_dir = Path(__file__).parent
    data_path = code_dir.parent / "data" / "TBI PUD 10-08-2013.csv"

    df = read_data(str(data_path))
    df = clean_data(df)

    eligible = df.get("pecarn_eligible", True) & df["PosIntFinal"].notna()
    df = df[eligible].copy()

    y = df["PosIntFinal"].astype(int)
    X = df.drop(columns=["PosIntFinal"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models_dict = {
        "Kuppermann CDR": KuppermannCDR(),
        "Age-Stratified LR": AgeStratifiedLR(
            C=1.0, class_weight={0: 1, 1: 120}, random_state=42
        ),
        "Random Forest": RandomForestModel(
            n_estimators=200, max_depth=8,
            class_weight={0: 1, 1: 120}, random_state=42
        ),
    }

    results = compare_models(models_dict, X_train, y_train, X_test, y_test)
    print("\nModel Comparison:")
    print(results[["Model", "AgeGroup", "Sensitivity", "Specificity",
                   "AUROC", "AUPRC"]].to_string(index=False))


if __name__ == "__main__":
    main()
