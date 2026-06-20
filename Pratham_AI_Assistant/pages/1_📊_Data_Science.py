import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Science Matrix", layout="wide")
st.title("📊 Data Science & Analytical Matrix")

# --- Step 1: Data Acquisition ---
st.header("📂 Data Acquisition")
uploaded_file = st.file_uploader("Upload simulation CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Data Loaded Successfully!")
    
    # --- Step 2: Exploratory Data Analysis (EDA) ---
    st.header("🔍 Exploratory Data Analysis")
    st.write("### Data Preview", df.head())
    
    # Statistical Summary
    if st.checkbox("Show Statistical Summary"):
        st.write(df.describe())

    # --- Step 3: Visualization ---
    st.header("📈 Research Visualizations")
    numeric_cols = df.select_dtypes(include=[npnumber]).columns.tolist()
    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("Select X-Axis", numeric_cols)
        y_axis = st.selectbox("Select Y-Axis", numeric_cols)
        
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
        st.pyplot(fig)
else:
    st.info("Upload a CSV file to begin your 7.2 THz waveguide analysis.")
