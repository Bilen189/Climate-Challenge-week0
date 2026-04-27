"""
Clean a single country CSV using the same logic as Task 2.
Usage:  python scripts/clean_country.py kenya
"""
import sys, os
import pandas as pd
import numpy as np
from scipy import stats

country = sys.argv[1].lower()
src = f"data/{country}.csv"
dst = f"data/{country}_clean.csv"

df = pd.read_csv(src)

# 1. Build a real Date column from YEAR + DOY
df["Date"] = pd.to_datetime(df["YEAR"].astype(str) + df["DOY"].astype(str), format="%Y%j")

# 2. Z-score outlier flagging (|Z| > 3)
zcols = ["T2M","T2M_MAX","T2M_MIN","PRECTOTCORR","RH2M","WS2M","WS2M_MAX"]
z = np.abs(stats.zscore(df[zcols], nan_policy="omit"))
outliers = (z > 3).any(axis=1)
print(f"{country}: {outliers.sum()} outlier rows flagged")

# 3. Decision: KEEP outliers (climate extremes are real signal, not errors)
#    -> we only forward-fill any missing values
df = df.ffill()

# 4. Drop rows where >30% values are missing (safety net)
df = df.dropna(thresh=int(df.shape[1] * 0.7))

# 5. Export
os.makedirs("data", exist_ok=True)
df.to_csv(dst, index=False)
print(f"✅ Saved {dst}  shape={df.shape}")
