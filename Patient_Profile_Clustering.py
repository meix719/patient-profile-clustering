"""Patient profile clustering for an academic analysis.

Run in VS Code with Class 5 - Dataset.xlsx in this script's folder.
Required packages: pandas, openpyxl, matplotlib, seaborn, scikit-learn.
Outputs: elbow chart, cluster scatterplots, and cluster summary CSV.
The original dataset is required to reproduce the reported results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Keep the Excel dataset in the same folder as this script.
file_path = Path(__file__).resolve().parent / "Class 5 - Dataset.xlsx"
# Load the worksheet containing one row per patient.
df = pd.read_excel(file_path, sheet_name="Raw Data")

print("Number of patients:", len(df))

# Use measurements only; Patient ID is an identifier, not a clustering feature.
feature_columns = [
    "Age",
    "BMI",
    "Blood Pressure (mmHg)",
    "Cholesterol (mg/dL)",
    "Doctor Visits"
]

# Convert measurements to numeric values and stop if a value is missing or invalid.
features = df[feature_columns].apply(pd.to_numeric, errors="coerce")

print("\nMissing values:")
print(features.isnull().sum())

if features.isnull().any().any():
    raise ValueError("Address missing or nonnumeric feature values before clustering.")

# Standardize so variables measured on larger scales do not dominate distances.
df[feature_columns] = features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Compare within-cluster variation for K = 1 through 8.
# A bend in this curve can inform K; it does not prove that a choice is optimal.
k_values = range(1, 9)
inertia_values = []

for k in k_values:
    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )
    model.fit(scaled_features)
    inertia_values.append(model.inertia_)

sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(7, 4))

ax.plot(list(k_values), inertia_values, marker="o")
ax.set_title("Elbow Method")
ax.set_xlabel("Number of clusters (K)")
ax.set_ylabel("Inertia")
ax.set_xticks(list(k_values))

fig.tight_layout()
fig.savefig(file_path.parent / "patient_elbow.png", dpi=200, bbox_inches="tight")

# Use three clusters for this assignment, not as a validated clinical grouping.
# random_state makes the result reproducible; n_init tries multiple starts.
kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

# Add one so labels read 1, 2, 3. Cluster numbers are labels, not risk scores.
df["Cluster"] = kmeans.fit_predict(scaled_features) + 1

# Summarize original units for interpretation; clustering used standardized values.
summary = df.groupby("Cluster")[feature_columns].mean()
summary.insert(0, "Patients", df.groupby("Cluster").size())

print("\nAVERAGE PATIENT PROFILE BY CLUSTER")
print(summary.round(2).to_string())

print("\nPATIENT CLUSTER ASSIGNMENTS")
print(df[["Patient ID", "Cluster"]].to_string(index=False))

# Plot the observed patient profiles. These plots do not establish causation.
palette = {
    1: "#0072B2",
    2: "#E69F00",
    3: "#CC79A7"
}

plot_pairs = [
    ("Age", "BMI"),
    ("BMI", "Blood Pressure (mmHg)"),
    ("Age", "Cholesterol (mg/dL)"),
    ("Age", "Doctor Visits")
]

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

for ax, (x_column, y_column) in zip(axes.flat, plot_pairs):
    sns.scatterplot(
        data=df,
        x=x_column,
        y=y_column,
        hue="Cluster",
        hue_order=[1, 2, 3],
        palette=palette,
        s=65,
        alpha=0.85,
        ax=ax
    )

    ax.set_title(f"{y_column} vs. {x_column}")
    ax.legend(title="Cluster")

fig.suptitle("Patient Groups Identified by K-Means", fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.96])

fig.savefig(file_path.parent / "patient_clusters.png", dpi=200, bbox_inches="tight")
summary.to_csv(file_path.parent / "patient_cluster_summary.csv")

# Group averages support exploratory planning, not diagnosis or visit schedules.
plt.show()
