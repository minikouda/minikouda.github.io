"""
analysis.py – PECARN TBI Lab 1.

Part 1 – Three EDA findings (pure probability tables and visualizations, no models):
  Finding 1: ciTBI risk is nonlinear and clustered, not gradual.
  Finding 2: Feature predictive meaning changes with age.
  Finding 3: Clinician CT ordering encodes hidden signal beyond recorded features.

Part 2 – Three classification models:
  Kuppermann CDR, Logistic Regression, Random Forest.

All EDA focuses on the PECARN-eligible cohort (GCS 14–15).

Run from the code/ directory:
    python analysis.py

Figures are saved as PNG (300 dpi) to ../report/figures/.
"""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")
matplotlib.use("Agg")

# ── paths ─────────────────────────────────────────────────────────────────────
CODE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(CODE_DIR))

from clean import clean_data, missing_summary, read_data  # noqa: E402
from models import (  # noqa: E402
    KuppermannCDR,
    AgeStratifiedLR,
    RandomForestModel,
    evaluate_model,
)

DATA_PATH = CODE_DIR.parent / "data" / "TBI PUD 10-08-2013.csv"
FIG_DIR = CODE_DIR.parent / "report" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── global plot style ─────────────────────────────────────────────────────────
plt.rcParams.update(
    {
        "figure.dpi": 150,
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
PALETTE = sns.color_palette("colorblind")

# ── PECARN binary predictors available in the dataset ─────────────────────────
# Names confirmed from contradiction-check parent columns and derived features.
PECARN_BINARY = ["AMS", "severe_mechanism", "LOCSeparate", "Vomit",
                 "HA_verb", "SFxBas", "SFxPalp", "Hema", "NeuroD"]

# Human-readable labels for each predictor
FEATURE_LABELS = {
    "AMS":              "Altered Mental\nStatus",
    "severe_mechanism": "Severe\nMechanism",
    "LOCSeparate":      "Loss of\nConsciousness",
    "Vomit":            "Vomiting",
    "HA_verb":          "Headache",
    "SFxBas":           "Basilar Skull\nFracture Signs",
    "SFxPalp":          "Palpable Skull\nFracture",
    "Hema":             "Scalp\nHematoma",
    "NeuroD":           "Neurological\nDeficit",
}

# Age bins: five developmental periods
AGE_BINS   = [0, 12, 24, 60, 144, 216]
AGE_LABELS = ["<1 yr", "1–2 yr", "2–5 yr", "5–12 yr", "12–18 yr"]


def savefig(name: str) -> None:
    path = FIG_DIR / name
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  saved {path.name}")


def _avail(cols, df):
    """Return subset of cols that exist in df."""
    return [c for c in cols if c in df.columns]

# ══════════════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════════════

def load_and_clean():
    print("Loading data …")
    df_raw = read_data(str(DATA_PATH))
    print(f"  raw shape: {df_raw.shape}")
    df = clean_data(df_raw)
    print(f"  clean shape: {df.shape}")

    # PECARN-eligible cohort: GCS 14–15, known outcome
    elig = (
        df.get("pecarn_eligible", pd.Series(True, index=df.index))
        & df["PosIntFinal"].notna()
    )
    df_elig = df[elig].copy()
    n_pos = int(df_elig["PosIntFinal"].sum())
    print(
        f"  PECARN-eligible (GCS 14–15): {len(df_elig):,} patients, "
        f"{n_pos} ciTBI ({n_pos / len(df_elig) * 100:.2f}%)"
    )
    return df_raw, df, df_elig


# ══════════════════════════════════════════════════════════════════════════════
# Standard EDA figures (Data section of report)
# ══════════════════════════════════════════════════════════════════════════════

_VAR_LABELS = {
    "Dizzy":        "Dizziness",
    "Ethnicity":    "Ethnicity",
    "ActNorm":      "Acting Normally (parent report)",
    "Race":         "Race",
    "LocLen":       "LOC Duration",
    "Observed":     "Observed in ED (CT decision)",
    "Amnesia_verb": "Amnesia (verbal report)",
    "LOCSeparate":  "Loss of Consciousness (history)",
    "Drugs":        "Drugs/Alcohol Suspected",
    "HAStart":      "Headache Onset Time",
    "GCSMotor":     "GCS Motor",
    "GCSVerbal":    "GCS Verbal",
    "GCSEye":       "GCS Eye",
    "HASeverity":   "Headache Severity",
    "VomitLast":    "Time of Last Vomiting",
}


def fig_missing(df_raw):
    print("\nFigure: missing data …")
    ms = missing_summary(df_raw)
    top = ms[ms["pct_missing"] > 0].head(10).copy()
    top.index = [_VAR_LABELS.get(v, v) for v in top.index]

    fig, ax = plt.subplots(figsize=(4, 3))
    cmap = matplotlib.colormaps.get_cmap("RdYlGn_r")
    colors = cmap(top["pct_missing"].values / 100)
    ax.barh(range(len(top)), top["pct_missing"],
            color=colors, edgecolor="white", linewidth=0.4)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top.index, fontsize=5.5)
    ax.invert_yaxis()
    ax.set_xlabel("Variables Missing (%)",fontsize=8)
    ax.set_title("Top 10 Variables by Missingness", fontsize=8)
    for i, v in enumerate(top["pct_missing"]):
        ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=7.5)
    plt.tight_layout()
    savefig("fig_missing_data.png")


