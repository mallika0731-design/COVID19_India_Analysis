# COVID19_India_Analysis_Local.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from prophet import Prophet
import geopandas as gpd
import os
import warnings
warnings.filterwarnings('ignore')

# -----------------------------
# Set page config
# -----------------------------
st.set_page_config(layout="wide", page_title="COVID-19 India Dashboard (Local Data)")

# -----------------------------
# 1️⃣ Local Data Folder
# -----------------------------
# Update this path to your Desktop 'data' folder
BASE_DIR = r"C:\Users\Lenovo\Desktop\data"

covid_file = os.path.join(BASE_DIR, "covid_cases.csv")
vacc_file = os.path.join(BASE_DIR, "vaccination.csv")
pop_file = os.path.join(BASE_DIR, "population.csv")
geo_file = os.path.join(BASE_DIR, "states_geojson.geojson")

# -----------------------------
# 2️⃣ Load Data
# -----------------------------
st.header("1️⃣ Load Data from Local Folder")
covid_df = pd.read_csv(covid_file)
vacc_df = pd.read_csv(vacc_file)
pop_df = pd.read_csv(pop_file)
states_geo = gpd.read_file(geo_file)
st.success("✅ Data loaded successfully from local folder.")

# -----------------------------
# 3️⃣ Clean Data
# -----------------------------
covid_df['Date'] = pd.to_datetime(covid_df['Date'], dayfirst=True)
vacc_df['Updated On'] = pd.to_datetime(vacc_df['Updated On'], dayfirst=True)

state_cols = [col for col in covid_df.columns if col not in ['Date','Status']]
covid_pivot = covid_df.pivot(index='Date', columns='Status', values=state_cols).fillna(0)
covid_pivot.columns = ['_'.join(col).strip() for col in covid_pivot.columns.values]
covid_pivot.reset_index(inplace=True)

latest_vacc = vacc_df.groupby('Updated On').sum().reset_index()
merged_df = pd.merge(covid_pivot, latest_vacc, left_on='Date', right_on='Updated On', how='left').fillna(0)

pop_df = pop_df[['State','Population']]
state_population = dict(zip(pop_df['State'], pop_df['Population']))

for state in state_cols:
    merged_df[f'{state}_cases_per_million'] = merged_df[f'Confirmed_{state}'] / state_population.get(state,1) * 1e6
    merged_df[f'{state}_vacc_per_million'] = merged_df.get(f'{state}_total_doses_administered',0)/state_population.get(state,1)*1e6

st.write("✅ Data cleaned and per-million metrics computed.")

# -----------------------------
# 4️⃣ Interactive Dashboard
# -----------------------------
st.header("2️⃣ Interactive Dashboard")
selected_states = st.multiselect("Select States", options=state_cols, default=state_cols[:5])
date_range = st.date_input("Select Date Range", [merged_df['Date'].min(), merged_df['Date'].max()])
start_date, end_date = date_range
filtered_df = merged_df[(merged_df['Date']>=pd.to_datetime(start_date)) & (merged_df['Date']<=pd.to_datetime(end_date))]

# Key metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Confirmed", int(filtered_df[[f'Confirmed_{s}' for s in selected_states]].sum().sum()))
col2.metric("Total Recovered", int(filtered_df[[f'Recovered_{s}' for s in selected_states]].sum().sum()))
col3.metric("Total Deaths", int(filtered_df[[f'Deceased_{s}' for s in selected_states]].sum().sum()))
col4.metric("Total Vaccinations", int(filtered_df[[s+'_total_doses_administered' for s in selected_states if s+'_total_doses_administered' in filtered_df.columns]].sum().sum()))

# Line Charts
st.subhead
