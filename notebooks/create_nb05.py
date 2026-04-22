import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.12.0"}}
c = []

c.append(nbf.v4.new_markdown_cell("""# 05 — KPI Framework & Tableau Data Preparation

## Objective
Define and compute Key Performance Indicators (KPIs), then export Tableau-ready datasets for dashboard creation.

**Deliverables:**
1. KPI definitions and computed values
2. `tableau_main.csv` — Full cleaned dataset
3. `tableau_kpi_summary.csv` — Pre-aggregated KPIs
4. `tableau_segment_churn.csv` — Churn rates by segment
5. `tableau_cluster_profiles.csv` — K-Means cluster profiles

---"""))

c.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('../data/processed/telco_churn_cleaned.csv')
df['Churn_Binary'] = (df['Churn'] == 'Yes').astype(int)
print(f"Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")"""))

# KPI 1
c.append(nbf.v4.new_markdown_cell("""## 1. KPI Definitions & Computation

### KPI 1: Overall Churn Rate
**Formula:** (Customers Churned / Total Customers) x 100  
**Purpose:** Primary health metric — the headline number for executive reporting."""))

c.append(nbf.v4.new_code_cell("""churn_rate = df['Churn_Binary'].mean() * 100
print(f"Overall Churn Rate: {churn_rate:.1f}%")
print(f"  Churned: {df['Churn_Binary'].sum():,}")
print(f"  Retained: {(df['Churn_Binary'] == 0).sum():,}")
print(f"  Total: {len(df):,}")"""))

# KPI 2
c.append(nbf.v4.new_markdown_cell("""### KPI 2: Monthly Revenue at Risk
**Formula:** Sum of MonthlyCharges for all churned customers  
**Purpose:** Quantifies the direct financial impact of churn."""))

c.append(nbf.v4.new_code_cell("""monthly_rev_at_risk = df[df['Churn'] == 'Yes']['MonthlyCharges'].sum()
total_monthly_rev = df['MonthlyCharges'].sum()
rev_at_risk_pct = monthly_rev_at_risk / total_monthly_rev * 100

print(f"Monthly Revenue at Risk: ${monthly_rev_at_risk:,.2f}")
print(f"Total Monthly Revenue:   ${total_monthly_rev:,.2f}")
print(f"Revenue at Risk %:       {rev_at_risk_pct:.1f}%")
print(f"Annualized Revenue Loss: ${monthly_rev_at_risk * 12:,.2f}")"""))

# KPI 3
c.append(nbf.v4.new_markdown_cell("""### KPI 3: Customer Lifetime Value (CLV) by Segment
**Formula:** Average TotalCharges per segment  
**Purpose:** Helps prioritize which customer segments to invest in retaining."""))

c.append(nbf.v4.new_code_cell("""clv_by_segment = df.groupby('TenureBucket').agg(
    Avg_CLV=('TotalCharges', 'mean'),
    Median_CLV=('TotalCharges', 'median'),
    Count=('customerID', 'count'),
    Churn_Rate=('Churn_Binary', 'mean')
).round(2)

bucket_order = ['New (0-12)', 'Growing (13-24)', 'Mature (25-48)', 'Loyal (49-72)']
clv_by_segment = clv_by_segment.reindex(bucket_order)
clv_by_segment['Churn_Rate'] = (clv_by_segment['Churn_Rate'] * 100).round(1)

print("Customer Lifetime Value by Tenure Segment:")
print(clv_by_segment.to_string())"""))

# KPI 4
c.append(nbf.v4.new_markdown_cell("""### KPI 4: Average Revenue Per User (ARPU)
**Formula:** Average MonthlyCharges across all customers  
**Purpose:** Pricing benchmark and revenue density metric."""))

c.append(nbf.v4.new_code_cell("""arpu_overall = df['MonthlyCharges'].mean()
arpu_retained = df[df['Churn'] == 'No']['MonthlyCharges'].mean()
arpu_churned = df[df['Churn'] == 'Yes']['MonthlyCharges'].mean()