def fig_outcome(df):
    print("Figure: outcome distribution …")
    outcome = df["PosIntFinal"].dropna()
    n_pos = int((outcome == 1).sum())
    n_neg = int((outcome == 0).sum())
    pct = n_pos / len(outcome) * 100

    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].bar(["No ciTBI (0)", "ciTBI (1)"], [n_neg, n_pos],
                color=[PALETTE[2], PALETTE[3]], edgecolor="black", linewidth=0.6)
    axes[0].set_ylabel("Patient count")
    axes[0].set_title("ciTBI outcome counts")
    for i, v in enumerate([n_neg, n_pos]):
        axes[0].text(i, v + 200, f"{v:,}", ha="center",
                     fontsize=9, fontweight="bold")
    axes[1].pie([n_neg, n_pos], labels=["No ciTBI", "ciTBI"],
                autopct="%1.2f%%", colors=[PALETTE[2], PALETTE[3]],
                startangle=90, textprops={"fontsize": 10})
    axes[1].set_title(f"Class split  (ciTBI = {pct:.2f}%)")
    plt.tight_layout()
    savefig("fig_outcome_dist.png")
    return pct


def fig_age(df):
    print("Figure: age distribution …")
    age = df["AgeInMonth"].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(age, bins=60, color=PALETTE[0],
                 edgecolor="white", linewidth=0.3, alpha=0.85)
    axes[0].axvline(24, color="crimson", linestyle="--",
                    linewidth=1.6, label="24 mo (2 yr)")
    axes[0].set_xlabel("Age (months)")
    axes[0].set_ylabel("Patients")
    axes[0].set_title("Age distribution")
    axes[0].legend()

    grp_counts = pd.cut(age, bins=AGE_BINS, labels=AGE_LABELS,
                        include_lowest=True, right=False
                        ).value_counts().reindex(AGE_LABELS)
    axes[1].bar(AGE_LABELS, grp_counts.values,
                color=PALETTE[:5], edgecolor="black", linewidth=0.5)
    axes[1].set_xlabel("Age group")
    axes[1].set_ylabel("Patients")
    axes[1].set_title("Patients by age group")
    for i, v in enumerate(grp_counts.values):
        axes[1].text(i, v + 150, f"{v:,}", ha="center", fontsize=8)
    plt.tight_layout()
    savefig("fig_age_dist.png")


