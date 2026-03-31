from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Variables that carry true numeric values and must NOT have any special code
# converted to NaN.  All other columns are treated as categorical.
# ---------------------------------------------------------------------------
_TRUE_NUMERIC_COLS = ['AgeInMonth', 'AgeinYears', 'GCSTotal', 'PosIntFinal']

# PECARN codebook special values that encode non-informative responses.
# 92 = Not Applicable, 91 = Refused/Declined, 99 = Unknown/Not Documented.
# All three are semantically "missing" for categorical variables.
_SPECIAL_MISSING_CODES = [91, 92, 99]

# Valid range for GCS Total (Glasgow Coma Scale: 3–15).
_GCS_MIN, _GCS_MAX = 3, 15

# Valid ranges for GCS subscales (per Glasgow Coma Scale definition).
_GCS_EYE_MIN, _GCS_EYE_MAX = 1, 4      # Eye opening: spontaneous(4)→none(1)
_GCS_VERBAL_MIN, _GCS_VERBAL_MAX = 1, 5  # Verbal: oriented(5)→none(1)
_GCS_MOTOR_MIN, _GCS_MOTOR_MAX = 1, 6    # Motor: obeys commands(6)→none(1)

# Valid age range for the study (0–216 months = 0–18 years).
_AGE_MIN_MONTHS, _AGE_MAX_MONTHS = 0, 216

# Kuppermann et al. 2009: CDR was derived for patients with GCS of 14 or 15
# at ED presentation.  Patients with GCS ≤13 were outside the study scope.
_PECARN_GCS_MIN = 14


def read_data(data_path: str) -> pd.DataFrame:
    """Load the raw PECARN TBI CSV, using the first column as the index."""
    return pd.read_csv(data_path, index_col=0)


def category_na_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace PECARN special missing codes with NaN for all categorical columns.

    Codes converted: 91 (Refused), 92 (Not Applicable), 99 (Unknown).
    Columns in ``_TRUE_NUMERIC_COLS`` are left unchanged because they hold
    genuine numeric measurements.

    Parameters
    ----------
    df : pd.DataFrame
        Raw or partially-cleaned DataFrame.

    Returns
    -------
    pd.DataFrame
        Copy of ``df`` with special codes replaced by NaN.
    """
    df_clean = df.copy()
    for col in df_clean.columns:
        if col not in _TRUE_NUMERIC_COLS:
            df_clean[col] = df_clean[col].replace(_SPECIAL_MISSING_CODES, np.nan)
    return df_clean


def _validate_gcs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce out-of-range GCS Total values to NaN.

    The Glasgow Coma Scale is defined on [3, 15].  Values outside this range
    (e.g. 0, 1, 2, or >15) are data-entry errors and are set to NaN so they
    do not distort downstream analyses.
    """
    df_clean = df.copy()
    if 'GCSTotal' in df_clean.columns:
        invalid_mask = (
            df_clean['GCSTotal'].notna()
            & (
                (df_clean['GCSTotal'] < _GCS_MIN)
                | (df_clean['GCSTotal'] > _GCS_MAX)
            )
        )
        n_invalid = invalid_mask.sum()
        if n_invalid > 0:
            print(f"  GCS range check: set {n_invalid} out-of-range values to NaN")
            df_clean.loc[invalid_mask, 'GCSTotal'] = np.nan
    return df_clean