print(f"ARPU (Overall):  ${arpu_overall:.2f}/month")
print(f"ARPU (Retained): ${arpu_retained:.2f}/month")
print(f"ARPU (Churned):  ${arpu_churned:.2f}/month")
print(f"\\nChurned customers pay ${arpu_churned - arpu_retained:.2f} MORE per month on average.")"""))

# KPI 5
c.append(nbf.v4.new_markdown_cell("""### KPI 5: Service Adoption Rate
**Formula:** Percentage of internet customers subscribed to each add-on  
**Purpose:** Identifies upsell opportunities and their retention impact."""))

c.append(nbf.v4.new_code_cell("""service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
                'TechSupport', 'StreamingTV', 'StreamingMovies']
internet_users = df[df['InternetService'] != 'No']

print("Service Adoption Rates (Internet Users Only):")
print("=" * 65)
print(f"{'Service':<20} {'Adoption %':>12} {'Churn w/':>10} {'Churn w/o':>10}")
print("-" * 65)
svc_data = []
for svc in service_cols:
    adopted = (internet_users[svc] == 'Yes').mean() * 100
    churn_with = internet_users[internet_users[svc] == 'Yes']['Churn_Binary'].mean() * 100
    churn_without = internet_users[internet_users[svc] == 'No']['Churn_Binary'].mean() * 100
    print(f"  {svc:<20} {adopted:>10.1f}% {churn_with:>9.1f}% {churn_without:>9.1f}%")
    svc_data.append({'Service': svc, 'Adoption_Rate': adopted, 
                     'Churn_With': churn_with, 'Churn_Without': churn_without})
print(f"\\nTotal internet users: {len(internet_users):,}")"""))

# KPI 6
c.append(nbf.v4.new_markdown_cell("""### KPI 6: Contract Stability Index
**Formula:** Percentage of customers on 1-year or 2-year contracts  
**Purpose:** Measures overall customer commitment level."""))

c.append(nbf.v4.new_code_cell("""long_term = (df['Contract'] != 'Month-to-month').mean() * 100
print(f"Contract Stability Index: {long_term:.1f}%")
print(f"  Month-to-month: {(df['Contract'] == 'Month-to-month').sum():,} ({(df['Contract'] == 'Month-to-month').mean()*100:.1f}%)")
print(f"  One year:       {(df['Contract'] == 'One year').sum():,} ({(df['Contract'] == 'One year').mean()*100:.1f}%)")
print(f"  Two year:       {(df['Contract'] == 'Two year').sum():,} ({(df['Contract'] == 'Two year').mean()*100:.1f}%)")"""))

# KPI 7
c.append(nbf.v4.new_markdown_cell("""### KPI 7: High-Risk Customer Count & Revenue
**Formula:** Count of customers in the high-risk K-Means cluster  
**Purpose:** Sizes the retention campaign target audience."""))

c.append(nbf.v4.new_code_cell("""if 'Cluster' in df.columns:
    cluster_stats = df.groupby('Cluster').agg(
        Count=('customerID', 'count'),
        Churn_Rate=('Churn_Binary', 'mean'),
        Monthly_Rev=('MonthlyCharges', 'sum')
    )
    cluster_stats['Churn_Rate'] = (cluster_stats['Churn_Rate'] * 100).round(1)
    
    high_risk_cluster = cluster_stats['Churn_Rate'].idxmax()
    hr = cluster_stats.loc[high_risk_cluster]
    
    print(f"High-Risk Cluster (Cluster {high_risk_cluster}):")
    print(f"  Customer Count:     {int(hr['Count']):,}")
    print(f"  Churn Rate:         {hr['Churn_Rate']:.1f}%")
    print(f"  Monthly Revenue:    ${hr['Monthly_Rev']:,.2f}")
    print(f"  Annualized Revenue: ${hr['Monthly_Rev'] * 12:,.2f}")