def fig_gcs_outcome(df):
    """
    Bar chart: ciTBI rate (%) by GCS Total score.

    Uses the full cleaned dataset (all GCS levels) so the steep gradient
    from GCS ≤13 to GCS 14–15 is visible, motivating the cohort restriction.
    """
    print("\nFigure: GCS vs ciTBI rate …")
    sub = df[df["PosIntFinal"].notna() & df["GCSTotal"].notna()].copy()
    sub["GCSTotal"] = sub["GCSTotal"].astype(int)

    gcs_stats = (
        sub.groupby("GCSTotal")["PosIntFinal"]
        .agg(n="count", n_pos="sum")
        .assign(rate=lambda d: d["n_pos"] / d["n"] * 100)
        .reset_index()
        .sort_values("GCSTotal")
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#d73027" if g <= 13 else "#4575b4" for g in gcs_stats["GCSTotal"]]
    ax.bar(gcs_stats["GCSTotal"].astype(str), gcs_stats["rate"],
           color=colors, edgecolor="white", linewidth=0.5)
    ax.axvline(x=gcs_stats[gcs_stats["GCSTotal"] == 13].index[0] + 0.5
               if not gcs_stats[gcs_stats["GCSTotal"] == 13].empty else 1.5,
               color="black", linestyle="--", linewidth=1.2,
               label="GCS 13/14 cutoff")
    ax.set_xlabel("GCS Total Score")
    ax.set_ylabel("ciTBI Rate (%)")
    ax.set_title("ciTBI Rate by GCS Total Score")
    red_patch = mpatches.Patch(color="#d73027", label="GCS ≤13 (excluded)")
    blue_patch = mpatches.Patch(color="#4575b4", label="GCS 14–15 (analytic cohort)")
    ax.legend(handles=[red_patch, blue_patch], fontsize=8)
    plt.tight_layout()
    savefig("fig_gcs_outcome.png")


def print_gcs_table(df):
    """
    Print GCS breakdown table used in the Data section of the report.

    Shows patient counts and ciTBI rates for each GCS level (15, 14, 13, 12, ≤11),
    then prints the cohort derivation leading to the 42,412 analytic sample.
    """
    print("\nGCS breakdown (full cleaned dataset):")
    gcs_bins = [
        ("15",  df["GCSTotal"] == 15),
        ("14",  df["GCSTotal"] == 14),
        ("13",  df["GCSTotal"] == 13),
        ("12",  df["GCSTotal"] == 12),
        ("≤11", df["GCSTotal"] <= 11),
    ]
    rows = []
    for label, mask in gcs_bins:
        sub = df[mask & df["PosIntFinal"].notna()]
        n = len(sub)
        n_pos = int(sub["PosIntFinal"].sum())
        rate = n_pos / n * 100 if n > 0 else float("nan")
        rows.append({"GCS": label, "N": n, "ciTBI": n_pos, "Rate (%)": f"{rate:.1f}"})
    tbl = pd.DataFrame(rows)
    print(tbl.to_string(index=False))

    # Cohort derivation
    n_total = len(df)
    n_gcs_lt14 = int((df["GCSTotal"] <= 13).sum())
    df_mild = df[df["GCSTotal"] >= 14].copy()
    n_miss_outcome = int(df_mild["PosIntFinal"].isna().sum())
    n_final = len(df_mild[df_mild["PosIntFinal"].notna()])
    print(
        f"\n  Cohort derivation: {n_total:,} total"
        f" − {n_gcs_lt14:,} (GCS ≤13)"
        f" − {n_miss_outcome} (missing outcome)"
        f" = {n_final:,} analytic patients"
    )


# ══════════════════════════════════════════════════════════════════════════════
# FINDING 1 – Risk Is Nonlinear and Clustered, Not Gradual
#
# Hypothesis: ciTBI risk does not increase smoothly across features.
# It forms natural plateaus and sudden jumps rather than a smooth gradient.
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# FINDING 1 – Risk Is Nonlinear and Clustered, Not Gradual
#
# Hypothesis: ciTBI risk does not increase smoothly across features.
# It forms natural plateaus and sudden jumps rather than a smooth gradient.
# ══════════════════════════════════════════════════════════════════════════════

def _build_marginal_and_burden(df_elig):
    """Compute marginal dict and burden_stats for Finding 1."""
    y = df_elig["PosIntFinal"]
    feats = _avail(PECARN_BINARY, df_elig)

    marginal = {}
    for f in feats:
        sub = df_elig[[f, "PosIntFinal"]].dropna()
        pos_rate = sub[sub[f] == 1]["PosIntFinal"].mean() * 100
        n_pos_f  = int((sub[f] == 1).sum())
        neg_rate = sub[sub[f] == 0]["PosIntFinal"].mean() * 100
        marginal[f] = {"pos_rate": pos_rate, "neg_rate": neg_rate,
                       "n_pos": n_pos_f, "rr": pos_rate / (neg_rate + 1e-9)}

    marg_df = pd.DataFrame(marginal).T.sort_values("pos_rate")

    sub_burden = df_elig[feats + ["PosIntFinal"]].copy()
    sub_burden[feats] = sub_burden[feats].fillna(0)
    sub_burden["burden"] = sub_burden[feats].sum(axis=1).astype(int)
    burden_stats = (
        sub_burden.dropna(subset=["PosIntFinal"])
        .groupby("burden")["PosIntFinal"]
        .agg(["mean", "count"])
        .reset_index()
    )
    burden_stats = burden_stats[burden_stats["count"] >= 20]
    burden_stats["citbi_pct"] = burden_stats["mean"] * 100

    pairs = [("AMS", "SFxPalp"), ("Vomit", "HA_verb")]
    pairs = [(a, b) for a, b in pairs if a in df_elig.columns and b in df_elig.columns]

    overall = y.mean() * 100
    return marg_df, burden_stats, pairs, overall, feats


def fig_f1a_marginal_rates(df_elig):
    """Panel A: Marginal P(ciTBI | feature=1) for each PECARN binary predictor."""
    print("\nFigure [F1a]: marginal ciTBI rates …")
    marg_df, burden_stats, pairs, overall, feats = _build_marginal_and_burden(df_elig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ylabels = [FEATURE_LABELS.get(f, f) for f in marg_df.index]
    bar_c = [PALETTE[3] if r > 5 else (PALETTE[1] if r > 2 else PALETTE[2])
             for r in marg_df["pos_rate"]]
    ax.barh(ylabels, marg_df["pos_rate"], color=bar_c,
            edgecolor="black", linewidth=0.4)
    ax.axvline(overall, color="gray", linestyle="--", linewidth=1.2,
               label=f"Overall ({overall:.1f}%)")
    ax.set_xlabel("ciTBI Rate when Feature Present (%)")
    ax.set_title("Marginal ciTBI Rate by PECARN Predictor")
    ax.legend(fontsize=8)
    for i, (f, row) in enumerate(marg_df.iterrows()):
        ax.text(row["pos_rate"] + 0.2, i,
                f"{row['pos_rate']:.1f}%  n={row['n_pos']:,}",
                va="center", fontsize=7.5)
    plt.tight_layout()
    savefig("fig_f1a_marginal_rates.png")


def fig_f1b_burden(df_elig):
    """Panel B: P(ciTBI) by number of positive predictors (predictor burden)."""
    print("\nFigure [F1b]: predictor burden …")
    marg_df, burden_stats, pairs, overall, feats = _build_marginal_and_burden(df_elig)

    fig, ax = plt.subplots(figsize=(7, 5))
    cmap_b = matplotlib.colormaps.get_cmap("RdYlGn_r")
    max_b  = burden_stats["citbi_pct"].max()
    bar_c_b = cmap_b(burden_stats["citbi_pct"].values / (max_b + 1e-9))
    ax.bar(burden_stats["burden"].astype(str),
           burden_stats["citbi_pct"],
           color=bar_c_b, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Number of Positive PECARN Predictors")
    ax.set_ylabel("ciTBI Rate (%)")
    ax.set_title("Risk by Predictor Burden (Do rates jump or drift?)")
    ax.axhline(overall, color="gray", linestyle="--", linewidth=1,
               label=f"Overall ({overall:.1f}%)")
    ax.legend(fontsize=8)
    for i, row in burden_stats.iterrows():
        ax.text(
            burden_stats.index.get_loc(i),
            row["citbi_pct"] + 0.2,
            f"{row['citbi_pct']:.1f}%\n(n={int(row['count']):,})",
            ha="center", fontsize=8,
        )
    plt.tight_layout()
    savefig("fig_f1b_burden.png")
    return burden_stats


def fig_f1c_heatmaps(df_elig):
    """Panel C: Conditional risk heatmap for the two strongest feature pairs."""
    print("\nFigure [F1c]: pairwise risk heatmaps …")
    marg_df, burden_stats, pairs, overall, feats = _build_marginal_and_burden(df_elig)

    n_heat = len(pairs)
    # Each cell is 2×2 in display; keep the grid compact and square
    fig, heat_axes = plt.subplots(1, n_heat, figsize=(7 * n_heat, 5))
    if n_heat == 1:
        heat_axes = [heat_axes]

    for ax_h, (fa, fb) in zip(heat_axes, pairs):
        sub_p = df_elig[[fa, fb, "PosIntFinal"]].dropna()
        matrix = (
            sub_p.groupby([fa, fb])["PosIntFinal"]
            .agg(["mean", "count"])
            .reset_index()
        )
        matrix.columns = [fa, fb, "rate", "n"]
        matrix["citbi_pct"] = matrix["rate"] * 100
        pivot = matrix.pivot_table(values="citbi_pct", index=fa, columns=fb)
        count_pivot = matrix.pivot_table(values="n", index=fa, columns=fb)
        # Single-line annotation: "X.X% (n=NNN)"
        annot = np.array([
            [f"{v:.1f}%\n (n={int(c):,})" if not np.isnan(v) else "—"
             for v, c in zip(pivot.iloc[r], count_pivot.iloc[r])]
            for r in range(len(pivot))
        ])
        sns.heatmap(pivot, ax=ax_h, annot=annot, fmt="s",
                    cmap="YlOrRd", linewidths=1.0, linecolor="white",
                    annot_kws={"fontsize": 14, "fontweight": "normal"},
                    cbar_kws={"label": "ciTBI Rate (%)"},
                    vmin=0)
        fa_label = FEATURE_LABELS.get(fa, fa).replace("\n", " ")
        fb_label = FEATURE_LABELS.get(fb, fb).replace("\n", " ")
        ax_h.set_title(f"ciTBI Rate: {fa_label} × {fb_label}", fontsize=15, pad=6)
        ax_h.set_xlabel(fb_label, fontsize=14)
        ax_h.set_ylabel(fa_label, fontsize=14)
        ax_h.set_xticklabels(
            ["Absent (0)", "Present (1)"] if len(pivot.columns) == 2
            else [str(v) for v in pivot.columns],
            fontsize=11,
        )
        ax_h.set_yticklabels(
            ["Absent (0)", "Present (1)"] if len(pivot.index) == 2
            else [str(v) for v in pivot.index],
            fontsize=11, rotation=0,
        )

    plt.tight_layout()
    savefig("fig_f1c_heatmaps.png")

# ══════════════════════════════════════════════════════════════════════════════
# FINDING 2 – Feature Predictive Meaning Changes With Age
#
# Hypothesis: P(ciTBI | feature, age) varies substantially across developmental
# periods; the PECARN 24-month split may not capture all natural breakpoints.
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# FINDING 2 – Feature Predictive Meaning Changes With Age
#
# Hypothesis: P(ciTBI | feature, age) varies substantially across developmental
# periods; the PECARN 24-month split may not capture all natural breakpoints.
# ══════════════════════════════════════════════════════════════════════════════

def _build_risk_matrix(df_elig):
    """Build risk_matrix, rr_matrix, count_matrix, overall_by_age, readable_index."""
    feats = _avail(PECARN_BINARY, df_elig)

    df_e = df_elig.copy()
    df_e["AgeGroup"] = pd.cut(
        df_e["AgeInMonth"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        include_lowest=True,
        right=False,
    )

    risk_matrix = pd.DataFrame(index=feats, columns=AGE_LABELS, dtype=float)
    count_matrix = pd.DataFrame(index=feats, columns=AGE_LABELS, dtype=float)
    overall_by_age = {}

    for age_grp in AGE_LABELS:
        grp = df_e[df_e["AgeGroup"] == age_grp]
        overall_by_age[age_grp] = grp["PosIntFinal"].mean() * 100
        for f in feats:
            sub = grp[[f, "PosIntFinal"]].dropna()
            pos_grp = sub[sub[f] == 1]
            risk_matrix.loc[f, age_grp] = (
                pos_grp["PosIntFinal"].mean() * 100 if len(pos_grp) >= 10 else np.nan
            )
            count_matrix.loc[f, age_grp] = len(pos_grp)

    overall_series = pd.Series(overall_by_age)
    rr_matrix = risk_matrix.divide(overall_series + 1e-9)

    readable_index = [FEATURE_LABELS.get(f, f).replace("\n", " ") for f in feats]
    risk_matrix.index = readable_index
    rr_matrix.index   = readable_index
    count_matrix.index = readable_index

    return risk_matrix, rr_matrix, count_matrix, overall_by_age, readable_index


def fig_f2a_abs_heatmap(df_elig):
    """Panel A: Heatmap of P(ciTBI | feature=1, age bin) for all binary predictors."""
    print("\nFigure [F2a]: absolute risk heatmap …")
    if "AgeInMonth" not in df_elig.columns or not _avail(PECARN_BINARY, df_elig):
        print("  skipping: missing required columns")
        return None, None

    risk_matrix, rr_matrix, count_matrix, overall_by_age, readable_index = _build_risk_matrix(df_elig)

    fig, ax = plt.subplots(figsize=(9, 6))
    annot_a = np.array([
        [f"{risk_matrix.loc[f, a]:.1f}%\n(n={int(count_matrix.loc[f, a]):,})"
         if not pd.isna(risk_matrix.loc[f, a]) else "—"
         for a in AGE_LABELS]
        for f in readable_index
    ])
    sns.heatmap(
        risk_matrix.astype(float), ax=ax,
        annot=annot_a, fmt="s",
        cmap="YlOrRd", linewidths=0.4, linecolor="white",
        annot_kws={"fontsize": 7},
        cbar_kws={"label": "ciTBI Rate (%)"},
        vmin=0,
    )
    ax.set_title("P(ciTBI | Feature=1, Age) – Absolute Rate")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("")
    ax.set_xticklabels(AGE_LABELS, rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    savefig("fig_f2a_abs_heatmap.png")
    return risk_matrix, rr_matrix


def fig_f2b_risk_curves(df_elig):
    """Panel B: Age-specific risk curves for the three most variable features."""
    print("\nFigure [F2b]: age-specific risk curves …")
    if "AgeInMonth" not in df_elig.columns or not _avail(PECARN_BINARY, df_elig):
        print("  skipping: missing required columns")
        return

    risk_matrix, rr_matrix, count_matrix, overall_by_age, readable_index = _build_risk_matrix(df_elig)

    risk_range = risk_matrix.max(axis=1) - risk_matrix.min(axis=1)
    top3 = risk_range.nlargest(3).index.tolist()

    fig, ax = plt.subplots(figsize=(7, 5))
    for i, feat_label in enumerate(top3):
        rates = risk_matrix.loc[feat_label].astype(float).values
        valid = ~np.isnan(rates)
        ax.plot(
            np.array(AGE_LABELS)[valid],
            rates[valid],
            "o-",
            color=PALETTE[i],
            label=feat_label,
            linewidth=1.8,
            markersize=6,
        )
    overall_arr = np.array([overall_by_age[a] for a in AGE_LABELS])
    ax.plot(AGE_LABELS, overall_arr, "k--", linewidth=1,
            label="Age-group overall rate")
    ax.set_ylabel("ciTBI Rate (%)")
    ax.set_xlabel("Age Group")
    ax.set_title("Risk Curves for Most Age-Variable Features")
    ax.legend(fontsize=7.5)
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    savefig("fig_f2b_risk_curves.png")


def fig_f2c_rr_heatmap(df_elig):
    """Panel C: Relative risk (age-bin rate / overall rate) heatmap."""
    print("\nFigure [F2c]: relative risk heatmap …")
    if "AgeInMonth" not in df_elig.columns or not _avail(PECARN_BINARY, df_elig):
        print("  skipping: missing required columns")
        return

    risk_matrix, rr_matrix, count_matrix, overall_by_age, readable_index = _build_risk_matrix(df_elig)

    fig, ax = plt.subplots(figsize=(9, 6))
    annot_c = np.array([
        [f"{rr_matrix.loc[f, a]:.1f}×" if not pd.isna(rr_matrix.loc[f, a]) else "—"
         for a in AGE_LABELS]
        for f in readable_index
    ])
    sns.heatmap(
        rr_matrix.astype(float), ax=ax,
        annot=annot_c, fmt="s",
        cmap="RdBu_r", center=1.0, linewidths=0.4, linecolor="white",
        annot_kws={"fontsize": 7.5},
        cbar_kws={"label": "Relative Risk vs Age-Group Baseline"},
        vmin=0,
    )
    ax.set_title("Relative Risk (Feature Rate / Age Baseline)")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("")
    ax.set_xticklabels(AGE_LABELS, rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    savefig("fig_f2c_rr_heatmap.png")

# ══════════════════════════════════════════════════════════════════════════════
# FINDING 3 – Clinician CT Decision Encodes Hidden Signal
#
# Hypothesis: the decision to order CT reflects latent clinical information
# not captured in the structured PECARN features.
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# FINDING 3 – Clinician CT Decision Encodes Hidden Signal
#
# Hypothesis: the decision to order CT reflects latent clinical information
# not captured in the structured PECARN features.
# ══════════════════════════════════════════════════════════════════════════════

def _build_ct_data(df_elig):
    """Shared setup for Finding 3 panels."""
    ct_col = "CTDone"
    sub = df_elig.dropna(subset=[ct_col, "PosIntFinal"]).copy()
    sub["ct"] = sub[ct_col].astype(int)
    sub["citbi"] = sub["PosIntFinal"].astype(int)
    overall = sub["citbi"].mean() * 100
    feats = _avail(PECARN_BINARY, sub)
    return sub, overall, feats


def fig_f3a_ct_ams(df_elig):
    """Panel A: P(ciTBI | CT ordered) vs P(ciTBI | No CT), stratified by AMS status."""
    print("\nFigure [F3a]: CT decision × AMS …")
    ct_col = "CTDone"
    if ct_col not in df_elig.columns:
        print("  skipping: CTDone not available")
        return

    sub, overall, feats = _build_ct_data(df_elig)
    ams_col = "AMS" if "AMS" in sub.columns else None
    panel_a_data = {}
    if ams_col:
        for ams_val, ams_label in [(0, "AMS Absent"), (1, "AMS Present")]:
            for ct_val, ct_label in [(0, "No CT"), (1, "CT Ordered")]:
                grp = sub[(sub[ams_col] == ams_val) & (sub["ct"] == ct_val)]
                if len(grp) < 10:
                    continue
                key = f"{ams_label}\n{ct_label}"
                panel_a_data[key] = (grp["citbi"].mean() * 100, len(grp))
    else:
        for ct_val, ct_label in [(0, "No CT"), (1, "CT Ordered")]:
            grp = sub[sub["ct"] == ct_val]
            panel_a_data[ct_label] = (grp["citbi"].mean() * 100, len(grp))

    fig, ax = plt.subplots(figsize=(7, 5))
    a_labels = list(panel_a_data.keys())
    a_rates  = [panel_a_data[lbl][0] for lbl in a_labels]
    a_ns     = [panel_a_data[lbl][1] for lbl in a_labels]
    a_cols   = []
    for lbl in a_labels:
        if "CT Ordered" in lbl and "AMS Present" in lbl:
            a_cols.append(PALETTE[3])
        elif "CT Ordered" in lbl:
            a_cols.append(PALETTE[1])
        elif "AMS Present" in lbl:
            a_cols.append(PALETTE[5])
        else:
            a_cols.append(PALETTE[2])

    ax.bar(a_labels, a_rates, color=a_cols, edgecolor="black", linewidth=0.5)
    ax.axhline(overall, color="gray", linestyle="--", linewidth=1,
               label=f"Overall ({overall:.1f}%)")
    ax.set_ylabel("ciTBI Rate (%)")
    ax.set_title("P(ciTBI | CT Decision, AMS): Does CT Ordering Add Risk Signal?", pad=14)
    ax.legend(fontsize=8)
    for i, (r, n) in enumerate(zip(a_rates, a_ns)):
        ax.text(i, r + 0.05, f"{r:.1f}%\n(n={n:,})",
                ha="center", fontsize=8, fontweight="bold")
    plt.tight_layout()
    savefig("fig_f3a_ct_ams.png")


def fig_f3b_ct_vs_citbi(df_elig):
    """Panel B: For each PECARN feature: CT ordering rate vs ciTBI rate."""
    print("\nFigure [F3b]: CT rate vs ciTBI rate per feature …")
    ct_col = "CTDone"
    if ct_col not in df_elig.columns:
        print("  skipping: CTDone not available")
        return

    sub, overall, feats = _build_ct_data(df_elig)
    ct_vs_citbi = {}
    for f in feats:
        s = sub[[f, "ct", "citbi"]].dropna()
        pos = s[s[f] == 1]
        if len(pos) < 30:
            continue
        ct_vs_citbi[f] = {
            "ct_rate":    pos["ct"].mean() * 100,
            "citbi_rate": pos["citbi"].mean() * 100,
            "n":          len(pos),
        }

    fig, ax = plt.subplots(figsize=(7, 5))
    if ct_vs_citbi:
        xs, ys, texts = [], [], []
        for f, vals in ct_vs_citbi.items():
            lbl = FEATURE_LABELS.get(f, f).replace("\n", " ")
            ax.scatter(vals["ct_rate"], vals["citbi_rate"],
                       s=np.sqrt(vals["n"]) * 2,
                       color=PALETTE[0], edgecolors="black",
                       linewidths=0.5, alpha=0.8, zorder=3)
            xs.append(vals["ct_rate"])
            ys.append(vals["citbi_rate"])
            texts.append(ax.text(vals["ct_rate"], vals["citbi_rate"],
                                 f" {lbl}", fontsize=9.5, va="center"))
        # Repel overlapping labels; fall back to fixed offset if not installed
        try:
            from adjustText import adjust_text
            adjust_text(texts, x=xs, y=ys, ax=ax,
                        arrowprops=dict(arrowstyle="-", color="gray",
                                        lw=0.6, alpha=0.7),
                        expand=(1.4, 1.6), force_text=(0.5, 0.8))
        except ImportError:
            # Manual fallback: alternate offsets above/below the point
            for i, txt in enumerate(texts):
                sign = 1 if i % 2 == 0 else -1
                x0, y0 = xs[i], ys[i]
                txt.set_position((x0 + 0.8, y0 + sign * 0.4))
        xlim = ax.get_xlim()
        lim  = max(xlim[1],
                   max(v["ct_rate"] for v in ct_vs_citbi.values()) + 5)
        ax.plot([0, lim], [0, lim], "k--", linewidth=0.8,
                label="CT rate = ciTBI rate")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, max(v["citbi_rate"] for v in ct_vs_citbi.values()) * 1.3)
        ax.set_xlabel("CT Ordering Rate when Feature Present (%)")
        ax.set_ylabel("ciTBI Rate when Feature Present (%)")
        ax.set_title("CT Rate vs ciTBI Rate per Feature (Dots above line = under-imaging)")
        ax.legend(fontsize=8)
        ax.fill_between([0, lim], [0, lim], [0, 0],
                        alpha=0.06, color="green", label="Under-imaging zone")
        ax.fill_between([0, lim], [lim, lim], [0, lim],
                        alpha=0.06, color="red", label="Over-imaging zone")
    plt.tight_layout()
    savefig("fig_f3b_ct_vs_citbi.png")


def fig_f3c_feature_negative(df_elig):
    """Panel C: Among feature-negative patients, compare ciTBI rates by CT decision."""
    print("\nFigure [F3c]: feature-negative patients …")
    ct_col = "CTDone"
    if ct_col not in df_elig.columns:
        print("  skipping: CTDone not available")
        return {}

    sub, overall, feats = _build_ct_data(df_elig)
    fn_mask = sub[feats].fillna(0).sum(axis=1) == 0
    fn_sub  = sub[fn_mask]
    fn_ct_rate    = fn_sub["ct"].mean() * 100
    fn_notct_rate = fn_sub[fn_sub["ct"] == 0]["citbi"].mean() * 100
    fn_ct_citbi   = fn_sub[fn_sub["ct"] == 1]["citbi"].mean() * 100
    n_fn_ct  = int((fn_sub["ct"] == 1).sum())
    n_fn_noct = int((fn_sub["ct"] == 0).sum())
    print(
        f"  Feature-negative: n={len(fn_sub):,}  CT ordered in {fn_ct_rate:.1f}%\n"
        f"    ciTBI | CT=1: {fn_ct_citbi:.2f}%  ciTBI | CT=0: {fn_notct_rate:.2f}%"
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        [f"CT Ordered\n(n={n_fn_ct:,})", f"No CT\n(n={n_fn_noct:,})"],
        [fn_ct_citbi, fn_notct_rate],
        color=[PALETTE[1], PALETTE[2]], edgecolor="black", linewidth=0.6,
    )
    ax.axhline(overall, color="gray", linestyle="--", linewidth=1,
               label=f"Overall ({overall:.1f}%)")
    ax.set_ylabel("ciTBI Rate (%)")
    ax.set_title(
        "Feature-Negative Patients: ciTBI Rate by CT Decision\n"
        "(0 recorded PECARN predictors)",
    )
    ax.legend(fontsize=8)
    for bar, r in zip(bars, [fn_ct_citbi, fn_notct_rate]):
        ax.text(bar.get_x() + bar.get_width() / 2, r + 0.05,
                f"{r:.2f}%", ha="center", fontsize=10, fontweight="bold")
    plt.tight_layout()
    savefig("fig_f3c_feature_negative.png")
    return {"fn_ct_citbi": fn_ct_citbi, "fn_notct_citbi": fn_notct_rate,
            "fn_ct_rate": fn_ct_rate}

# ══════════════════════════════════════════════════════════════════════════════
# Stability check – perturb the age developmental split (24 mo → 18 mo)
# Tests whether Finding 2's age-feature interaction pattern is robust.
# ══════════════════════════════════════════════════════════════════════════════

def fig_stability(df_elig):
    """
    Judgment call: Finding 2 uses 24 months as the infant/toddler boundary
    (matching the PECARN CDR).  We perturb to 18 months to test sensitivity.

    Show before-and-after risk curves for the three most variable features:
    if the pattern holds, the finding is stable.
    """
    print("\nFigure [Stability]: age split perturbation (24 mo → 18 mo) …")
    feats = _avail(PECARN_BINARY, df_elig)
    if "AgeInMonth" not in df_elig.columns or not feats:
        print("  skipping: required columns missing")
        return

    def _compute_risk_curves(df, bins, labels):
        """Return DataFrame of P(ciTBI | feature=1, age_bin) for each feature."""
        df2 = df.copy()
        df2["AG"] = pd.cut(df2["AgeInMonth"], bins=bins, labels=labels,
                           include_lowest=True, right=False)
        rows = {}
        for f in feats:
            row = {}
            for ag in labels:
                sub = df2[df2["AG"] == ag][[f, "PosIntFinal"]].dropna()
                pos = sub[sub[f] == 1]
                row[ag] = pos["PosIntFinal"].mean() * 100 if len(pos) >= 10 else np.nan
            rows[f] = row
        return pd.DataFrame(rows).T

    # Original: PECARN bins (0,12,24,60,144,216)
    orig_labels = ["<1 yr", "1–2 yr", "2–5 yr", "5–12 yr", "12–18 yr"]
    orig_risk   = _compute_risk_curves(df_elig, AGE_BINS, orig_labels)

    # Perturbed: shift infant boundary from 24 mo to 18 mo
    pert_bins   = [0, 12, 18, 60, 144, 216]
    pert_labels = ["<1 yr", "1–1.5 yr", "1.5–5 yr", "5–12 yr", "12–18 yr"]
    pert_risk   = _compute_risk_curves(df_elig, pert_bins, pert_labels)

    # Pick three most variable features from original analysis
    risk_range = orig_risk.max(axis=1) - orig_risk.min(axis=1)
    top3 = risk_range.dropna().nlargest(3).index.tolist()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(
        "Stability Check: Age Developmental Split 24 months → 18 months\n"
        "(Does Finding 2's age-feature interaction pattern change?)",
        fontsize=11, fontweight="bold",
    )

    for ax, risk_df, labels, title in [
        (axes[0], orig_risk,   orig_labels, "Original: boundary at 24 months"),
        (axes[1], pert_risk,   pert_labels, "Perturbed: boundary at 18 months"),
    ]:
        for i, f in enumerate(top3):
            row = risk_df.loc[f].astype(float)
            valid = ~row.isna()
            ax.plot(
                np.array(labels)[valid.values],
                row.values[valid.values],
                "o-", color=PALETTE[i],
                label=FEATURE_LABELS.get(f, f).replace("\n", " "),
                linewidth=1.8, markersize=6,
            )
        ax.set_ylabel("ciTBI Rate (%)")
        ax.set_xlabel("Age Group")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", rotation=20)

    plt.tight_layout()
    savefig("fig_stability.png")


# ══════════════════════════════════════════════════════════════════════════════
# Part 2 – Modeling
# ══════════════════════════════════════════════════════════════════════════════

def run_models(df):
    """
    Train and evaluate three models on a stratified 80/20 split:
    1. Kuppermann CDR (rule-based, no training required)
    2. Logistic Regression (L2, balanced class weights)
    3. Random Forest (ensemble, balanced class weights)

    Produces ROC + PR curves and feature importance figures.
    """
    print("\nModeling …")
    outcome_col = "PosIntFinal"
    df_model = df.dropna(subset=[outcome_col]).copy()
    y = df_model[outcome_col].astype(int)
    X = df_model.drop(columns=[outcome_col])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    cdr = KuppermannCDR()
    lr  = AgeStratifiedLR(C=1.0, class_weight={0: 1, 1: 120}, random_state=42)
    rf  = RandomForestModel(n_estimators=200, max_depth=8,
                            class_weight={0: 1, 1: 120}, random_state=42)

    models  = {"Kuppermann CDR": cdr, "Age-Stratified LR": lr, "Random Forest": rf}
    results = {}
    fitted  = {}

    for name, model in models.items():
        print(f"  training {name} …")
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test, model_name=name)
        results[name] = metrics
        fitted[name]  = model
        print(metrics)

    # ── ROC + PR curves ───────────────────────────────────────────────────────
    print("Figure: ROC + PR curves …")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    colors_roc = [PALETTE[3], PALETTE[0], PALETTE[1]]

    for (name, model), col in zip(fitted.items(), colors_roc):
        proba     = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, proba)
        auroc     = roc_auc_score(y_test, proba)
        axes[0].plot(fpr, tpr, label=f"{name} (AUC={auroc:.3f})",
                     color=col, linewidth=1.8)

    axes[0].plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Random")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curves – ciTBI Prediction")
    axes[0].legend(fontsize=8)

    for (name, model), col in zip(fitted.items(), colors_roc):
        proba     = model.predict_proba(X_test)[:, 1]
        prec, rec, _ = precision_recall_curve(y_test, proba)
        auprc     = average_precision_score(y_test, proba)
        axes[1].plot(rec, prec, label=f"{name} (AP={auprc:.3f})",
                     color=col, linewidth=1.8)

    baseline = y_test.mean()
    axes[1].axhline(baseline, color="gray", linestyle="--", linewidth=0.8,
                    label=f"Baseline ({baseline:.3f})")
    axes[1].set_xlabel("Recall (Sensitivity)")
    axes[1].set_ylabel("Precision (PPV)")
    axes[1].set_title("Precision–Recall Curves – ciTBI Prediction")
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    savefig("fig_model_roc_prc.png")

    # ── Feature importance ────────────────────────────────────────────────────
    print("Figure: feature importance …")
    lr_imp = fitted["Age-Stratified LR"].get_feature_importance(stratum='ge2').head(15)
    rf_imp = fitted["Random Forest"].get_feature_importance().head(15)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors_lr = [PALETTE[3] if c > 0 else PALETTE[0] for c in lr_imp["Coefficient"]]
    axes[0].barh(lr_imp["Feature"][::-1], lr_imp["Coefficient"][::-1],
                 color=colors_lr[::-1], edgecolor="white", linewidth=0.4)
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("Coefficient (standardised)")
    axes[0].set_title("Logistic Regression – Top 15 Coefficients")

    axes[1].barh(rf_imp["Feature"][::-1], rf_imp["Importance"][::-1],
                 color=PALETTE[1], edgecolor="white", linewidth=0.4)
    axes[1].set_xlabel("Mean Decrease in Impurity")
    axes[1].set_title("Random Forest – Top 15 Feature Importances")

    plt.tight_layout()
    savefig("fig_feature_importance.png")

    # ── Model stability under class weight ratio variation ────────────────────
    print("Figure: model stability across class weight ratios …")
    # The minority class weight of 120 is a judgment call (1.76% prevalence
    # ≈ 57:1 imbalance, so 120 is ≈2× the inverse frequency).  We test
    # ratios [20, 40, 60, 80, 100, 120, 150, 200] to see whether the
    # sensitivity/specificity trade-off is stable or sensitive to this choice.
    CLASS_WEIGHTS = [20, 40, 60, 80, 100, 120, 150, 200]
    weight_labels = [str(w) for w in CLASS_WEIGHTS]

    stab_rows = []
    for w in CLASS_WEIGHTS:
        lr_w = AgeStratifiedLR(C=1.0, class_weight={0: 1, 1: w}, random_state=42)
        lr_w.fit(X_train, y_train)

        rf_w = RandomForestModel(n_estimators=200, max_depth=8,
                                 class_weight={0: 1, 1: w}, random_state=42)
        rf_w.fit(X_train, y_train)

        for name, model in [("Age-Stratified LR", lr_w), ("Random Forest", rf_w)]:
            res = evaluate_model(model, X_test, y_test)
            overall = res[res["AgeGroup"] == "Overall"].iloc[0]
            stab_rows.append({
                "weight": w, "model": name,
                "Sensitivity": overall["Sensitivity"],
                "Specificity": overall["Specificity"],
                "AUROC":       overall["AUROC"],
            })

    stab_df = pd.DataFrame(stab_rows)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    colors = {
        "Age-Stratified LR": PALETTE[0],
        "Random Forest":     PALETTE[1],
    }
    for ax, metric, title, ylim in zip(
        axes,
        ["Sensitivity", "Specificity", "AUROC"],
        ["Sensitivity vs class weight",
         "Specificity vs class weight",
         "AUROC vs class weight"],
        [(0.70, 1.02), (0.0, 1.02), (0.70, 1.0)],
    ):
        for name, col in colors.items():
            sub = stab_df[stab_df["model"] == name].sort_values("weight")
            ax.plot(weight_labels, sub[metric].values,
                    "o-", color=col, linewidth=1.8, markersize=6, label=name)
            for x, y_val in zip(weight_labels, sub[metric].values):
                ax.annotate(f"{y_val:.3f}", (x, y_val),
                            textcoords="offset points", xytext=(0, 6),
                            ha="center", fontsize=6.5)
        ax.axvline(weight_labels.index("120"), color="gray",
                   linestyle="--", linewidth=1, label="Default (120)")
        ax.set_xlabel("Minority class weight")
        ax.set_ylabel(metric)
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.tick_params(axis="x", rotation=20)
        if metric == "Sensitivity":
            ax.legend(fontsize=8)

    plt.suptitle(
        "Model Stability: Sensitivity to the Minority Class Weight\n"
        "(default = 120; dashed line)",
        fontsize=11,
    )
    plt.tight_layout()
    savefig("fig_model_stability.png")

    print("\n  Stability summary (LR across class weights):")
    lr_sub = stab_df[stab_df["model"] == "Age-Stratified LR"]
    for _, row in lr_sub.iterrows():
        print(f"    w={int(row['weight']):3d}  "
              f"sens={row['Sensitivity']:.3f}  "
              f"spec={row['Specificity']:.3f}  "
              f"auroc={row['AUROC']:.3f}")
    print("  Stability summary (RF across class weights):")
    rf_sub = stab_df[stab_df["model"] == "Random Forest"]
    for _, row in rf_sub.iterrows():
        print(f"    w={int(row['weight']):3d}  "
              f"sens={row['Sensitivity']:.3f}  "
              f"spec={row['Specificity']:.3f}  "
              f"auroc={row['AUROC']:.3f}")

    # ── Print comparison table ────────────────────────────────────────────────
    print("\nModel Comparison:")
    res_df = pd.concat(results.values(), ignore_index=True)[
        ["Model", "AgeGroup", "Sensitivity", "Specificity", "PPV", "NPV",
         "AUROC", "AUPRC", "TP", "FP", "FN", "TN"]
    ]
    print(res_df.to_string(float_format="{:.3f}".format, index=False))

    return fitted, results, X_test, y_test


# ══════════════════════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    df_raw, df, df_elig = load_and_clean()

    # ── Data-section figures ──────────────────────────────────────────────────
    fig_missing(df_raw)
    fig_outcome(df_elig)
    fig_age(df_elig)
    fig_gcs_outcome(df)
    print_gcs_table(df)

    # ── Part 1: Three EDA findings ────────────────────────────────────────────
    fig_f1a_marginal_rates(df_elig)
    burden_stats = fig_f1b_burden(df_elig)
    fig_f1c_heatmaps(df_elig)
    risk_matrix, rr_matrix = fig_f2a_abs_heatmap(df_elig)
    fig_f2b_risk_curves(df_elig)
    fig_f2c_rr_heatmap(df_elig)
    fig_f3a_ct_ams(df_elig)
    fig_f3b_ct_vs_citbi(df_elig)
    clinician_results = fig_f3c_feature_negative(df_elig)

    # ── Stability check ───────────────────────────────────────────────────────
    fig_stability(df_elig)

    # ── Part 2: Modeling ──────────────────────────────────────────────────────
    fitted, results, X_test, y_test = run_models(df_elig)

    print(f"\nAll figures saved to {FIG_DIR}")
