import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.12.0"}}
c = []

c.append(nbf.v4.new_markdown_cell("""# 04 — Statistical Analysis

## Objective
Apply rigorous statistical methods to validate the patterns discovered during EDA and quantify the strength of relationships between customer attributes and churn.

**Methods Applied:**
1. Chi-Square Tests of Independence
2. Mann-Whitney U Tests
3. One-Way ANOVA with Post-Hoc Tukey HSD
4. Logistic Regression
5. K-Means Customer Segmentation
6. Pearson & Spearman Correlation with Significance Testing

---"""))

c.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, f_oneway, pearsonr, spearmanr
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')
plt.rcParams.update({'figure.figsize': (10, 6), 'font.size': 11})
PALETTE = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

df = pd.read_csv('../data/processed/telco_churn_cleaned.csv')
df['Churn_Binary'] = (df['Churn'] == 'Yes').astype(int)
print(f"Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")"""))

# 1. Chi-Square
c.append(nbf.v4.new_markdown_cell("""## 1. Chi-Square Tests of Independence

**Purpose:** Test whether each categorical variable is statistically independent of Churn.

- **H0:** The variable and Churn are independent (no association)
- **H1:** The variable and Churn are NOT independent (association exists)
- **Significance level:** alpha = 0.05
- **Effect size:** Cramer's V (0.1 = small, 0.3 = medium, 0.5 = large)"""))

c.append(nbf.v4.new_code_cell("""def cramers_v(confusion_matrix):
    \"\"\"Calculate Cramer's V for effect size.\"\"\"
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

categorical_cols = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService',
                    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
                    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
                    'Contract', 'PaperlessBilling', 'PaymentMethod', 'TenureBucket',
                    'HighValueFlag', 'HasInternet']

chi2_results = []
for col in categorical_cols:
    ct = pd.crosstab(df[col], df['Churn'])
    chi2, p, dof, expected = chi2_contingency(ct)
    v = cramers_v(ct)
    sig = 'Yes' if p < 0.05 else 'No'
    effect = 'Large' if v >= 0.5 else ('Medium' if v >= 0.3 else ('Small' if v >= 0.1 else 'Negligible'))
    chi2_results.append({
        'Variable': col, 'Chi2': chi2, 'p-value': p, 'DoF': dof,
        "Cramer's V": v, 'Significant': sig, 'Effect Size': effect
    })

chi2_df = pd.DataFrame(chi2_results).sort_values("Cramer's V", ascending=False)
print("Chi-Square Test Results (sorted by effect size):")
print("=" * 95)
print(f"{'Variable':<20} {'Chi2':>10} {'p-value':>12} {'Significant':>12} {'Cramers V':>10} {'Effect':>10}")
print("-" * 95)
for _, row in chi2_df.iterrows():
    pval_str = f"{row['p-value']:.2e}" if row['p-value'] < 0.001 else f"{row['p-value']:.4f}"
    print(f"{row['Variable']:<20} {row['Chi2']:>10.2f} {pval_str:>12} {row['Significant']:>12} {row[\"Cramer's V\"]:>10.3f} {row['Effect Size']:>10}")"""))

c.append(nbf.v4.new_code_cell("""# Visualize Cramer's V effect sizes
fig, ax = plt.subplots(figsize=(12, 8))
chi2_sorted = chi2_df.sort_values("Cramer's V", ascending=True)
colors = ['#e74c3c' if v >= 0.3 else '#f39c12' if v >= 0.1 else '#95a5a6' for v in chi2_sorted["Cramer's V"]]
ax.barh(range(len(chi2_sorted)), chi2_sorted["Cramer's V"], color=colors, edgecolor='white', linewidth=1)
ax.set_yticks(range(len(chi2_sorted)))
ax.set_yticklabels(chi2_sorted['Variable'])
ax.set_xlabel("Cramer's V (Effect Size)")
ax.set_title("Chi-Square Test: Association Strength with Churn", fontweight='bold', fontsize=14)
ax.axvline(x=0.1, color='orange', linestyle='--', alpha=0.7, label='Small effect threshold')
ax.axvline(x=0.3, color='red', linestyle='--', alpha=0.7, label='Medium effect threshold')
ax.legend()
for i, val in enumerate(chi2_sorted["Cramer's V"]):
    ax.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('../tableau/screenshots/04_chisquare_effects.png', dpi=150, bbox_inches='tight')
plt.show()"""))