else:
    print("Note: Run notebook 04 first to generate cluster labels.")"""))

# KPI Summary
c.append(nbf.v4.new_markdown_cell("## 2. KPI Summary Table"))

c.append(nbf.v4.new_code_cell("""kpi_summary = pd.DataFrame([
    {'KPI': 'Overall Churn Rate', 'Value': f'{churn_rate:.1f}%', 'Category': 'Health'},
    {'KPI': 'Monthly Revenue at Risk', 'Value': f'${monthly_rev_at_risk:,.0f}', 'Category': 'Financial'},
    {'KPI': 'Annualized Revenue Loss', 'Value': f'${monthly_rev_at_risk * 12:,.0f}', 'Category': 'Financial'},
    {'KPI': 'ARPU (Overall)', 'Value': f'${arpu_overall:.2f}', 'Category': 'Revenue'},
    {'KPI': 'ARPU (Churned)', 'Value': f'${arpu_churned:.2f}', 'Category': 'Revenue'},
    {'KPI': 'ARPU (Retained)', 'Value': f'${arpu_retained:.2f}', 'Category': 'Revenue'},
    {'KPI': 'Contract Stability Index', 'Value': f'{long_term:.1f}%', 'Category': 'Retention'},
    {'KPI': 'Total Customers', 'Value': f'{len(df):,}', 'Category': 'Scale'},
    {'KPI': 'Churned Customers', 'Value': f'{df["Churn_Binary"].sum():,}', 'Category': 'Scale'},
])
print(kpi_summary.to_string(index=False))"""))

# Tableau exports
c.append(nbf.v4.new_markdown_cell("""## 3. Tableau Data Exports

Exporting 4 purpose-built CSV files for Tableau dashboard creation."""))

c.append(nbf.v4.new_code_cell("""# Export 1: Main dataset
export_cols = [col for col in df.columns if col != 'Churn_Binary']
df[export_cols].to_csv('../data/processed/tableau_main.csv', index=False)
print(f"1. tableau_main.csv: {df[export_cols].shape[0]:,} rows x {df[export_cols].shape[1]} columns")"""))

c.append(nbf.v4.new_code_cell("""# Export 2: KPI Summary
kpi_summary.to_csv('../data/processed/tableau_kpi_summary.csv', index=False)
print(f"2. tableau_kpi_summary.csv: {len(kpi_summary)} KPIs")"""))

c.append(nbf.v4.new_code_cell("""# Export 3: Segment churn rates
segments = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'InternetService',
            'Contract', 'PaymentMethod', 'PaperlessBilling', 'TenureBucket', 
            'HighValueFlag', 'HasInternet']

segment_rows = []
for seg in segments:
    for val in df[seg].unique():
        subset = df[df[seg] == val]
        segment_rows.append({
            'Segment': seg,
            'Value': val,
            'Customer_Count': len(subset),
            'Churn_Count': subset['Churn_Binary'].sum(),
            'Churn_Rate': (subset['Churn_Binary'].mean() * 100).round(1),
            'Avg_Monthly_Charges': subset['MonthlyCharges'].mean().round(2),
            'Total_Monthly_Revenue': subset['MonthlyCharges'].sum().round(2),
            'Revenue_At_Risk': subset[subset['Churn'] == 'Yes']['MonthlyCharges'].sum().round(2)
        })

segment_df = pd.DataFrame(segment_rows)
segment_df.to_csv('../data/processed/tableau_segment_churn.csv', index=False)
print(f"3. tableau_segment_churn.csv: {len(segment_df)} segment-value combinations")
print(f"   Segments covered: {', '.join(segments)}")"""))

c.append(nbf.v4.new_code_cell("""# Export 4: Cluster profiles
if 'Cluster' in df.columns:
    cluster_export = df.groupby('Cluster').agg(
        Customer_Count=('customerID', 'count'),
        Avg_Tenure=('tenure', 'mean'),
        Avg_Monthly_Charges=('MonthlyCharges', 'mean'),
        Avg_Total_Charges=('TotalCharges', 'mean'),
        Avg_NumServices=('NumServices', 'mean'),
        Pct_Month_to_Month=('ContractRisk', 'mean'),
        Churn_Rate=('Churn_Binary', 'mean'),
        Total_Monthly_Revenue=('MonthlyCharges', 'sum'),
        Revenue_At_Risk=('MonthlyCharges', lambda x: df.loc[x.index][df.loc[x.index, 'Churn'] == 'Yes']['MonthlyCharges'].sum())
    ).round(2)
    
    cluster_export['Churn_Rate'] = (cluster_export['Churn_Rate'] * 100).round(1)
    cluster_export['Pct_Month_to_Month'] = (cluster_export['Pct_Month_to_Month'] * 100).round(1)
    
    risk_order = cluster_export['Churn_Rate'].rank(method='dense')
    risk_map = {1.0: 'Low', 2.0: 'Medium-Low', 3.0: 'Medium-High', 4.0: 'High'}
    cluster_export['Risk_Level'] = risk_order.map(risk_map)
    
    cluster_export.to_csv('../data/processed/tableau_cluster_profiles.csv')
    print(f"4. tableau_cluster_profiles.csv: {len(cluster_export)} clusters")
    print(cluster_export.to_string())
