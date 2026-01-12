import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data
from itertools import combinations
from collections import Counter

# 1. Load Data
df = load_data()

# ======================================================
# DATA PRE-PROCESSING (Before Tabs)
# ======================================================

# --- Process CITY Heatmap ---
city_party_cols = ["party_1", "party_2", "party_3", "party_4"]
city_all_parties = sorted(set(df[city_party_cols].values.flatten().tolist()))

# Filter for mixed votes
city_mixed_df = df[df[city_party_cols].nunique(axis=1) > 1]
city_pair_counter = Counter()

for _, row in city_mixed_df.iterrows():
    parties = sorted(set(row[city_party_cols]))
    for a, b in combinations(parties, 2):
        city_pair_counter[(a, b)] += 1

city_heatmap_df = pd.DataFrame(0, index=city_all_parties, columns=city_all_parties)
for (a, b), c in city_pair_counter.items():
    city_heatmap_df.loc[a, b] = c
    city_heatmap_df.loc[b, a] = c

# --- Process DISTRICT Heatmap ---
district_party_cols = ["district_party_1", "district_party_2"]
district_all_parties = sorted(set(df[district_party_cols].values.flatten().tolist()))

# Filter for mixed votes
district_mixed_df = df[df["district_party_1"] != df["district_party_2"]]
dist_pair_counter = Counter()

for _, row in district_mixed_df.iterrows():
    pair = tuple(sorted([row["district_party_1"], row["district_party_2"]]))
    dist_pair_counter[pair] += 1

district_heatmap_df = pd.DataFrame(0, index=district_all_parties, columns=district_all_parties)
for (a, b), c in dist_pair_counter.items():
    district_heatmap_df.loc[a, b] = c
    district_heatmap_df.loc[b, a] = c

# --- Sync Color Scale ---
# Calculate the max across both dataframes for visual honesty
global_max = max(city_heatmap_df.max().max(), district_heatmap_df.max().max())

# ======================================================
# UI LAYOUT
# ======================================================

tab1, tab2 = st.tabs([
    "Хотын сонгууль – Намын холимог санал өгөлт",
    "Дүүргийн сонгууль – Намын холимог санал өгөлт",
])

with tab1:
    st.markdown("### Хотын сонгууль дахь намын холигдлын хэв шинж")
    
    fig1 = px.imshow(
        city_heatmap_df,
        text_auto=True,
        aspect="auto",
        title="<b>Хотын сонгууль: Нам хоорондийн саналын холигдлын график</b>",
        labels=dict(color="Саналын тоо"),
        color_continuous_scale="Blues",
        zmin=0,
        zmax=global_max
    )
    fig1.update_layout(xaxis_title="Нам", yaxis_title="Нам", margin=dict(t=80))
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Аргачлал:** 4 төлөөлөгч сонгохдоо өөр өөр нам сонгосон хуудсуудыг шүүсэн. 
    Эндээс харахад томоохон намуудын хоорондох 'санал хуваалт' илүү тод ажиглагдаж байна.
    """)

with tab2:
    st.markdown("### Дүүргийн сонгууль дахь намын холигдлын хэв шинж")
    
    fig2 = px.imshow(
        district_heatmap_df,
        text_auto=True,
        aspect="auto",
        title="<b>Дүүргийн сонгууль: Нам хоорондийн саналын холигдлын график</b>",
        labels=dict(color="Саналын тоо"),
        color_continuous_scale="Blues",
        zmin=0,
        zmax=global_max
    )
    fig2.update_layout(xaxis_title="Нам", yaxis_title="Нам", margin=dict(t=80))
    st.plotly_chart(fig2, use_container_width=True)
    st.caption('Өнгөний (scale) нь хотын сонгуультай ижил тул шууд харьцуулах боломжтой.')

    st.markdown("""
    **Аргачлал:** 2 төлөөлөгч нь өөр өөр намынх байсан саналын хуудсуудыг нэгтгэв. 
    
    """)