def _validate_gcs_subscales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce out-of-range GCS subscale values to NaN.

    The Glasgow Coma Scale components have fixed valid ranges:
    - Eye opening  : 1–4
    - Verbal       : 1–5
    - Motor        : 1–6

    Values outside these ranges are data-entry errors.  We set them to NaN
    rather than dropping rows so that other columns from the same patient
    are preserved.
    """
    df_clean = df.copy()
    subscale_bounds = {
        'GCSEye':    (_GCS_EYE_MIN,    _GCS_EYE_MAX),
        'GCSVerbal': (_GCS_VERBAL_MIN, _GCS_VERBAL_MAX),
        'GCSMotor':  (_GCS_MOTOR_MIN,  _GCS_MOTOR_MAX),
    }
    for col, (lo, hi) in subscale_bounds.items():
        if col not in df_clean.columns:
            continue
        invalid_mask = (
            df_clean[col].notna()
            & ((df_clean[col] < lo) | (df_clean[col] > hi))
        )
        n_invalid = int(invalid_mask.sum())
        if n_invalid > 0:
            print(f"  GCS subscale range check ({col} ∈ [{lo},{hi}]): "
                  f"set {n_invalid} out-of-range values to NaN")
            df_clean.loc[invalid_mask, col] = np.nan
    return df_clean



def _validate_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce impossible age values to NaN.

    The PECARN study enrolled patients younger than 18 years (< 216 months).
    Negative ages or ages above 216 months are treated as data errors.
    """
    df_clean = df.copy()
    for col in ['AgeInMonth', 'AgeinYears']:
        if col not in df_clean.columns:
            continue
        limit = _AGE_MAX_MONTHS if col == 'AgeInMonth' else _AGE_MAX_MONTHS / 12
        invalid_mask = (
            df_clean[col].notna()
            & ((df_clean[col] < 0) | (df_clean[col] > limit))
        )
        n_invalid = invalid_mask.sum()
        if n_invalid > 0:
            print(f"  Age range check ({col}): set {n_invalid} out-of-range values to NaN")
            df_clean.loc[invalid_mask, col] = np.nan
    return df_clean