else:
    print("4. Skipped — run notebook 04 first for cluster labels.")"""))

c.append(nbf.v4.new_markdown_cell("""## 4. Tableau Dashboard Field Mapping

Use this reference when building the Tableau dashboard:

### Dashboard 1: Executive Summary
| Visual | Data Source | Fields |
|---|---|---|
| KPI Cards | `tableau_kpi_summary.csv` | KPI, Value |
| Churn Donut | `tableau_main.csv` | COUNT(Churn) |
| Churn by Tenure | `tableau_segment_churn.csv` | Segment='TenureBucket', Value, Churn_Rate |
| Top Drivers | `tableau_segment_churn.csv` | Sorted by Churn_Rate descending |

### Dashboard 2: Customer Risk Segments
| Visual | Data Source | Fields |
|---|---|---|
| Cluster Scatter | `tableau_main.csv` | tenure, MonthlyCharges, Cluster (color) |
| Cluster Profiles | `tableau_cluster_profiles.csv` | All fields |
| Customer Table | `tableau_main.csv` | Filtered by Cluster selection |

### Dashboard 3: Service & Contract Deep-Dive
| Visual | Data Source | Fields |
|---|---|---|
| Service Heatmap | `tableau_segment_churn.csv` | Filter Segment IN (service columns) |
| Contract Bars | `tableau_segment_churn.csv` | Filter Segment='Contract' |
| Payment Method | `tableau_segment_churn.csv` | Filter Segment='PaymentMethod' |

### Dashboard 4: Revenue Impact
| Visual | Data Source | Fields |
|---|---|---|
| Revenue Treemap | `tableau_segment_churn.csv` | Revenue_At_Risk by Segment |
| High-Value Scatter | `tableau_main.csv` | MonthlyCharges, TotalCharges, Churn (color) |
| Retention Actions | Manual text/annotations | Based on analysis findings |"""))

# Final verification
c.append(nbf.v4.new_markdown_cell("## 5. Final Verification"))

c.append(nbf.v4.new_code_cell("""import os

export_files = [
    'tableau_main.csv',
    'tableau_kpi_summary.csv', 
    'tableau_segment_churn.csv',
    'tableau_cluster_profiles.csv'
]

print("Export Verification:")
print("=" * 60)
for f in export_files:
    path = f'../data/processed/{f}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        rows = len(pd.read_csv(path))
        print(f"  {f:<35} {rows:>6} rows  {size/1024:>8.1f} KB")
    else:
        print(f"  {f:<35} MISSING")

print("\\nAll exports complete. Ready for Tableau dashboard creation.")"""))

c.append(nbf.v4.new_markdown_cell("""## Summary

### KPIs Computed
1. **Overall Churn Rate** — Primary health metric
2. **Monthly Revenue at Risk** — Financial impact quantification
3. **Customer Lifetime Value** — By tenure segment
4. **ARPU** — Revenue density metric
5. **Service Adoption Rate** — Upsell opportunities
6. **Contract Stability Index** — Customer commitment level
7. **High-Risk Customer Count** — Retention campaign sizing

### Tableau Exports
4 CSV files exported to `data/processed/` — ready for import into Tableau Public.

---
*Next: Build Tableau Dashboard (manual step — see field mapping above)*"""))

nb.cells = c
nbf.write(nb, '../notebooks/05_final_load_prep.ipynb')
print("Created 05_final_load_prep.ipynb")
