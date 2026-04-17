# Data Dictionary — Telco Customer Churn

## Source

- **Dataset:** IBM Watson Analytics Sample Dataset — Telco Customer Churn
- **File:** `WA_Fn-UseC_-Telco-Customer-Churn.csv`
- **Records:** 7,043 customers
- **Columns:** 21 (raw) + 6 engineered = 27 total after ETL

---

## Raw Columns (Original Dataset)

### Identifiers

| Column | Data Type | Description | Example Values |
|---|---|---|---|
| `customerID` | String | Unique identifier for each customer | 7590-VHVEG, 5575-GNVDE |

### Demographics

| Column | Data Type | Description | Values | Distribution |
|---|---|---|---|---|
| `gender` | Categorical | Customer's gender | Male, Female | Male: 3,555 (50.5%), Female: 3,488 (49.5%) |
| `SeniorCitizen` | Binary (0/1) | Whether the customer is a senior citizen (65+) | 0 = No, 1 = Yes | No: 5,901 (83.8%), Yes: 1,142 (16.2%) |
| `Partner` | Categorical | Whether the customer has a partner | Yes, No | Yes: 3,402 (48.3%), No: 3,641 (51.7%) |
| `Dependents` | Categorical | Whether the customer has dependents | Yes, No | No: 4,933 (70.0%), Yes: 2,110 (30.0%) |

### Account Information

| Column | Data Type | Description | Values / Range | Notes |
|---|---|---|---|---|
| `tenure` | Integer | Number of months the customer has been with the company | 0 - 72 | Mean: 32.4 months |
| `Contract` | Categorical | Type of contract | Month-to-month, One year, Two year | Month-to-month: 3,875 (55.0%) |
| `PaperlessBilling` | Categorical | Whether the customer uses paperless billing | Yes, No | Yes: 4,171 (59.2%) |
| `PaymentMethod` | Categorical | Customer's payment method | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) | Electronic check: 2,365 (33.6%) |

### Services

| Column | Data Type | Description | Values | Notes |
|---|---|---|---|---|
| `PhoneService` | Categorical | Whether the customer has phone service | Yes, No | Yes: 6,361 (90.3%) |
| `MultipleLines` | Categorical | Whether the customer has multiple phone lines | Yes, No, No phone service | "No phone service" = PhoneService is No |
| `InternetService` | Categorical | Customer's internet service provider type | DSL, Fiber optic, No | Fiber optic: 3,096 (43.9%) |
| `OnlineSecurity` | Categorical | Whether the customer has online security add-on | Yes, No, No internet service | "No internet service" = InternetService is No |
| `OnlineBackup` | Categorical | Whether the customer has online backup add-on | Yes, No, No internet service | |
| `DeviceProtection` | Categorical | Whether the customer has device protection add-on | Yes, No, No internet service | |
| `TechSupport` | Categorical | Whether the customer has tech support add-on | Yes, No, No internet service | |
| `StreamingTV` | Categorical | Whether the customer has streaming TV add-on | Yes, No, No internet service | |
| `StreamingMovies` | Categorical | Whether the customer has streaming movies add-on | Yes, No, No internet service | |

### Financials

| Column | Data Type | Description | Range | Notes |
|---|---|---|---|---|
| `MonthlyCharges` | Float | The amount charged to the customer monthly | $18.25 - $118.75 | Mean: $64.76 |
| `TotalCharges` | String (needs conversion) | The total amount charged to the customer | $18.80 - $8,684.80 | **11 blank values** (tenure = 0 customers). Must convert to float. |

### Target Variable

| Column | Data Type | Description | Values | Distribution |
|---|---|---|---|---|
| `Churn` | Categorical | Whether the customer left the company | Yes, No | **No: 5,174 (73.5%), Yes: 1,869 (26.5%)** |

---

## Engineered Features (Created During ETL)

| Column | Data Type | Formula | Business Purpose |
|---|---|---|---|
| `AvgMonthlySpend` | Float | `TotalCharges / max(tenure, 1)` | Reveals actual spending pattern over customer lifecycle |
| `NumServices` | Integer (0-6) | Count of subscribed add-ons: OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | Measures service bundle depth — more services often = lower churn |
| `TenureBucket` | Categorical | Binned tenure: New (0-12), Growing (13-24), Mature (25-48), Loyal (49-72) | Customer lifecycle stage for segmented analysis |
| `HighValueFlag` | Boolean | `MonthlyCharges > 75th percentile` | Identifies premium customers for targeted retention |
| `HasInternet` | Boolean | `InternetService != 'No'` | Simplifies internet-based segmentation |
| `ContractRisk` | Binary (0/1) | `1 if Contract == 'Month-to-month' else 0` | Quick binary risk flag for filtering |

---

## Data Quality Notes

| Issue | Details | Resolution |
|---|---|---|
| `TotalCharges` blanks | 11 rows with empty TotalCharges (all have tenure = 0) | Set to 0.0 — these are brand-new customers who haven't been billed yet |
| `TotalCharges` type | Stored as string in raw CSV | Convert to float64 after handling blanks |
| `SeniorCitizen` encoding | Uses 0/1 while all other categoricals use Yes/No | Convert to Yes/No for consistency |
| No duplicates | All 7,043 customerIDs are unique | No action needed |
| No date column | Dataset is a snapshot, not time-series | Analysis focuses on cross-sectional patterns; tenure serves as the time proxy |