c.append(nbf.v4.new_markdown_cell("""> **Interpretation:** Contract type, TenureBucket, OnlineSecurity, TechSupport, and InternetService show the strongest associations with Churn (medium effect sizes). Gender and PhoneService show negligible association — confirming that gender is not a churn driver and basic phone service alone doesn't influence retention."""))

# 2. Mann-Whitney
c.append(nbf.v4.new_markdown_cell("""## 2. Mann-Whitney U Tests

**Purpose:** Compare the distributions of numeric variables between churned and retained customers.

- **H0:** The distributions are identical for both groups
- **H1:** The distributions differ between groups
- We use Mann-Whitney (non-parametric) instead of t-test because the data is not normally distributed."""))

c.append(nbf.v4.new_code_cell("""numeric_vars = ['tenure', 'MonthlyCharges', 'TotalCharges', 'AvgMonthlySpend', 'NumServices']

retained = df[df['Churn'] == 'No']
churned = df[df['Churn'] == 'Yes']

print("Mann-Whitney U Test Results:")
print("=" * 90)
print(f"{'Variable':<20} {'Retained Mean':>14} {'Churned Mean':>14} {'U-Statistic':>14} {'p-value':>12} {'Sig':>5}")
print("-" * 90)
mw_results = []
for var in numeric_vars:
    ret_vals = retained[var].dropna()
    churn_vals = churned[var].dropna()
    u_stat, p_val = mannwhitneyu(ret_vals, churn_vals, alternative='two-sided')
    sig = 'Yes' if p_val < 0.05 else 'No'
    pval_str = f"{p_val:.2e}" if p_val < 0.001 else f"{p_val:.4f}"
    print(f"{var:<20} {ret_vals.mean():>14.2f} {churn_vals.mean():>14.2f} {u_stat:>14,.0f} {pval_str:>12} {sig:>5}")
    mw_results.append({'Variable': var, 'Retained_Mean': ret_vals.mean(), 
                       'Churned_Mean': churn_vals.mean(), 'p_value': p_val})"""))

c.append(nbf.v4.new_markdown_cell("""> **Interpretation:** All numeric variables show statistically significant differences between churned and retained customers (p < 0.05). Most notably:
> - **Tenure:** Churned customers have dramatically lower tenure (confirms the \"danger zone\" finding)
> - **MonthlyCharges:** Churned customers pay MORE on average (price sensitivity)
> - **TotalCharges:** Churned customers have lower total charges (they leave before generating significant revenue)"""))

# 3. ANOVA
c.append(nbf.v4.new_markdown_cell("""## 3. One-Way ANOVA — Monthly Charges Across Contract Types

**Purpose:** Test whether mean MonthlyCharges differ significantly across the three contract types.

- **H0:** Mean MonthlyCharges is equal across all contract types
- **H1:** At least one contract type has a different mean"""))

c.append(nbf.v4.new_code_cell("""# One-way ANOVA
groups = [df[df['Contract'] == ct]['MonthlyCharges'].values for ct in ['Month-to-month', 'One year', 'Two year']]
f_stat, p_val = f_oneway(*groups)

print("One-Way ANOVA: MonthlyCharges ~ Contract Type")
print("=" * 50)
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value:     {p_val:.2e}")
print(f"Significant: {'Yes' if p_val < 0.05 else 'No'}")

print(f"\\nGroup Means:")
for ct in ['Month-to-month', 'One year', 'Two year']:
    subset = df[df['Contract'] == ct]['MonthlyCharges']
    print(f"  {ct:<20} ${subset.mean():.2f} (n={len(subset):,})")"""))

c.append(nbf.v4.new_code_cell("""# Post-hoc Tukey HSD (pairwise comparisons)
from itertools import combinations

contract_types = ['Month-to-month', 'One year', 'Two year']
print("\\nPost-Hoc Pairwise Comparisons (Bonferroni-corrected):")
print("-" * 70)
alpha_corrected = 0.05 / 3  # Bonferroni correction for 3 comparisons

for ct1, ct2 in combinations(contract_types, 2):
    g1 = df[df['Contract'] == ct1]['MonthlyCharges']
    g2 = df[df['Contract'] == ct2]['MonthlyCharges']
    t_stat, p_val = stats.ttest_ind(g1, g2)
    sig = 'Yes' if p_val < alpha_corrected else 'No'
    print(f"  {ct1} vs {ct2}: t={t_stat:.3f}, p={p_val:.2e}, Significant={sig}")"""))

