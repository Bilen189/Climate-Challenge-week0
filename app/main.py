import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="African Climate Dashboard", layout="wide")
st.title("🌍 African Climate Dashboard — COP32")

COUNTRIES = ["ethiopia","kenya","sudan","tanzania","nigeria"]

@st.cache_data
def load_data():
    frames = []
    for c in COUNTRIES:
        path = f"data/{c}_clean.csv"
        if os.path.exists(path):
            d = pd.read_csv(path)
            d["country"] = c.capitalize()
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
sel_countries = st.sidebar.multiselect("Country", df["country"].unique(), default=list(df["country"].unique()))
yr_min, yr_max = int(df["YEAR"].min()), int(df["YEAR"].max())
yr_range = st.sidebar.slider("Year range", yr_min, yr_max, (yr_min, yr_max))
variable = st.sidebar.selectbox("Variable", ["T2M","T2M_MAX","PRECTOTCORR","RH2M","WS2M"])

# Filter
mask = (df["country"].isin(sel_countries)) & (df["YEAR"].between(*yr_range))
f = df[mask]

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("Mean Temp (°C)", f"{f['T2M'].mean():.2f}")
c2.metric("Total rainfall (mm)", f"{f['PRECTOTCORR'].sum():,.0f}")
c3.metric("Hot days (>35°C)", int((f['T2M_MAX']>35).sum()))

# Time series
st.subheader(f"{variable} over time")
ts = f.groupby(["Date","country"])[variable].mean().reset_index()
fig = px.line(ts, x="Date", y=variable, color="country")
st.plotly_chart(fig, use_container_width=True)

# Boxplot
st.subheader(f"{variable} distribution by country")
fig2 = px.box(f, x="country", y=variable, color="country")
st.plotly_chart(fig2, use_container_width=True)

st.caption("Data: NASA POWER (MERRA-2). Built for the COP32 EthioClimate Analytics challenge.")
