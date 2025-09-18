import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")

# -----------------------------
# Load Data
# -----------------------------
covid_file = os.path.join(DATA_PATH, "covid_cases_sample.csv")
districts_file = os.path.join(DATA_PATH, "districts_cases.csv")
population_file = os.path.join(DATA_PATH, "population_sample.csv")
states_file = os.path.join(DATA_PATH, "states_cases.csv")
vaccination_file = os.path.join(DATA_PATH, "vaccination_sample.csv")
vaccination_statewise_file = os.path.join(DATA_PATH, "vaccination_statewise.csv")
geojson_file = os.path.join(DATA_PATH, "states_sample.geojson")

covid_df = pd.read_csv(covid_file)
districts_df = pd.read_csv(districts_file)
population_df = pd.read_csv(population_file)
states_df = pd.read_csv(states_file)
vaccination_df = pd.read_csv(vaccination_file)
vaccination_statewise_df = pd.read_csv(vaccination_statewise_file)
india_states = gpd.read_file(geojson_file)

# -----------------------------
# Clean Dates
# -----------------------------
for df in [covid_df, districts_df, states_df, vaccination_df]:
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
        # Drop rows where Date could not be parsed
        df.dropna(subset=["Date"], inplace=True)

# -----------------------------
# Streamlit Dashboard
# -----------------------------
st.title("COVID-19 India Analysis Project (Advance Dashboard)")

st.sidebar.header("Navigation")
options = [
    "Dataset Overview",
    "COVID Cases Trend",
    "State-wise Cases",
    "District-wise Cases",
    "Population vs Cases",
    "Vaccination Progress",
    "Statewise Vaccination",
    "Active Cases Over Time",
    "Top States by Cases",
    "Heatmap Correlations",
    "Geospatial Map"
]
choice = st.sidebar.radio("Go to:", options)

# 1. Dataset Overview
if choice == "Dataset Overview":
    st.subheader("Dataset Overview")
    st.write("COVID Dataset Sample")
    st.dataframe(covid_df.head())
    st.write("District Dataset Sample")
    st.dataframe(districts_df.head())
    st.write("Population Dataset Sample")
    st.dataframe(population_df.head())
    st.write("States Dataset Sample")
    st.dataframe(states_df.head())
    st.write("Vaccination Dataset Sample")
    st.dataframe(vaccination_df.head())

# 2. COVID Cases Trend
elif choice == "COVID Cases Trend":
    st.subheader("COVID-19 Cases Trend in India")
    daily_cases = covid_df.groupby("Date")["Confirmed"].sum().reset_index()
    st.line_chart(daily_cases.set_index("Date"))

# 3. State-wise Cases
elif choice == "State-wise Cases":
    st.subheader("State-wise Confirmed Cases")
    state_cases = states_df.groupby("State")["Confirmed"].max().sort_values(ascending=False)
    st.bar_chart(state_cases)

# 4. District-wise Cases
elif choice == "District-wise Cases":
    st.subheader("District-wise Confirmed Cases")
    district_cases = districts_df.groupby("District")["Confirmed"].max().nlargest(15)
    st.bar_chart(district_cases)

# 5. Population vs Cases
elif choice == "Population vs Cases":
    st.subheader("Population vs Confirmed Cases")
    # Ensure 'State' column exists and drop rows with missing values
    states_clean = states_df.dropna(subset=["State", "Confirmed"])
    population_clean = population_df.dropna(subset=["State", "Population"])
    merged = states_clean.merge(population_clean, on="State", how="inner")
    # Ensure numeric types for plotting
    merged["Population"] = pd.to_numeric(merged["Population"], errors="coerce")
    merged["Confirmed"] = pd.to_numeric(merged["Confirmed"], errors="coerce")
    merged = merged.dropna(subset=["Population", "Confirmed"])
    fig, ax = plt.subplots()
    sns.scatterplot(x="Population", y="Confirmed", data=merged, ax=ax)
    st.pyplot(fig)

# 6. Vaccination Progress
elif choice == "Vaccination Progress":
    st.subheader("Vaccination Progress Overview")
    # Use columns: 'total_doses_administered', 'first_dose', 'second_dose'
    vax_cols = ["total_doses_administered", "first_dose", "second_dose"]
    available_cols = [col for col in vax_cols if col in vaccination_df.columns]
    if available_cols:
        total_vax = vaccination_df[available_cols].sum()
        st.bar_chart(total_vax)
    else:
        st.error("Required vaccination columns not found in the dataset.")

# 7. Statewise Vaccination
elif choice == "Statewise Vaccination":
    st.subheader("Statewise Vaccination Coverage")
    # Standardize column names to strip spaces
    vaccination_statewise_df.columns = [col.strip() for col in vaccination_statewise_df.columns]
    required_cols = ["State", "total_doses_administered", "first_dose", "second_dose"]
    if all(col in vaccination_statewise_df.columns for col in required_cols):
        vax_statewise = vaccination_statewise_df.dropna(subset=["State"])
        # Show total doses administered per state
        vax_statewise_grouped = vax_statewise.groupby("State")[["total_doses_administered", "first_dose", "second_dose"]].sum()
        st.bar_chart(vax_statewise_grouped)
    else:
        st.error("Required columns 'State', 'total_doses_administered', 'first_dose', and 'second_dose' not found in statewise vaccination data.")

# 8. Active Cases Over Time
elif choice == "Active Cases Over Time":
    st.subheader("Active Cases Trend")
    active_cases = covid_df.groupby("Date")["Active"].sum().reset_index()
    st.line_chart(active_cases.set_index("Date"))

# 9. Top States by Cases
elif choice == "Top States by Cases":
    st.subheader("Top 10 States by Confirmed Cases")
    top_states = states_df.groupby("State")["Confirmed"].max().nlargest(10)
    st.bar_chart(top_states)

# 10. Heatmap Correlations
elif choice == "Heatmap Correlations":
    st.subheader("Correlation Heatmap")
    corr = covid_df[["Confirmed", "Recovered", "Deceased", "Active"]].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# 11. Geospatial Map
elif choice == "Geospatial Map":
    st.subheader("Geospatial Map of Cases")
    merged = india_states.merge(states_df, left_on="ST_NM", right_on="State", how="left")
    merged = merged.fillna(0)
    st.write(merged[["ST_NM", "Confirmed", "geometry"]].head())
    # Ensure CRS is WGS84 for st.map
    merged = merged.to_crs(epsg=4326)
    # Extract centroid latitude and longitude for each state
    merged["lat"] = merged.geometry.centroid.y
    merged["lon"] = merged.geometry.centroid.x
    st.map(merged[["lat", "lon", "Confirmed"]])