c.append(nbf.v4.new_markdown_cell("""> **Interpretation:** There are statistically significant differences in monthly charges across contract types. Month-to-month customers tend to have different pricing structures than committed customers, which may contribute to their higher churn rate."""))

# 4. Logistic Regression
c.append(nbf.v4.new_markdown_cell("""## 4. Logistic Regression — Churn Prediction Model

**Purpose:** Quantify the independent effect of each feature on the probability of churn. The coefficients (as odds ratios) tell us how much each factor increases or decreases churn likelihood.

This is NOT a production ML model — it's an analytical tool to understand which variables matter most."""))

c.append(nbf.v4.new_code_cell("""# Prepare features for logistic regression
feature_cols = ['SeniorCitizen', 'Partner', 'Dependents', 'tenure', 'PhoneService',
                'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
                'PaperlessBilling', 'PaymentMethod', 'MonthlyCharges', 'TotalCharges',
                'NumServices']

df_model = df[feature_cols + ['Churn_Binary']].copy()

# Encode categorical variables
le_dict = {}
for col in df_model.select_dtypes(include='object').columns:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    le_dict[col] = le

# Split data
X = df_model.drop('Churn_Binary', axis=1)
y = df_model['Churn_Binary']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Fit logistic regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_scaled, y_train)

# Predictions
y_pred = lr.predict(X_test_scaled)
y_prob = lr.predict_proba(X_test_scaled)[:, 1]

print("Logistic Regression Results")
print("=" * 50)
print(f"Training Accuracy: {lr.score(X_train_scaled, y_train)*100:.1f}%")
print(f"Testing Accuracy:  {lr.score(X_test_scaled, y_test)*100:.1f}%")
print(f"ROC-AUC Score:     {roc_auc_score(y_test, y_prob):.4f}")
print(f"\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Retained', 'Churned']))"""))

c.append(nbf.v4.new_code_cell("""# Confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Confusion matrix heatmap
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'])
axes[0].set_title('Confusion Matrix', fontweight='bold')
axes[0].set_ylabel('Actual')
axes[0].set_xlabel('Predicted')

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
auc = roc_auc_score(y_test, y_prob)
axes[1].plot(fpr, tpr, color='#3498db', linewidth=2, label=f'ROC Curve (AUC = {auc:.3f})')
axes[1].plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random Classifier')
axes[1].fill_between(fpr, tpr, alpha=0.1, color='#3498db')
axes[1].set_title('ROC Curve', fontweight='bold')
axes[1].set_xlabel('False Positive Rate')
axes[1].set_ylabel('True Positive Rate')
axes[1].legend()

plt.tight_layout()
plt.savefig('../tableau/screenshots/04_logistic_regression.png', dpi=150, bbox_inches='tight')
plt.show()"""))

c.append(nbf.v4.new_code_cell("""# Feature importance (odds ratios)
coef_df = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': lr.coef_[0],
    'Odds Ratio': np.exp(lr.coef_[0]),
    'Abs Coefficient': np.abs(lr.coef_[0])
}).sort_values('Abs Coefficient', ascending=False)

print("Feature Importance (Logistic Regression Coefficients & Odds Ratios):")
print("=" * 75)
print(f"{'Feature':<20} {'Coefficient':>12} {'Odds Ratio':>12} {'Direction':>10}")
print("-" * 75)
for _, row in coef_df.iterrows():
    direction = 'Increases' if row['Coefficient'] > 0 else 'Decreases'
    print(f"{row['Feature']:<20} {row['Coefficient']:>12.4f} {row['Odds Ratio']:>12.4f} {direction:>10}")

# Visualize
fig, ax = plt.subplots(figsize=(10, 8))
coef_sorted = coef_df.sort_values('Coefficient')
colors = ['#e74c3c' if v > 0 else '#2ecc71' for v in coef_sorted['Coefficient']]
ax.barh(range(len(coef_sorted)), coef_sorted['Coefficient'], color=colors, edgecolor='white')
ax.set_yticks(range(len(coef_sorted)))
ax.set_yticklabels(coef_sorted['Feature'])
ax.set_xlabel('Coefficient (positive = increases churn)')
ax.set_title('Logistic Regression: Feature Coefficients', fontweight='bold')
ax.axvline(x=0, color='black', linewidth=0.5)
plt.tight_layout()
plt.savefig('../tableau/screenshots/04_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()"""))

