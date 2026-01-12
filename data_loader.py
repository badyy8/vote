import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=True)
def get_contestants_df():
    df = pd.read_csv(
        "data/contest_2_names_clean.csv"
    )
    return df

@st.cache_data(show_spinner=True)
def load_data():

    df = pd.read_csv('data/final_cleaned.csv')

    return df

@st.cache_data(show_spinner=True)
def get_raw_df():

    df = pd.read_csv("raw_data.csv")
    return df