def check_contradictions(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Audit the PECARN dataset for logical contradictions implied by the codebook.

    The codebook specifies parent-child relationships between variables: a sub-
    question is only applicable when its parent question is answered affirmatively.
    When these relationships are violated, the affected values are likely data-entry
    errors.  This function detects every such violation and, where appropriate,
    corrects the child field by setting it to NaN.

    Contradiction checks performed
    --------------------------------
    1.  **GCS component sum** – ``GCSTotal`` must equal ``GCSEye + GCSVerbal +
        GCSMotor``.  Two patients violate this; their ``GCSTotal`` is replaced by
        the computed sum (the component scores are collected independently and are
        more reliable).

    2.  **AgeTwoPlus consistency** – ``AgeTwoPlus`` (1 = <2 yr, 2 = ≥2 yr) must
        agree with ``AgeInMonth``.  Any mismatch is corrected by recomputing
        ``AgeTwoPlus`` from ``AgeInMonth``.

    3.  **PosIntFinal consistency** – ``PosIntFinal = 1`` (ciTBI) requires at
        least one of the four outcome components to be positive:
        ``DeathTBI``, ``HospHeadPosCT``, ``Intub24Head``, ``Neurosurgery``.
        Three patients have ``PosIntFinal = 1`` with all components = 0; they are
        flagged but *not* corrected because the cause is unknown (possible data
        loss in component fields).

    4.  **Conditional sub-fields** – twelve parent→children relationships from the
        codebook are checked.  When a parent is negative (0) but a child field is
        non-NaN, the child is set to NaN because the question was logically not
        applicable.  Groups checked:

        - ``LOCSeparate = 0`` → ``LocLen`` should be NaN
        - ``Seiz = 0`` → ``SeizOccur``, ``SeizLen`` should be NaN
        - ``HA_verb = 0`` → ``HASeverity``, ``HAStart`` should be NaN
        - ``Vomit = 0`` → ``VomitNbr``, ``VomitStart``, ``VomitLast`` should be NaN
        - ``AMS = 0`` → AMS sub-types should be NaN
        - ``SFxBas = 0`` → basilar SFx sub-types should be NaN
        - ``SFxPalp = 0`` → ``SFxPalpDepress`` should be NaN
        - ``Hema = 0`` → ``HemaLoc``, ``HemaSize`` should be NaN
        - ``Clav = 0`` → Clav location sub-types should be NaN
        - ``NeuroD = 0`` → NeuroD sub-types should be NaN
        - ``OSI = 0`` → OSI sub-types should be NaN
        - ``CTDone = 0`` → ``EDCT``, ``PosCT``, CT finding columns should be NaN

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame produced by ``category_na_clean`` (special codes already NaN).
    verbose : bool, default True
        Print a summary of findings to stdout.

    Returns
    -------
    pd.DataFrame
        Copy of ``df`` with contradictions corrected where possible.
    """
    df_out = df.copy()

    # Track corrections for the summary report
    report_rows = []

    def _flag(check_name: str, n_affected: int, action: str) -> None:
        report_rows.append({
            'check': check_name,
            'n_affected': n_affected,
            'action': action,
        })

    def _null_children(parent_col: str, parent_neg_val: float,
                       child_cols: list, df_: pd.DataFrame) -> tuple:
        """Set child cols to NaN where parent == parent_neg_val and child is not NaN."""
        if parent_col not in df_.columns:
            return df_, 0
        parent_neg = df_[parent_col] == parent_neg_val
        total_fixed = 0
        for child in child_cols:
            if child not in df_.columns:
                continue
            mask = parent_neg & df_[child].notna()
            n = int(mask.sum())
            if n:
                df_.loc[mask, child] = np.nan
                total_fixed += n
        return df_, total_fixed

    # ── 1. GCS component sum ──────────────────────────────────────────────────
    gcs_cols = ['GCSEye', 'GCSVerbal', 'GCSMotor', 'GCSTotal']
    if all(c in df_out.columns for c in gcs_cols):
        mask_all = df_out[gcs_cols].notna().all(axis=1)
        computed = (df_out.loc[mask_all, 'GCSEye']
                    + df_out.loc[mask_all, 'GCSVerbal']
                    + df_out.loc[mask_all, 'GCSMotor'])
        mismatch = mask_all.copy()
        mismatch[mask_all] = computed.values != df_out.loc[mask_all, 'GCSTotal'].values
        n_gcs = int(mismatch.sum())
        if n_gcs:
            # Replace GCSTotal with the computed sum; component scores are more reliable
            df_out.loc[mismatch, 'GCSTotal'] = computed[
                computed.index.isin(df_out.index[mismatch])
            ].values
        _flag('GCS total != Eye+Verbal+Motor', n_gcs,
              'replaced GCSTotal with component sum')

    # ── 2. AgeTwoPlus vs AgeInMonth ──────────────────────────────────────────
    if 'AgeTwoPlus' in df_out.columns and 'AgeInMonth' in df_out.columns:
        mask_age = df_out['AgeInMonth'].notna() & df_out['AgeTwoPlus'].notna()
        expected = (df_out.loc[mask_age, 'AgeInMonth'] >= 24).astype(int) + 1
        mismatch_age = mask_age.copy()
        mismatch_age[mask_age] = (
            expected.values != df_out.loc[mask_age, 'AgeTwoPlus'].values
        )
        n_age = int(mismatch_age.sum())
        if n_age:
            df_out.loc[mismatch_age, 'AgeTwoPlus'] = (
                (df_out.loc[mismatch_age, 'AgeInMonth'] >= 24).astype(int) + 1
            )
        _flag('AgeTwoPlus inconsistent with AgeInMonth', n_age,
              'recomputed AgeTwoPlus from AgeInMonth')

    # ── 3. PosIntFinal=1 but no outcome component is 1 ───────────────────────
    oc_cols = ['DeathTBI', 'HospHeadPosCT', 'Intub24Head', 'Neurosurgery']
    oc_avail = [c for c in oc_cols if c in df_out.columns]
    if 'PosIntFinal' in df_out.columns and oc_avail:
        any_component = df_out[oc_avail].eq(1).any(axis=1)
        orphan = (df_out['PosIntFinal'] == 1) & ~any_component
        n_orphan = int(orphan.sum())
        _flag('PosIntFinal=1 with no outcome component positive', n_orphan,
              'flagged only — cause unknown, values retained')

    # ── 4. Conditional sub-field nullification ────────────────────────────────
    parent_child_groups = [
        # (parent_col, negative_value, [child_cols], description)
        ('LOCSeparate', 0, ['LocLen'],
         'LOCSeparate=0 → LocLen'),
        ('Seiz', 0, ['SeizOccur', 'SeizLen'],
         'Seiz=0 → SeizOccur/SeizLen'),
        ('HA_verb', 0, ['HASeverity', 'HAStart'],
         'HA_verb=0 → HASeverity/HAStart'),
        ('Vomit', 0, ['VomitNbr', 'VomitStart', 'VomitLast'],
         'Vomit=0 → VomitNbr/VomitStart/VomitLast'),
        ('AMS', 0, ['AMSAgitated', 'AMSSleep', 'AMSSlow', 'AMSRepeat', 'AMSOth'],
         'AMS=0 → AMS sub-types'),
        ('SFxBas', 0, ['SFxBasHem', 'SFxBasOto', 'SFxBasPer', 'SFxBasRet', 'SFxBasRhi'],
         'SFxBas=0 → basilar SFx sub-types'),
        ('SFxPalp', 0, ['SFxPalpDepress'],
         'SFxPalp=0 → SFxPalpDepress'),
        ('Hema', 0, ['HemaLoc', 'HemaSize'],
         'Hema=0 → HemaLoc/HemaSize'),
        ('Clav', 0, ['ClavFace', 'ClavNeck', 'ClavFro', 'ClavOcc', 'ClavPar', 'ClavTem'],
         'Clav=0 → Clav location sub-types'),
        ('NeuroD', 0, ['NeuroDMotor', 'NeuroDSensory', 'NeuroDCranial',
                       'NeuroDReflex', 'NeuroDOth'],
         'NeuroD=0 → NeuroD sub-types'),
        ('OSI', 0, ['OSIExtremity', 'OSICut', 'OSICspine', 'OSIFlank',
                    'OSIAbdomen', 'OSIPelvis', 'OSIOth'],
         'OSI=0 → OSI sub-types'),
        ('CTDone', 0, ['EDCT', 'PosCT']
         + [f'Finding{i}' for i in list(range(1, 15)) + [20, 21, 22, 23]],
         'CTDone=0 → EDCT/PosCT/Findings'),
    ]

    for parent_col, neg_val, children, description in parent_child_groups:
        df_out, n_fixed = _null_children(parent_col, neg_val, children, df_out)
        _flag(description, n_fixed, 'set child fields to NaN')

    # ── Summary report ────────────────────────────────────────────────────────
    report = pd.DataFrame(report_rows)
    if verbose:
        print("  Contradiction check results:")
        for _, row in report.iterrows():
            status = f"  [{row['n_affected']:4d} rows]  {row['check']}"
            print(f"    {status}")
            print(f"           → {row['action']}")

    return df_out


def contradiction_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame reporting all logical contradictions found in ``df``.

    This is a read-only audit that does not modify ``df``.  It is useful for
    understanding data quality before committing to a cleaning strategy.

    Returns
    -------
    pd.DataFrame
        Columns: check, n_affected, description
    """
    rows = []

    def _add(check, n, desc):
        rows.append({'check': check, 'n_affected': n, 'description': desc})

    # GCS sum
    gcs_cols = ['GCSEye', 'GCSVerbal', 'GCSMotor', 'GCSTotal']
    if all(c in df.columns for c in gcs_cols):
        mask = df[gcs_cols].notna().all(axis=1)
        computed = df.loc[mask, 'GCSEye'] + df.loc[mask, 'GCSVerbal'] + df.loc[mask, 'GCSMotor']
        n = int((computed.values != df.loc[mask, 'GCSTotal'].values).sum())
        _add('GCS component sum mismatch', n,
             'GCSTotal != GCSEye + GCSVerbal + GCSMotor; likely data-entry error')

    # AgeTwoPlus
    if 'AgeTwoPlus' in df.columns and 'AgeInMonth' in df.columns:
        mask = df['AgeInMonth'].notna() & df['AgeTwoPlus'].notna()
        expected = (df.loc[mask, 'AgeInMonth'] >= 24).astype(int) + 1
        n = int((expected.values != df.loc[mask, 'AgeTwoPlus'].values).sum())
        _add('AgeTwoPlus inconsistent with AgeInMonth', n,
             'Derived age-group flag disagrees with continuous age')

    # PosIntFinal orphans
    oc_avail = [c for c in ['DeathTBI', 'HospHeadPosCT', 'Intub24Head', 'Neurosurgery']
                if c in df.columns]
    if 'PosIntFinal' in df.columns and oc_avail:
        n = int(((df['PosIntFinal'] == 1) & ~df[oc_avail].eq(1).any(axis=1)).sum())
        _add('PosIntFinal=1 with no component positive', n,
             'ciTBI outcome set without any of: DeathTBI, HospHeadPosCT, '
             'Intub24Head, Neurosurgery; possible data loss in component fields')

    # Parent-child violations (read-only count)
    parent_child = [
        ('LOCSeparate', ['LocLen']),
        ('Seiz', ['SeizOccur', 'SeizLen']),
        ('HA_verb', ['HASeverity', 'HAStart']),
        ('Vomit', ['VomitNbr', 'VomitStart', 'VomitLast']),
        ('AMS', ['AMSAgitated', 'AMSSleep', 'AMSSlow', 'AMSRepeat', 'AMSOth']),
        ('SFxBas', ['SFxBasHem', 'SFxBasOto', 'SFxBasPer', 'SFxBasRet', 'SFxBasRhi']),
        ('SFxPalp', ['SFxPalpDepress']),
        ('Hema', ['HemaLoc', 'HemaSize']),
        ('Clav', ['ClavFace', 'ClavNeck', 'ClavFro', 'ClavOcc', 'ClavPar', 'ClavTem']),
        ('NeuroD', ['NeuroDMotor', 'NeuroDSensory', 'NeuroDCranial',
                    'NeuroDReflex', 'NeuroDOth']),
        ('OSI', ['OSIExtremity', 'OSICut', 'OSICspine', 'OSIFlank',
                 'OSIAbdomen', 'OSIPelvis', 'OSIOth']),
        ('CTDone', ['EDCT', 'PosCT']
         + [f'Finding{i}' for i in list(range(1, 15)) + [20, 21, 22, 23]]),
    ]
    for parent, children in parent_child:
        if parent not in df.columns:
            continue
        avail_children = [c for c in children if c in df.columns]
        n = int(
            ((df[parent] == 0) & df[avail_children].notna().any(axis=1)).sum()
        )
        _add(f'{parent}=0 but child field(s) non-NaN', n,
             f'Child fields should be NaN (not applicable) when {parent}=0')

    return pd.DataFrame(rows).sort_values('n_affected', ascending=False)


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame summarising missingness for every column.

    Columns in the output
    ---------------------
    n_missing  : absolute count of NaN values
    pct_missing: percentage of rows that are NaN
    n_present  : absolute count of non-NaN values
    n_unique   : number of distinct non-NaN values
    dtype      : pandas dtype as a string

    The result is sorted descending by ``pct_missing``.
    """
    return pd.DataFrame({
        'n_missing': df.isna().sum(),
        'pct_missing': df.isna().mean() * 100,
        'n_present': df.notna().sum(),
        'n_unique': df.nunique(dropna=True),
        'dtype': df.dtypes.astype(str),
    }).sort_values('pct_missing', ascending=False)


def age_group(df: pd.DataFrame) -> None:
    """
    Add an ``AgeGroup`` column to ``df`` in-place.

    Bins align with the PECARN age stratification used in Kuppermann et al.:
    the primary split is at 24 months (2 years), with finer groups for EDA.

    Groups: [0,1)y | [1,2)y | [2,5)y | [5,10)y | [10,18)y
    """
    df['AgeGroup'] = pd.cut(
        df['AgeInMonth'],
        bins=[0, 12, 24, 60, 120, 216],
        labels=['[0,1)y', '[1,2)y', '[2,5)y', '[5,10)y', '[10,18)y'],
        include_lowest=True,
        right=False,
    )


def add_eligibility_flag(df: pd.DataFrame) -> None:
    """
    Add a ``pecarn_eligible`` column indicating PECARN CDR applicability.

    Kuppermann et al. (2009) derived and validated the PECARN CDR specifically
    for children who presented to the ED with a GCS of 14 or 15.  Applying the
    CDR to patients with GCS ≤13 (moderate–severe TBI) is out of scope: those
    patients virtually always warrant CT regardless of other predictors.

    ``pecarn_eligible = True``  → GCS ∈ {14, 15} and age < 216 months
    ``pecarn_eligible = False`` → GCS outside 14–15 or age ≥ 18 years

    The flag is added in-place and never overrides existing columns.
    """
    eligible = pd.Series(True, index=df.index)

    if 'GCSTotal' in df.columns:
        gcs_ok = df['GCSTotal'].isin([14, 15])
        eligible = eligible & gcs_ok

    if 'AgeInMonth' in df.columns:
        age_ok = df['AgeInMonth'].notna() & (df['AgeInMonth'] < _AGE_MAX_MONTHS)
        eligible = eligible & age_ok

    df['pecarn_eligible'] = eligible


def add_derived_features(df: pd.DataFrame) -> None:
    """
    Add clinically meaningful derived columns used in the PECARN CDR.

    Derived columns
    ---------------
    ams_any : int (0/1)
        Composite altered-mental-status flag.  The PECARN CDR defines AMS as
        the presence of agitation, somnolence, repetitive questioning, or slow
        response to verbal communication (Kuppermann et al. 2009, Appendix).
        This column unifies the four sub-indicators into the single binary
        variable actually used by the rule.

    severe_mechanism : int (0/1)
        Composite severe-mechanism flag matching the PECARN CDR definition:
        - Motor-vehicle crash with ejection, death of another passenger, or
          rollover (MVCEject=1, MVCDeath=1, or MVCRollover=1)
        - Pedestrian or bicyclist struck by a motorized vehicle (PedBicStruck=1)
        - Fall > 5 ft for children ≥2 yr, or > 3 ft for children <2 yr
        - Head struck by a high-impact object (HighRiskMVC=1 as a proxy)

    All columns are added in-place.
    """
    # ── Composite AMS flag ────────────────────────────────────────────────────
    # ams_any = 1 if AMS == 1 (present) or AMS is NaN (unknown → conservative).
    # ams_any = 0 only when AMS is explicitly recorded as 0 (absent).
    if 'AMS' in df.columns:
        df['ams_any'] = (~df['AMS'].eq(0)).astype(int)

    # ── Composite severe mechanism flag ───────────────────────────────────────
    # The PECARN dataset encodes mechanism via InjuryMech (categorical, 1–12+)
    # and the pre-computed High_impact_InjSev field (1 = high-impact, 2 = low,
    # 3 = intermediate by PECARN convention).
    #
    # Kuppermann 2009 defines "severe mechanism" as:
    #   MVC with ejection / death of another / rollover; pedestrian or
    #   bicyclist struck by motorized vehicle; fall > 5 ft (≥2 yr) or > 3 ft
    #   (<2 yr); head struck by high-impact object.
    #
    # InjuryMech codes that map to severe mechanism per PECARN codebook:
    #   1 = MVC occupant (any), 2 = pedestrian struck by vehicle,
    #   3 = bicyclist struck, 4 = motorcycle occupant.
    # High_impact_InjSev = 1 captures additional high-energy events.
    _SEVERE_MECH_CODES = {1, 2, 3, 4}

    mech_parts = []

    if 'InjuryMech' in df.columns:
        mech_parts.append(df['InjuryMech'].isin(_SEVERE_MECH_CODES))

    if 'High_impact_InjSev' in df.columns:
        mech_parts.append(df['High_impact_InjSev'].eq(3))

    if mech_parts:
        df['severe_mechanism'] = (
            pd.concat(mech_parts, axis=1)
            .any(axis=1)
            .astype(int)
        )


def clean_data(
    df: pd.DataFrame,
    remove_duplicates: bool = False,
    add_age_groups: bool = True,
    fix_contradictions: bool = True,
    add_derived: bool = True,
) -> pd.DataFrame:
    """
    Clean the raw PECARN TBI DataFrame.

    Cleaning pipeline (in order)
    ----------------------------
    1. **Special-code imputation** – replace codes 91, 92, 99 with NaN for all
       categorical columns (true numeric columns are exempt; see
       ``_TRUE_NUMERIC_COLS``).
    2. **GCS range validation** – out-of-range GCS Total values → NaN; GCS
       subscale values (Eye 1–4, Verbal 1–5, Motor 1–6) → NaN.
    3. **Age range validation** – impossible age values → NaN.
    4. **Outcome type coercion** – ``PosIntFinal`` is cast to numeric.
    5. **Contradiction resolution** (optional) – logical inconsistencies between
       related variables are detected and corrected where possible.  See
       ``check_contradictions`` for the full list of checks.  Key fixes:

       - 2 patients with ``GCSTotal != GCSEye + GCSVerbal + GCSMotor`` have their
         ``GCSTotal`` replaced by the computed component sum.
       - 3 patients with ``PosIntFinal = 1`` but no supporting outcome component
         are flagged but not altered (cause is unknown).
       - Parent→child field violations (e.g. ``LocLen`` present when
         ``LOCSeparate = 0``) have the child field set to NaN.

    6. **Age groups** (optional) – a new ``AgeGroup`` column is added.
    7. **PECARN eligibility flag** – ``pecarn_eligible`` marks patients with
       GCS 14–15 who fall within the CDR's intended scope (Kuppermann 2009).
    8. **Derived clinical features** (optional) – ``ams_any`` and
       ``severe_mechanism`` are added as analysis-ready composite variables.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame returned by ``read_data``.
    remove_duplicates : bool, default False
        Drop exact duplicate rows.  Disabled by default; see note above.
    add_age_groups : bool, default True
        Append the ``AgeGroup`` categorical column.
    fix_contradictions : bool, default True
        Run ``check_contradictions`` to resolve logical inconsistencies.
    add_derived : bool, default True
        Add PECARN eligibility flag and derived clinical features.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for EDA and modelling.

    Examples
    --------
    >>> df_raw = read_data('../data/TBI PUD 10-08-2013.csv')
    >>> df_clean = clean_data(df_raw)
    >>> df_clean.shape
    (43399, 129)
    """
    df_clean = df.copy()

    # Step 1: replace special PECARN missing codes with NaN
    df_clean = category_na_clean(df_clean)

    # Step 2: validate GCS Total and subscale ranges
    df_clean = _validate_gcs(df_clean)
    df_clean = _validate_gcs_subscales(df_clean)

    # Step 3: validate age range
    df_clean = _validate_age(df_clean)

    # Step 4: remove exact duplicate rows (disabled by default)
    if remove_duplicates:
        n_before = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        n_removed = n_before - len(df_clean)
        if n_removed > 0:
            print(f"  Duplicate removal: dropped {n_removed} rows "
                  f"({n_removed / n_before * 100:.2f}%)")

    # Step 5: ensure outcome variable is numeric
    if 'PosIntFinal' in df_clean.columns:
        df_clean['PosIntFinal'] = pd.to_numeric(
            df_clean['PosIntFinal'], errors='coerce'
        )

    # Step 6: resolve logical contradictions between related variables
    if fix_contradictions:
        df_clean = check_contradictions(df_clean, verbose=True)

    # Step 7: add age group column
    if add_age_groups:
        age_group(df_clean)

    # Step 8: add eligibility flag and derived clinical features
    if add_derived:
        add_eligibility_flag(df_clean)
        add_derived_features(df_clean)

    return df_clean


def add_pecarn_risk_tier(df: pd.DataFrame) -> None:
    """
    Add a ``cdr_positive`` column to ``df`` in-place.

    Applies the Kuppermann 2009 PECARN CDR to classify each patient as
    high-risk (CDR positive, CT recommended) or very-low-risk (CDR negative).

    ``cdr_positive = 1``   → at least one PECARN predictor present for the age group.
    ``cdr_positive = 0``   → no predictors present (very-low-risk tier).
    ``cdr_positive = NaN`` → age or outcome data insufficient to classify.

    Predictors for children **<2 years**:
        AMS | non-frontal scalp hematoma | LOC ≥5 s | severe mechanism |
        palpable skull fracture | not acting normally per parent

    Predictors for children **≥2 years**:
        AMS | any LOC | vomiting | severe mechanism |
        basilar skull fracture signs | severe headache

    This mirrors the KuppermannCDR class logic in models.py but uses the
    column names confirmed by the PECARN codebook (same as used throughout
    the cleaning pipeline), and is provided as a vectorised operation for
    efficient batch processing.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame produced by ``clean_data``.  The function reads
        ``AgeInMonth``, ``AMS``, ``SFxNonFront``, ``LOCSeparate``, ``LocLen``,
        ``severe_mechanism``, ``SFxPalp``, ``ActNorm``, ``Vomit``,
        ``SFxBas``, ``HA_verb``, and ``HASeverity``; missing columns are
        treated as "feature absent" rather than raising an error.
    """
    _zero = pd.Series(0, index=df.index)
    _nan  = pd.Series(np.nan, index=df.index)

    age = df.get("AgeInMonth", _nan)
    lt2 = age < 24
    ge2 = age >= 24

    ams       = df.get("AMS",            _zero) == 1
    sfx_nf    = df.get("SFxNonFront",    _zero) == 1
    loc_occ   = df.get("LOCSeparate",    _zero) == 1
    loc_len   = df.get("LocLen",         _nan)
    loc_5s    = loc_occ & (loc_len >= 5).fillna(False)
    sev_mech  = df.get("severe_mechanism", _zero) == 1
    sfx_palp  = df.get("SFxPalp",       _zero) == 1
    act_not_normal = df.get("ActNorm",   _nan).eq(0).fillna(False)
    vomit     = df.get("Vomit",          _zero) == 1
    sfx_bas   = df.get("SFxBas",         _zero) == 1

    # Severe headache: prefer HASeverity ≥ 3; fall back to HA_verb = 1
    if "HASeverity" in df.columns:
        ha_severe = df["HASeverity"] >= 3
    else:
        ha_severe = df.get("HA_verb", _zero) == 1

    cdr_lt2 = ams | sfx_nf | loc_5s | sev_mech | sfx_palp | act_not_normal
    cdr_ge2 = ams | loc_occ | vomit | sev_mech | sfx_bas | ha_severe

    cdr_pos = pd.Series(np.nan, index=df.index)
    cdr_pos[lt2 & age.notna()] = cdr_lt2[lt2 & age.notna()].astype(float)
    cdr_pos[ge2 & age.notna()] = cdr_ge2[ge2 & age.notna()].astype(float)
    df["cdr_positive"] = cdr_pos


def main() -> None:
    code_dir = Path(__file__).parent
    data_path = code_dir.parent / 'data' / 'TBI PUD 10-08-2013.csv'

    df = read_data(str(data_path))
    print(f"Raw data: {df.shape[0]:,} rows × {df.shape[1]} columns")

    df_clean = clean_data(df)
    print(f"Clean data: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
    print(df_clean.info())


if __name__ == '__main__':
    main()