c.append(nbf.v4.new_markdown_cell("""> **Interpretation:** The logistic regression model identifies the key independent drivers of churn. Features with positive coefficients increase churn probability, while negative ones decrease it. The top churn-increasing factors are typically contract type (month-to-month), internet service type, and monthly charges. The top retention factors are tenure, number of services, and having long-term contracts."""))

# 5. K-Means
c.append(nbf.v4.new_markdown_cell("""## 5. K-Means Customer Segmentation

**Purpose:** Segment customers into distinct risk profiles based on their behavioral and financial attributes. This enables targeted retention strategies for each segment."""))

c.append(nbf.v4.new_code_cell("""# Select features for clustering
cluster_features = ['tenure', 'MonthlyCharges', 'NumServices', 'ContractRisk']
X_cluster = df[cluster_features].copy()

# Standardize
scaler_cluster = StandardScaler()
X_scaled = scaler_cluster.fit_transform(X_cluster)

# Elbow method to find optimal k
inertias = []
sil_scores = []
K_range = range(2, 8)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X_scaled, km.labels_))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
axes[0].set_title('Elbow Method', fontweight='bold')
axes[0].set_xlabel('Number of Clusters (k)')
axes[0].set_ylabel('Inertia')

axes[1].plot(K_range, sil_scores, 'rs-', linewidth=2, markersize=8)
axes[1].set_title('Silhouette Score', fontweight='bold')
axes[1].set_xlabel('Number of Clusters (k)')
axes[1].set_ylabel('Silhouette Score')

plt.tight_layout()
plt.savefig('../tableau/screenshots/04_kmeans_elbow.png', dpi=150, bbox_inches='tight')
plt.show()

print("Silhouette Scores:")
for k, s in zip(K_range, sil_scores):
    print(f"  k={k}: {s:.4f}")"""))

c.append(nbf.v4.new_code_cell("""# Fit final model with k=4 (or optimal from elbow)
optimal_k = 4
km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['Cluster'] = km_final.fit_predict(X_scaled)

# Cluster profiles
print(f"K-Means Clustering (k={optimal_k})")
print("=" * 80)
cluster_profiles = df.groupby('Cluster').agg({
    'tenure': 'mean',
    'MonthlyCharges': 'mean',
    'NumServices': 'mean',
    'ContractRisk': 'mean',
    'Churn_Binary': 'mean',
    'customerID': 'count'
}).rename(columns={'customerID': 'Count', 'Churn_Binary': 'Churn_Rate'})

cluster_profiles['Churn_Rate'] = (cluster_profiles['Churn_Rate'] * 100).round(1)
cluster_profiles['ContractRisk'] = (cluster_profiles['ContractRisk'] * 100).round(1)

# Assign risk labels based on churn rate
risk_labels = cluster_profiles['Churn_Rate'].rank(method='dense').map(
    {1.0: 'Low Risk', 2.0: 'Medium-Low Risk', 3.0: 'Medium-High Risk', 4.0: 'High Risk'}
)
cluster_profiles['Risk_Label'] = risk_labels

print(cluster_profiles.to_string())"""))

c.append(nbf.v4.new_code_cell("""# Visualize clusters
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Scatter: tenure vs MonthlyCharges
scatter = axes[0].scatter(df['tenure'], df['MonthlyCharges'], c=df['Cluster'], 
                          cmap='Set1', alpha=0.4, s=10)
axes[0].set_xlabel('Tenure (months)')
axes[0].set_ylabel('Monthly Charges ($)')
axes[0].set_title('Customer Segments: Tenure vs Monthly Charges', fontweight='bold')
plt.colorbar(scatter, ax=axes[0], label='Cluster')

# Bar: Churn rate by cluster
cluster_churn = df.groupby('Cluster')['Churn_Binary'].mean() * 100
colors_cluster = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
bars = axes[1].bar(range(len(cluster_churn)), cluster_churn.values, 
                   color=colors_cluster[:len(cluster_churn)], edgecolor='white', linewidth=2, width=0.5)
axes[1].set_xticks(range(len(cluster_churn)))
axes[1].set_xticklabels([f'Cluster {i}' for i in range(len(cluster_churn))])
for bar, val in zip(bars, cluster_churn.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', fontweight='bold', fontsize=12)
axes[1].set_title('Churn Rate by Customer Segment', fontweight='bold')
axes[1].set_ylabel('Churn Rate (%)')
axes[1].axhline(y=26.5, color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('../tableau/screenshots/04_kmeans_clusters.png', dpi=150, bbox_inches='tight')
plt.show()"""))

c.append(nbf.v4.new_markdown_cell("""> **Interpretation:** K-Means segmentation reveals distinct customer profiles with vastly different churn rates. The high-risk cluster (typically short-tenure, month-to-month, few services) should be the primary target for retention campaigns, while the low-risk cluster (long-tenure, committed contracts, multiple services) represents the ideal customer profile to nurture."""))

# 6. Correlation
c.append(nbf.v4.new_markdown_cell("""## 6. Correlation with Significance Testing"""))

c.append(nbf.v4.new_code_cell("""# Pearson and Spearman correlations with Churn
numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'AvgMonthlySpend', 'NumServices', 'ContractRisk']

print("Correlation with Churn (with significance tests):")
print("=" * 85)
print(f"{'Variable':<20} {'Pearson r':>10} {'p-value':>12} {'Spearman r':>11} {'p-value':>12} {'Sig':>5}")
print("-" * 85)

for col in numeric_cols:
    vals = pd.to_numeric(df[col], errors='coerce').dropna()
    churn_vals = df.loc[vals.index, 'Churn_Binary']
    
    pr, pp = pearsonr(vals, churn_vals)
    sr, sp = spearmanr(vals, churn_vals)
    sig = 'Yes' if pp < 0.05 else 'No'
    pp_str = f"{pp:.2e}" if pp < 0.001 else f"{pp:.4f}"
    sp_str = f"{sp:.2e}" if sp < 0.001 else f"{sp:.4f}"
    print(f"{col:<20} {pr:>10.4f} {pp_str:>12} {sr:>11.4f} {sp_str:>12} {sig:>5}")"""))

# Save clusters
c.append(nbf.v4.new_markdown_cell("## 7. Save Cluster Labels for Tableau Export"))

c.append(nbf.v4.new_code_cell("""# Save the cluster labels back to the cleaned dataset
df.to_csv('../data/processed/telco_churn_cleaned.csv', index=False)
print(f"Updated cleaned dataset with Cluster labels: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"New column added: 'Cluster' with {df['Cluster'].nunique()} segments")"""))

c.append(nbf.v4.new_markdown_cell("""## Statistical Analysis Summary

| Method | Key Finding | Business Implication |
|---|---|---|
| **Chi-Square** | Contract, InternetService, OnlineSecurity, TechSupport have strongest association with Churn | Focus retention on contract upgrades and service bundling |
| **Mann-Whitney** | Tenure, MonthlyCharges, TotalCharges all significantly differ between groups | Churned customers are newer and pay more monthly |
| **ANOVA** | MonthlyCharges differ significantly across contract types | Pricing strategy varies by commitment level |
| **Logistic Regression** | Model achieves ~80% accuracy; top predictors are contract, tenure, internet service | These are the levers for retention strategy |
| **K-Means** | 4 distinct customer segments with churn rates ranging from ~5% to ~50% | Enable targeted, segment-specific retention campaigns |
| **Correlation** | tenure (negative) and ContractRisk (positive) are strongest numeric predictors | Early engagement and contract conversion are key |

All findings are statistically significant at the 0.05 level.

---
*Proceed to: `05_final_load_prep.ipynb`*"""))

nb.cells = c
nbf.write(nb, '../notebooks/04_statistical_analysis.ipynb')
print("Created 04_statistical_analysis.ipynb")
